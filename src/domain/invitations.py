"""Single-use group invitations without I/O (spec 001, delivery INV; FR-028p … FR-028t).

A teacher generates invitations for their own group; the first student who redeems one consumes
it. This module holds the token's alphabet, length and shape, the normalisation of what a student
types, an invitation's state and the order of the refusals. Persistence and its locking live in
the repositories; the expiry period is a server setting (`INVITATION_TTL_DAYS`).
"""

import secrets

# Upper-case letters and digits without the look-alikes 0, O, 1, I and L.
TOKEN_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
TOKEN_LENGTH = 10
MAX_INVITATIONS_PER_REQUEST = 50

# An invitation's state (FR-028t).
UNUSED = "unused"
USED = "used"
EXPIRED = "expired"
REVOKED = "revoked"

# A redemption's outcome (FR-028q … FR-028s): REDEEMED consumes the invitation, nothing else does.
REDEEMED = "ok"
INVALID = "invalid"
NO_COURSE = "no_course"
ALREADY_MEMBER = "already_member"

_IGNORED = frozenset("-‐‑‒–—")  # hyphens and the dashes chat apps turn them into


def new_token(choice=secrets.choice) -> str:
    """A fresh token: TOKEN_LENGTH characters of TOKEN_ALPHABET, each drawn by `choice`."""
    return "".join(choice(TOKEN_ALPHABET) for _ in range(TOKEN_LENGTH))


def format_token(token: str) -> str:
    """How a token is shown: two groups of five, XXXXX-XXXXX."""
    half = TOKEN_LENGTH // 2
    return f"{token[:half]}-{token[half:]}"


def normalise_token(text) -> str:
    """What a student typed, as stored: upper case, without spaces or hyphens."""
    if not isinstance(text, str):
        return ""
    return "".join(ch for ch in text.upper() if not ch.isspace() and ch not in _IGNORED)


def valid_invitation_count(count) -> bool:
    """A teacher asks for 1 to MAX_INVITATIONS_PER_REQUEST invitations at once."""
    return (
        isinstance(count, int)
        and not isinstance(count, bool)
        and 1 <= count <= MAX_INVITATIONS_PER_REQUEST
    )


def invitation_status(*, used: bool, revoked: bool, expired: bool) -> str:
    """Used or revoked stays so; otherwise expired once past its expiry; otherwise unused."""
    if used:
        return USED
    if revoked:
        return REVOKED
    if expired:
        return EXPIRED
    return UNUSED


def redemption_refusal(
    *,
    found: bool,
    used: bool,
    revoked: bool,
    expired: bool,
    has_course: bool,
    already_member: bool,
):
    """Why an invitation cannot be redeemed now, or None when it can (FR-028q … FR-028s).

    What the invitation is decides first — unknown or revoked, used, expired — then whether its
    group has a course to open, then whether the student is already in it.
    """
    if not found or revoked:
        return INVALID
    if used:
        return USED
    if expired:
        return EXPIRED
    if not has_course:
        return NO_COURSE
    if already_member:
        return ALREADY_MEMBER
    return None
