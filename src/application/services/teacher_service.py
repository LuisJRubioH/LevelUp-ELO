from src.infrastructure.external_api.ai_client import get_pedagogical_analysis

class TeacherService:
    """
    Servicio de aplicación que orquesta los casos de uso del profesor.
    """
    def __init__(self, repository):
        self.repository = repository

    def get_dashboard_data(self, teacher_id):
        """Recupera datos consolidados para el dashboard del profesor."""
        students = self.repository.get_students_by_teacher(teacher_id)
        groups = self.repository.get_groups_by_teacher(teacher_id)
        return students, groups

    def create_new_group(self, teacher_id: int, course_id: str, group_name: str) -> tuple:
        """Valida y crea un nuevo grupo vinculado a un curso del catálogo.

        Returns (True, mensaje_ok) o (False, mensaje_error).
        """
        group_name = group_name.strip() if group_name else ""
        if not group_name:
            return False, "El nombre del grupo no puede estar vacío."
        if not course_id:
            return False, "Debes seleccionar un curso."
        return self.repository.create_group(group_name, teacher_id, course_id)

    def get_teacher_groups(self, teacher_id: int) -> list:
        """Devuelve los grupos del profesor con información del curso asociado."""
        return self.repository.get_groups_by_teacher(teacher_id)

    def get_student_report(self, student_id):
        """Genera un reporte detallado de un estudiante."""
        attempts = self.repository.get_student_attempts_detail(student_id)
        # Aquí se podrían añadir cálculos adicionales de dominio
        return attempts

    def get_student_dashboard(self, student_id):
        """Datos consolidados para el panel de detalle del estudiante seleccionado.
        Retorna dict con: elo_summary, procedure_stats_by_course, attempts.
        """
        return {
            'elo_summary': self.repository.get_student_elo_summary(student_id),
            'procedure_stats_by_course': self.repository.get_procedure_stats_by_course(student_id),
            'attempts': self.repository.get_student_attempts_detail(student_id),
        }

    def validate_procedure(self, submission_id: int,
                           teacher_score: float, feedback: str = "") -> None:
        """Valida la calificación de un procedimiento y persiste la nota final oficial.

        teacher_score (0.0-100.0) se copia a final_score; el status pasa a
        VALIDATED_BY_TEACHER. Desde ese momento, solo final_score puede usarse
        en analytics y ELO (nunca ai_proposed_score).
        """
        if not (0.0 <= teacher_score <= 100.0):
            raise ValueError(
                f"teacher_score fuera de rango: {teacher_score}. Debe estar entre 0.0 y 100.0."
            )
        self.repository.validate_procedure_submission(submission_id, teacher_score, feedback)

    def generate_ai_analysis(self, student_id, global_elo, api_key=None, provider=None,
                             base_url=None, model_name=None,
                             procedure_stats=None, procedure_stats_by_course=None):
        """Orquesta la generación del análisis pedagógico con IA.
        Requiere un mínimo de 3 intentos para producir un análisis significativo.
        """
        attempts = self.repository.get_student_attempts_detail(student_id)
        if len(attempts) < 3:
            return (
                "ℹ️ El estudiante necesita completar al menos **3 ejercicios** para generar "
                "un análisis pedagógico significativo."
            )

        recent_attempts = attempts[-10:]
        recent_acc = sum(1 for a in recent_attempts if a['is_correct']) / len(recent_attempts) if recent_attempts else 0
        topics_unique = list(set([a['topic'] for a in attempts]))

        # T11: ELO desglosado por tópico para análisis pedagógico más preciso
        elo_by_topic = self.repository.get_latest_elo_by_topic(student_id)
        elo_topic_summary = {t: round(e, 1) for t, (e, _rd) in elo_by_topic.items()} if elo_by_topic else {}

        # T11: tiempo promedio de respuesta (solo intentos con time_taken registrado)
        _times = [a.get('time_taken') for a in attempts if a.get('time_taken') and a['time_taken'] > 0]
        avg_time = round(sum(_times) / len(_times), 1) if _times else None

        student_data = {
            "elo_global": global_elo,
            "attempts_count": len(attempts),
            "topics": topics_unique,
            "recent_accuracy": recent_acc,
            "elo_by_topic": elo_topic_summary,
            "avg_response_time": avg_time,
        }

        kwargs = dict(
            api_key=api_key,
            provider=provider,
            procedure_stats=procedure_stats,
            procedure_stats_by_course=procedure_stats_by_course,
        )
        if base_url:
            kwargs['base_url'] = base_url
        if model_name:
            kwargs['model_name'] = model_name

        return get_pedagogical_analysis(student_data, **kwargs)
