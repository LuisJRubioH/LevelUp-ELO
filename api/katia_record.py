"""
Spec 005 K3: the kind of difficulty of a closed KatIA conversation (FR-031, N2).

A conversation closes in the repository, which deletes its text in the same transaction and hands
it back once. Here, after the response is sent (a background task), one provider call reads that
text and picks one label of N2's fixed list; anything else, a failure or no system key leaves
«sin clasificar». The text lives only in this call's memory. The student's own key never outlives
their request (R7), so the classification uses the function's or the general key.
"""

import logging

from src.domain.katia.conversation import UNCLASSIFIED, classification_prompt, parse_difficulty

logger = logging.getLogger("api.katia")


def classify_closed(repo, closed: list) -> None:
    """Records the difficulty of each conversation in `closed` ([{"id", "messages"}]). Never
    raises: a conversation that cannot be classified keeps «sin clasificar»."""
    from api.ai_target import ai_target
    from api.config import settings
    from src.infrastructure.external_api.ai_client import _call_ai_api

    key = settings.get_ai_key("katia", "")
    for conversation in closed or []:
        if not key or not conversation["messages"]:
            continue
        try:
            target = ai_target("katia", key)
            reply = _call_ai_api(
                classification_prompt(conversation["messages"]),
                target.model,
                target.base_url,
                api_key=target.api_key,
                provider=target.provider,
                timeout=target.timeout,
                max_tokens=10,
            )
            label = parse_difficulty(reply)
        except Exception:
            logger.warning("KatIA: classifying a conversation failed")
            label = UNCLASSIFIED
        if label != UNCLASSIFIED:
            try:
                repo.set_katia_difficulty(conversation["id"], label)
            except Exception:
                logger.exception("KatIA: recording a difficulty failed")
