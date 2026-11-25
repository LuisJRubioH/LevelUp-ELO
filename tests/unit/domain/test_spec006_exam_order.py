"""Spec 006 AL (FR-028): the order of a template's items and options, as a pure rule."""

import random

from src.domain.exams.order import item_order, option_order, refers_to_the_others

OPTIONS = ["2", "4", "6", "8", "10"]


def test_options_are_a_permutation_fixed_by_session_and_item():
    """FR-028: every option, once; the same session and item give the same order."""
    first = option_order(OPTIONS, "s1", "item-1")
    assert sorted(first) == sorted(OPTIONS)
    assert option_order(OPTIONS, "s1", "item-1") == first


def test_options_differ_between_sessions():
    """FR-028: other sessions draw other orders."""
    orders = {tuple(option_order(OPTIONS, f"s{n}", "item-1")) for n in range(40)}
    assert len(orders) > 10


def test_an_option_that_refers_to_the_others_stays_last():
    """FR-028: «Ninguna de las anteriores» keeps its place at the end, in every session."""
    options = ["Ninguna de las anteriores", "3", "5", "7"]
    for n in range(30):
        assert option_order(options, f"s{n}", "item-1")[-1] == "Ninguna de las anteriores"


def test_what_refers_to_the_others():
    assert refers_to_the_others("Ninguna de las anteriores")
    assert refers_to_the_others("todos los anteriores")
    assert refers_to_the_others("Ninguno de los anteriores.")
    assert not refers_to_the_others("Aplicar la ley anterior, porque la ley nueva no aplica")
    assert not refers_to_the_others("Exponenciales en ambas variables")


def test_item_order_is_a_new_permutation():
    """FR-028: all the items, in a drawn order; the given list is not changed."""
    ids = [f"i{n}" for n in range(8)]
    order = item_order(ids, random.Random(7))
    assert sorted(order) == sorted(ids)
    assert ids == [f"i{n}" for n in range(8)]
    assert len({tuple(item_order(ids, random.Random(n))) for n in range(20)}) > 10
