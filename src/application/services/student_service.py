import logging

from src.domain.elo.model import (
    expected_score,
    is_valid_response_time,
    item_difficulty_delta,
    next_rd,
    rating_delta,
)
from src.domain.selector.item_selector import AdaptiveItemSelector
from src.domain.entities import (
    LEVEL_SEMILLERO,
    LEVEL_UNIVERSIDAD,
    VALID_LEVELS,
    valid_semillero_grade,
)
from src.application.interfaces.repositories import IStudentRepository
from src.application.services.rating_read_service import RatingReadService


logger = logging.getLogger(__name__)


class StudentService:
    """
    Servicio de aplicación que orquesta los casos de uso del estudiante.
    """

    def __init__(
        self,
        repository: IStudentRepository,
        ai_client=None,
        calibrator=None,
        ratings=None,
    ):
        """El calibrador se inyecta desde la composición (R2).

        `calibrator` es cualquier objeto con `predict(p_raw) -> float`; vive en
        infrastructure/ml porque carga un pickle de disco. Sin él —tests, o
        despliegue sin modelo entrenado— se usa p_raw, que es exactamente lo
        que hacía el calibrador sin modelo. El delta ELO siempre usa p_raw:
        el valor calibrado solo alimenta los dashboards.
        """
        self.repository = repository
        self.ai_client = ai_client
        self._calibrator = calibrator
        # Every current rating, rank and ranking is read through here (spec 001).
        self.ratings = ratings or RatingReadService(repository)

    def get_next_question(
        self,
        student_id,
        course_id,
        topic_filter=None,
        session_correct_ids=None,
        session_wrong_timestamps=None,
        session_questions_count=0,
        block=None,
    ):
        """Choose the next practice item of `course_id` (FR-016–019).

        `block` narrows the pool to a thematic block (concursos); `topic_filter` to one topic
        (practice from the map) when that topic has items. The selection rating is the topic's
        rating with a filter, otherwise the course rating (spec 001, FR-029a).
        """
        session_correct_ids = session_correct_ids or set()
        session_wrong_timestamps = session_wrong_timestamps or {}

        pool = self.repository.get_items_from_db(course_id=course_id, block=block)
        # Refuerzo desde el mapa: restringir a un tópico del curso.
        # Solo si quedan ítems — evita un pool vacío por un tópico inexistente.
        if topic_filter:
            by_topic = [i for i in pool if i.get("topic") == topic_filter]
            if by_topic:
                pool = by_topic

        answered_ids = set(self.repository.get_answered_item_ids(student_id))
        current_elo = self.ratings.selection_rating(student_id, course_id, topic_filter)

        # Excluir siempre las respondidas correctamente en esta sesión
        eligible = [i for i in pool if i["id"] not in session_correct_ids]

        # Prioridad 1: no vistas (no en DB histórica ni en sesión fallida)
        unseen = [
            i
            for i in eligible
            if i["id"] not in answered_ids and i["id"] not in session_wrong_timestamps
        ]

        # Prioridad 2: falladas en sesión con intervalo ≥ 3 preguntas
        wrong_available = [
            i
            for i in eligible
            if i["id"] in session_wrong_timestamps
            and session_questions_count - session_wrong_timestamps[i["id"]] >= 3
        ]

        # Prioridad 3: históricas no de esta sesión (ni en cooldown)
        historical = [
            i
            for i in eligible
            if i["id"] in answered_ids and i["id"] not in session_wrong_timestamps
        ]

        filtered = unseen or wrong_available or historical

        # Si no hay candidatos, reiniciar o declarar maestría
        if not filtered:
            if current_elo < 1800:
                filtered = eligible or pool
            else:
                return None, "mastery"

        # Seleccionar óptima
        from src.domain.elo.model import Item

        selector = AdaptiveItemSelector()
        items_objs = [Item(difficulty=i["difficulty"]) for i in filtered]
        target_item_obj = selector.select_optimal_item(current_elo, items_objs)

        if target_item_obj:
            # Dos ítems pueden tener la misma dificultad: conservar la identidad
            # sorteada, sin volver a escoger el primero que tenga ese valor.
            item_data = next(
                data for obj, data in zip(items_objs, filtered) if obj is target_item_obj
            )
            return item_data, "ok"
        return None, "empty"

    def process_answer(
        self,
        user_id,
        item_data,
        selected_option,
        reasoning,
        time_taken,
        request_id=None,
        request_fingerprint=None,
    ):
        """Process one practice answer (spec 001, FR-001…FR-010, FR-015, FR-029).

        The rating moved is the item's own (course, topic); the repository reads it under lock
        and calls `compute`. An attempt outside 3–600 s (or an explicit 0 s) is recorded with
        before = after and moves nothing (FR-008, FR-008a, FR-009). Returns
        `(is_correct, result)` with `elo_before`, `elo_after`, `rd_after` and `elo_valid`.
        """
        is_correct = selected_option == item_data["correct_option"]
        score = 1.0 if is_correct else 0.0
        valid = is_valid_response_time(time_taken)
        result = {"confidence_score": None, "error_type": "none"}

        def compute(state):
            """Domain calculation on the state read under lock (no I/O)."""
            rating, rd, difficulty = state["elo"], state["rd"], state["item_difficulty"]
            if valid:
                rating_after = rating + rating_delta(rating, rd, difficulty, score)
                rd_after = next_rd(rd)
                difficulty_after = difficulty + item_difficulty_delta(rating, difficulty, score)
            else:
                rating_after, rd_after, difficulty_after = rating, rd, difficulty

            # The calibrated value only feeds dashboards; the delta always uses the raw P.
            p_success = expected_score(rating, difficulty)
            p_display = self._calibrator.predict(p_success) if self._calibrator else p_success

            result.update(
                elo_before=rating, elo_after=rating_after, rd_after=rd_after, elo_valid=valid
            )
            attempt_data = {
                "is_correct": is_correct,
                "difficulty": difficulty,
                "topic": state.get("topic", item_data.get("topic")),
                "elo_before": rating,
                "elo_after": rating_after,
                "rating_deviation": rd_after,
                "elo_valid": valid,
                "prob_failure": 1.0 - p_display,
                "expected_score": p_display,
                "time_taken": time_taken,
                "confidence_score": result["confidence_score"],
                "error_type": result["error_type"],
            }
            return attempt_data, difficulty_after, state["item_rd"]

        save_kwargs = dict(user_id=user_id, item_id=item_data["id"], compute=compute)
        if request_id is not None:
            save_kwargs.update(request_id=request_id, request_fingerprint=request_fingerprint)
        if self.repository.save_answer_transaction(**save_kwargs) is False:
            result["idempotent_replay"] = True
            return is_correct, result

        # Achievements never block the answer, but a failure is logged (FR-015).
        try:
            new_badges = self._check_and_award_achievements(
                user_id=user_id, is_correct=is_correct, new_elo=result["elo_after"]
            )
            if new_badges:
                result["new_badges"] = new_badges
        except Exception:
            logger.exception("Awarding achievements failed for user %s", user_id)

        return is_correct, result

    # ── CATÁLOGO DE BADGES ────────────────────────────────────────────────────
    # Definición: (badge_id, label, descripción, check_fn(user_id, is_correct, new_elo, repo))

    _BADGE_CATALOG = [
        {
            "badge_id": "first_correct",
            "label": "Primera respuesta correcta",
            "icon": "⭐",
            "desc": "Respondiste correctamente tu primera pregunta",
        },
        {
            "badge_id": "elo_1000",
            "label": "ELO 1000",
            "icon": "🥈",
            "desc": "Alcanzaste ELO 1000 en un tópico",
        },
        {
            "badge_id": "elo_1500",
            "label": "ELO 1500",
            "icon": "🥇",
            "desc": "Alcanzaste ELO 1500 en un tópico",
        },
        {
            "badge_id": "elo_2000",
            "label": "ELO 2000",
            "icon": "🏆",
            "desc": "Alcanzaste ELO 2000 en un tópico — Maestro",
        },
        {
            "badge_id": "streak_5",
            "label": "Racha de 5 días",
            "icon": "🔥",
            "desc": "Estudiaste 5 días seguidos",
        },
        {
            "badge_id": "streak_10",
            "label": "Racha de 10 días",
            "icon": "🔥🔥",
            "desc": "Estudiaste 10 días seguidos",
        },
        {
            "badge_id": "attempts_100",
            "label": "100 respuestas",
            "icon": "💯",
            "desc": "Respondiste 100 preguntas en total",
        },
        {
            "badge_id": "attempts_500",
            "label": "500 respuestas",
            "icon": "🚀",
            "desc": "Respondiste 500 preguntas en total",
        },
    ]

    def _check_and_award_achievements(
        self, user_id: int, is_correct: bool, new_elo: float
    ) -> list[dict]:
        """Verifica qué badges debe recibir el usuario y los otorga si aplica.

        Retorna la lista de badges recién desbloqueados (vacía si ninguno nuevo).
        """
        repo = self.repository
        awarded_now = []

        # ─ first_correct
        if is_correct:
            if repo.award_achievement(user_id, "first_correct"):
                awarded_now.append("first_correct")

        # ─ ELO thresholds (basado en el ELO de este tópico)
        for threshold, badge_id in [(2000, "elo_2000"), (1500, "elo_1500"), (1000, "elo_1000")]:
            if new_elo >= threshold:
                if repo.award_achievement(user_id, badge_id):
                    awarded_now.append(badge_id)
                break  # Solo otorgar el más alto nuevo

        # ─ Rachas
        streak = repo.get_study_streak(user_id)
        for days, badge_id in [(10, "streak_10"), (5, "streak_5")]:
            if streak >= days:
                if repo.award_achievement(user_id, badge_id):
                    awarded_now.append(badge_id)
                break  # Solo otorgar el más alto nuevo

        # ─ Total de intentos
        total = repo.get_total_attempts_count(user_id)
        for count, badge_id in [(500, "attempts_500"), (100, "attempts_100")]:
            if total >= count:
                if repo.award_achievement(user_id, badge_id):
                    awarded_now.append(badge_id)
                break  # Solo otorgar el más alto nuevo

        # Mapear badge_ids a info completa
        catalog_map = {b["badge_id"]: b for b in self._BADGE_CATALOG}
        return [catalog_map[bid] for bid in awarded_now if bid in catalog_map]

    def get_groups_for_course(self, course_id: str) -> list:
        """Devuelve los grupos disponibles para inscribirse en un curso específico."""
        return self.repository.get_available_groups_for_course(course_id)

    def enroll_from_catalogue(self, user_id: int, course_id: str) -> None:
        """Enrol only in a course of the student's catalogue (spec 001 FR-028m).

        Raises PermissionError for any other course. It joins no group: groups, and courses
        outside the catalogue, are reached through `enroll_by_invitation` and its code.
        """
        if course_id not in {c["id"] for c in self.get_available_courses(user_id)}:
            raise PermissionError("The course is not in the student's catalogue.")
        self.repository.enroll_user(user_id, course_id)

    def enroll_by_invitation(self, user_id: int, group_id: int, course_id: str) -> None:
        """Enrol in an invitation group's course, at any level (spec 001 FR-028l).

        A semillero student needs a grade first (PermissionError otherwise). Neither the level
        nor the grade changes, and the course does not join the catalogue: it is accessible
        but never current for the overall rating.
        """
        level = (self.repository.get_education_level(user_id) or "").lower()
        if level == LEVEL_SEMILLERO and not valid_semillero_grade(
            self.repository.get_grade(user_id)
        ):
            raise PermissionError("A semillero student needs a grade to use an invitation.")
        self.repository.enroll_user(user_id, course_id, group_id)

    def ensure_enrolled(self, user_id: int, course_id: str) -> None:
        """Practice, answers and diagnostics only in an enrolled course (spec 001 FR-037, FR-037a).

        An enrolment from the student's level and one made through an invitation are both rows
        of the student's enrolments, so both pass. Raises PermissionError otherwise, including
        for a course that does not exist.
        """
        enrolled = {e["id"] for e in self.repository.get_user_enrollments(user_id)}
        if course_id not in enrolled:
            raise PermissionError("The student is not enrolled in that course.")

    def get_available_courses(self, user_id: int) -> list:
        """Devuelve los cursos disponibles para el nivel educativo del estudiante.

        El nivel se lee desde la base de datos (fuente de verdad), nunca
        desde la sesión, garantizando el filtro estricto de catálogo.
        Un estudiante de Colegio NUNCA recibe cursos de Universidad y viceversa.
        """
        level = self.repository.get_education_level(user_id) or LEVEL_UNIVERSIDAD
        if level.lower() not in VALID_LEVELS:
            level = LEVEL_UNIVERSIDAD
        grade = None
        if level == LEVEL_SEMILLERO:
            grade = self.repository.get_grade(user_id)
        return self.repository.get_available_courses_by_level(level, grade=grade)
