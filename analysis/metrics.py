# ======================================================
# analysis/metrics.py
# ======================================================

def mean_absolute_error(data):
    return sum(abs(d['true'] - d['estimated']) for d in data) / len(data)

