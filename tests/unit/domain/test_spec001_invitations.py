"""
Spec 001, delivery INV — single-use group invitations: the token's alphabet, length and shape, the
normalisation of what a student types, an invitation's state and the order of the refusals
(FR-028p, FR-028q, FR-028r, FR-028s, FR-028t). No I/O.

[CHANGE] tests: the base branch has no single-use invitation.
"""

import itertools

import pytest

from src.domain.invitations import (
    MAX_INVITATIONS_PER_REQUEST,
    TOKEN_ALPHABET,
    TOKEN_LENGTH,
    format_token,
    invitation_status,
    new_token,
    normalise_token,
    redemption_refusal,
    valid_invitation_count,
)


def test_spec001_token_alphabet_has_no_lookalike_characters():
    """FR-028p: upper-case letters and digits without 0, O, 1, I or L — 31 characters."""
    assert TOKEN_ALPHABET == "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    assert len(set(TOKEN_ALPHABET)) == len(TOKEN_ALPHABET) == 31
    assert not set("0O1IL") & set(TOKEN_ALPHABET)
    assert TOKEN_LENGTH == 10


def test_spec001_new_token_is_ten_characters_of_the_alphabet():
    """FR-028p: every token has 10 characters of the alphabet; drawn at random, they differ."""
    tokens = [new_token() for _ in range(500)]
    assert all(len(t) == TOKEN_LENGTH and set(t) <= set(TOKEN_ALPHABET) for t in tokens)
    assert len(set(tokens)) == len(tokens)


def test_spec001_new_token_draws_each_character_with_the_given_choice():
    """FR-028p: the token is drawn character by character (secrets.choice unless one is given)."""
    letters = itertools.cycle("AB")
    assert new_token(choice=lambda alphabet: next(letters)) == "ABABABABAB"


def test_spec001_token_is_shown_in_two_groups_of_five():
    """FR-028p: shown as XXXXX-XXXXX."""
    assert format_token("ABCDEFGHJK") == "ABCDE-FGHJK"


@pytest.mark.parametrize(
    "typed",
    [
        "ABCDEFGHJK",
        "ABCDE-FGHJK",
        "  abcde-fghjk  ",
        "abcde fghjk",
        "AbCdE\tfGhJk",
        "ABCDE–FGHJK",  # an en dash pasted from a chat
        "A-B-C-D-E-F-G-H-J-K",
    ],
)
def test_spec001_redemption_input_is_normalised(typed):
    """FR-028q: letter case, spaces and hyphens are ignored."""
    assert normalise_token(typed) == "ABCDEFGHJK"


@pytest.mark.parametrize("typed", [None, "", "   ", "-"])
def test_spec001_empty_input_normalises_to_nothing(typed):
    assert normalise_token(typed) == ""


@pytest.mark.parametrize(
    "count, ok",
    [(1, True), (MAX_INVITATIONS_PER_REQUEST, True), (0, False), (51, False), (-3, False)],
)
def test_spec001_between_one_and_fifty_invitations_at_once(count, ok):
    """FR-028p: a teacher asks for 1 to 50 invitations at once."""
    assert MAX_INVITATIONS_PER_REQUEST == 50
    assert valid_invitation_count(count) is ok


@pytest.mark.parametrize("count", [True, 2.0, "3", None])
def test_spec001_invitation_count_must_be_a_whole_number(count):
    assert valid_invitation_count(count) is False


@pytest.mark.parametrize(
    "used, revoked, expired, status",
    [
        (False, False, False, "unused"),
        (True, False, False, "used"),
        (True, False, True, "used"),  # used before it expired: it stays used
        (False, True, False, "revoked"),
        (False, True, True, "revoked"),  # revoked before it expired: it stays revoked
        (False, False, True, "expired"),
    ],
)
def test_spec001_invitation_status(used, revoked, expired, status):
    """FR-028t: unused, used, expired or revoked, from what the invitation records."""
    assert invitation_status(used=used, revoked=revoked, expired=expired) == status


_LIVE = dict(
    found=True, used=False, revoked=False, expired=False, has_course=True, already_member=False
)


@pytest.mark.parametrize(
    "change, refusal",
    [
        ({}, None),
        ({"found": False}, "invalid"),
        ({"revoked": True}, "invalid"),
        ({"revoked": True, "expired": True}, "invalid"),
        ({"used": True}, "used"),
        ({"used": True, "expired": True}, "used"),
        ({"expired": True}, "expired"),
        ({"has_course": False}, "no_course"),
        ({"already_member": True}, "already_member"),
        # What the invitation is decides before what the student or the group is.
        ({"used": True, "already_member": True}, "used"),
        ({"expired": True, "has_course": False}, "expired"),
        ({"has_course": False, "already_member": True}, "no_course"),
    ],
)
def test_spec001_redemption_refusal(change, refusal):
    """FR-028q, FR-028r, FR-028s: only a live invitation of a group with a course, for a student
    not already in it, is redeemed; any other case names its refusal."""
    assert redemption_refusal(**{**_LIVE, **change}) == refusal
