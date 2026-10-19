"""Deletes the KatIA messages typed before spec 005 K3 (decision N3).

Until K3 every message a student typed to KatIA, and her reply, was kept in `katia_interactions`
with no expiry; no conversation summary can be rebuilt from them (they carry no outcome). The
owner runs this after the switch: `python scripts/repairs/delete_katia_texts.py [--apply]`.
"""

from _repair import run

if __name__ == "__main__":
    run("repair_katia_texts", "KatIA messages typed before K3", __doc__)
