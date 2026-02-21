# ======================================================
# elo/zdp.py
# ======================================================

def zdp_interval(rating: float, delta: float):
    return rating - delta, rating + delta
