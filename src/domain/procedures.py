"""
src/domain/procedures.py
========================
What an uploaded procedure file is (spec 001 block 7, FR-024i … FR-024k). Pure, no I/O.

A file is identified by its SHA-256. The repositories look up two facts under lock — the item
the student already uploaded this file for, if any, and the first student who uploaded it — and
this module decides.
"""

ACCEPT = "accept"
COPY = "copy"
REFUSE_SAME_ITEM = "refuse_same_item"
REFUSE_OTHER_ITEM = "refuse_other_item"

REFUSED = (REFUSE_SAME_ITEM, REFUSE_OTHER_ITEM)


def classify_upload(
    student_id: int,
    item_id: str,
    own_upload_item: str | None,
    first_owner: int | None,
) -> str:
    """The outcome of a student uploading a file for an item.

    1. The student already uploaded this file — for this item → refused (FR-024k); for another
       item → refused (FR-024j). Nothing changes, so a copy already recorded is never a second 0.
    2. Otherwise, another student uploaded it first, for any item → a copy, graded 0 (FR-024i).
    3. Otherwise → accepted.
    """
    if own_upload_item is not None:
        return REFUSE_SAME_ITEM if own_upload_item == item_id else REFUSE_OTHER_ITEM
    if first_owner is not None and first_owner != student_id:
        return COPY
    return ACCEPT
