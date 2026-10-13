"""
KatIA's consumption limits (spec 005 FR-016, FR-023, FR-024, FR-031, FR-034; research R11).

The single definition of the Socratic output limit: V1's model router, the API settings and the
KatIA service read it from here.
"""

from dataclasses import dataclass

# The documented Socratic output limit (block 6 point 7). Changing it needs pedagogical examples
# and the owner's explicit agreement.
SOCRATIC_MAX_TOKENS = 120


@dataclass(frozen=True)
class KatiaLimits:
    """Defaults recommended in spec 005 (K2); each one is configurable in `api/config.py`."""

    max_output_tokens: int = SOCRATIC_MAX_TOKENS
    max_message_chars: int = 500
    history_turns: int = 4
    max_turns_per_serving: int = 12
    max_flagged_turns: int = 3
