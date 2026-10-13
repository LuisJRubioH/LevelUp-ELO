"""
src/application/services/katia_service.py
==========================================
KatIA's chat as a use case the server controls (spec 005, block 6).

One reply, in this order:

1. Refusals, with no model call and nothing stored: unknown item, course not enrolled, item of
   an open exam, item never served to the student, message over the limit (FR-019 … FR-025).
2. A serving that used all its turns gets the closing message (FR-034).
3. A message that asks for the answer, proposes an option or tries to change the rules gets a
   reviewed redirect (FR-003 … FR-005); after too many flagged turns, reviewed hints only (FR-016).
4. Otherwise the model receives the store's exercise — with the key only after the server
   recorded an answer to this serving (FR-006 … FR-008) — the latest accepted turns of the
   serving (FR-023) and the message as its own turn (FR-002).
5. Its reply is checked; a revealing one is replaced by a reviewed hint (FR-009 … FR-017), a
   cut-off one keeps its complete sentences (FR-032).
6. The turn is stored with its serving and outcome (FR-037). A model failure stores nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.interfaces.repositories import IKatiaRepository
from src.application.interfaces.tutor import ITutor, TutorUnavailable
from src.domain.katia.guardrails import ItemFacts, inspect_message, inspect_reply, trim_to_sentences
from src.domain.katia.limits import KatiaLimits
from src.domain.katia.reviewed_messages import closing, hint, redirect
from src.domain.katia.tutor_prompt import build_instructions, build_messages, normalize_lang

# Turns whose KatIA text came from the model and passed the checks: the only history the model
# sees, and the only replies that count towards an accumulated solution.
ACCEPTED_OUTCOMES = ("accepted", "truncated")
# Turns that count towards the escalation to reviewed hints (FR-016).
FLAGGED_PREFIXES = ("redirected:", "rejected:")


class KatiaRefused(Exception):
    """The request is refused before any model call. `code` names why (contracts/api.md)."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class KatiaReply:
    text: str
    outcome: str
    serve_id: int
    answered: bool = False


class KatiaService:
    def __init__(self, repository: IKatiaRepository, tutor: ITutor, limits: KatiaLimits = None):
        self.repository = repository
        self.tutor = tutor
        self.limits = limits or KatiaLimits()

    def reply(
        self,
        user_id: int,
        item_id: str,
        message: str,
        lang: str = "es",
        level: float | None = None,
    ) -> KatiaReply:
        lang = normalize_lang(lang)
        item, serve = self._admit(user_id, item_id, message)
        facts = ItemFacts(
            statement=item["content"],
            options=tuple(item["options"]),
            correct_option=item["correct_option"],
        )
        turns = self.repository.get_katia_turns(serve["id"])
        turn = len(turns)

        def store(text: str, outcome: str, answered: bool = False) -> KatiaReply:
            self.repository.save_katia_interaction(
                user_id=user_id,
                course_id=item.get("course_id"),
                item_id=item_id,
                item_topic=item.get("topic"),
                student_message=message,
                katia_response=text,
                serve_id=serve["id"],
                guard_outcome=outcome,
            )
            return KatiaReply(text=text, outcome=outcome, serve_id=serve["id"], answered=answered)

        if turn >= self.limits.max_turns_per_serving:
            return store(closing(lang), "closed")

        flags = inspect_message(message, facts)
        if flags:
            text, reason = redirect(flags, lang, turn)
            return store(text, f"redirected:{reason}")

        flagged = sum(
            1 for t in turns if (t.get("guard_outcome") or "").startswith(FLAGGED_PREFIXES)
        )
        if flagged >= self.limits.max_flagged_turns:
            return store(hint(lang, turn), "restricted")

        answered = self.repository.has_attempt_after(user_id, item_id, serve["attempt_watermark"])
        accepted = [t for t in turns if t.get("guard_outcome") in ACCEPTED_OUTCOMES]
        history = accepted[-self.limits.history_turns :] if self.limits.history_turns else []
        system = build_instructions(
            facts,
            item.get("topic") or "",
            lang,
            level,
            reference=facts.correct_option if answered else None,
        )
        messages = build_messages(
            [(t["student_message"], t["katia_response"]) for t in history], message
        )

        completion = self.tutor.complete(system, messages)
        text = (completion.text or "").strip()
        outcome = "accepted"
        if completion.truncated:
            text = trim_to_sentences(text)
            outcome = "truncated"
            if not text:
                return store(hint(lang, turn), "truncated_empty", answered)
        if not text:
            # An empty reply is a failure of the model, not KatIA speaking (#57).
            raise TutorUnavailable("empty")

        reasons = inspect_reply(text, facts, [t["katia_response"] or "" for t in accepted])
        if reasons:
            return store(hint(lang, turn), "rejected:" + ",".join(reasons), answered)
        return store(text, outcome, answered)

    def _admit(self, user_id: int, item_id: str, message: str):
        """The item and its current serving, or KatiaRefused (FR-019 … FR-021, FR-024, FR-025)."""
        item = self.repository.get_item_by_id(item_id)
        if not item:
            raise KatiaRefused("item_not_found")
        enrolled = {e["id"] for e in self.repository.get_user_enrollments(user_id)}
        if item.get("course_id") not in enrolled:
            raise KatiaRefused("not_enrolled")
        if item_id in set(self.repository.get_open_exam_item_ids(user_id)):
            raise KatiaRefused("exam_active")
        serve = self.repository.get_latest_item_serve(user_id, item_id)
        if not serve:
            raise KatiaRefused("not_served")
        if len(message) > self.limits.max_message_chars:
            raise KatiaRefused("message_too_long")
        return item, serve
