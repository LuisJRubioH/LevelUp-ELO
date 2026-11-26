"""
Spec 006 AB2 (FR-063): the AI's proposal for a submission's open answers.

After the submission is answered (a background task), one provider call per non-empty answer asks
for a level 0–3 on each of the rubric's four criteria. The call carries the statement, the
reference solution, the answer and its code — never a name, username or identification. The AI
only proposes: the teacher decides (FR-064). It uses the teacher-analysis function's key or the
general key, never a student's own (R7); with none, or when a reply cannot be read, the answer
waits for the teacher with that state.
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

FUNCTION = "teacher_analysis"


def propose_for_session(repo, session_id: str) -> None:
    """Records a proposal, or why there is none, for each pending answer of the session. Never
    raises: an answer whose proposal fails keeps waiting for the teacher."""
    from api.ai_target import ai_target
    from api.config import settings
    from src.infrastructure.external_api.ai_client import _call_ai_api

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
        if key:
            try:
                target = ai_target(FUNCTION, key)
                reply = _call_ai_api(
                    rubric_prompt(
                        answer_code(answer["id"]),
                        answer["statement"],
                        answer["reference_solution"],
                        answer["answer_text"],
                    ),
                    target.model,
                    target.base_url,
                    api_key=target.api_key,
                    provider=target.provider,
                    timeout=target.timeout,
                    max_tokens=300,
                )
                parsed = parse_rubric(reply)
            except Exception:
                logger.warning("Open answers: the provider call failed")
                parsed = None
            if parsed is None:
                status = FAILED
            else:
                status, (levels, comment) = PROPOSED, parsed
        try:
            repo.set_open_answer_proposal(answer["id"], status, levels, comment)
        except Exception:
            logger.exception("Open answers: recording a proposal failed")
