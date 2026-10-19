"""Deactivates active users whose password hash is empty (spec 002 FR-018).

Before spec 002 D1 every start did this, undoing an administrator who reactivated such a user on
purpose. Now it runs only when the owner asks: `python scripts/repairs/deactivate_users_without_password.py [--apply]`.
"""

from _repair import run

if __name__ == "__main__":
    run("repair_users_without_password", "active users without a password hash", __doc__)
