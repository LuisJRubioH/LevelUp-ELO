"""
src/application/interfaces/tutor.py
====================================
What KatIA's use case needs from a language model (spec 005, research R7).

The infrastructure implements it (`src/infrastructure/external_api/katia_tutor.py`); the API
composes it; tests replace it with a fake that records what the model would receive.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class TutorCompletion:
    """The model's reply; `truncated` when the output limit cut it (FR-032)."""

    text: str
    truncated: bool = False
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class TutorUnavailable(Exception):
    """The model could not answer. `code` is safe to log: never the provider's error text."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@runtime_checkable
class ITutor(Protocol):
    def complete(self, system: str, messages: list) -> TutorCompletion: ...
