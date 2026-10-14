"""Account rules without I/O (spec 004 E2): the password rule."""

PASSWORD_MIN_LENGTH = 6


def valid_new_password(password) -> bool:
    """FR-026: PASSWORD_MIN_LENGTH characters or more after trimming — the account rule today."""
    return isinstance(password, str) and len(password.strip()) >= PASSWORD_MIN_LENGTH
