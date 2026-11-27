"""
Spec 006 AB2 (FR-064): the AI's proposal for a submission's procedure photos.

After the submission is answered (a background task), one call to Groq's vision model per
procedure answer with a photo asks for a level 0–3 on each of the rubric's four criteria. The call
carries the photo, the statement, the reference solution and the answer's code — never a name,
username or identification. Short answers are graded on submission and never reach the AI. The AI
only proposes: the teacher decides (FR-065). It uses the procedure function's key or the general
key, never a student's own (R7); vision is Groq's (spec 005 FR-014), so with no Groq key, a
failure or an unreadable reply the answer waits for the teacher with that state.
"""

import logging

from src.domain.exams.open_answers import (
    FAILED,
    NO_KEY,
    PENDING,
    PROPOSED,
    answer_code,
    parse_rubric,
    rubric_prompt,
)

logger = logging.getLogger("api.open_answers")

FUNCTION = "procedure"


def propose_for_session(repo, session_id: str) -> None:
    """Records a proposal, or why there is none, for each pending procedure answer of the
    session. Never raises: an answer whose proposal fails keeps waiting for the teacher."""
    from api.ai_target import ai_target
    from api.config import settings
    from src.infrastructure.external_api.math_procedure_review import rubric_from_image

    key = settings.get_ai_key(FUNCTION, "")
    try:
        answers = repo.get_session_open_answers(session_id)
    except Exception:
        logger.exception("Open answers: reading a session failed")
        return
    for answer in answers:
        if answer["ai_status"] != PENDING:
            continue
        status, levels, comment = NO_KEY, None, None
        target = None
        if key:
            try:
                target = ai_target(FUNCTION, key)
            except Exception:
                target = None
        if target is not None and target.provider == "groq" and answer["image"]:
            try:
                reply = rubric_from_image(
                    answer["image"],
                    answer["mime_type"] or "image/jpeg",
                    target.api_key,
                    rubric_prompt(
                        answer_code(answer["id"]), answer["statement"], answer["reference_solution"]
                    ),
                    model=target.model,
                    timeout=target.timeout,
                )
                parsed = parse_rubric(reply)
            except Exception:
                logger.warning("Open answers: the vision call failed")
                parsed = None
            if parsed is None:
                status = FAILED
            else:
                status, (levels, comment) = PROPOSED, parsed
        elif target is not None and not answer["image"]:
            status = FAILED
        try:
            repo.set_open_answer_proposal(answer["id"], status, levels, comment)
        except Exception:
            logger.exception("Open answers: recording a proposal failed")
