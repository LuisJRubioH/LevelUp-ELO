# Plan — spec 006, delivery AL: a template in an order of its own

**Spec**: [spec.md](spec.md) § Deliveries, AL (US7-AS1 … US7-AS4; FR-028) · **Branch**:
`claude/dazzling-mendel-uta2jw` · **Date**: 2026-11-25 · **Status**: for the owner's approval
(Clarifications, session 2026-11-25: every template; an option that refers to the others last)

## Summary

`POST /exam/start` served a template's items in the order the teacher saved them, and every
item's options as the bank has them. The 2027 municipal olympiad's rules promise questions and
options in random order: two students taking the same phase should not find the same question in
the same place with the right answer under the same letter.

## Constitution Check (1.2.0)

| Principle | AL |
|---|---|
| Layers (R2) | the order rule is pure domain (`src/domain/exams/order.py`); the router only applies it |
| No schema change | the item order is already stored per session (`active_exam_sessions.item_ids`); the option order comes from a seed, so nothing new is stored |
| Dual database (R1) | no repository changes |
| Tests first (VII) | US7-AS1's tests fail on the unchanged code; US7-AS2 … AS4 pin what must not change |
| Secrets (V2-R9) | no correct option is added; grading still compares the chosen text on the server |

## Design

- **Items.** For a template, the router draws the order with `item_order(ids, SystemRandom())`
  after reading the template's items and before storing the session, so `item_ids` holds the
  session's order. FR-002 already compares a submission with that stored list, and FR-025 resumes
  from it.
- **Options.** `option_order(options, session_id, item_id)` shuffles with a `random.Random` seeded
  by the session and the item: the same order every time that session shows the item, a new one
  for another session, with nothing stored. Options matching «Ninguna/Ninguno/Todas/Todos (de)
  las/los (opciones) anteriores» stay last, in their own order.
- **Grading** is unchanged: the server compares the chosen option's text with the correct one.
- **Standard exams** are unchanged: their 30/40/30 curve orders the items from easy to hard.

## Out of scope

- A per-template switch to keep the teacher's order (it needs a column; nobody asked for it).
- Options whose meaning depends on a letter («A y B son correctas»): none in the bank today; the
  bank's validator could refuse them if they appear.
