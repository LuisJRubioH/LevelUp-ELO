"""The part of a rehearsal report that may go into a PUBLIC log or artifact.

The repository is public, so its Actions logs and artifacts are readable by anyone. When a
rehearsal step fails, `scripts/rehearse_migration.py` writes the raw output of the failing command
into its report, and PostgreSQL quotes row data in its errors: `DETAIL: Key (email)=(…) is
duplicated`, `Failing row contains (…)`. This keeps only what the script itself formats (section
headers, check labels, counts, the result) and drops anything that can quote a row. The full output
stays in the encrypted backup.

Usage: public_rehearsal_summary.py FULL_OUTPUT > PUBLIC_SUMMARY
"""

import re
import sys

_CHECK = re.compile(r"^  \[(PASS|FAIL)\] (.*)$")
# Text that can quote data: PostgreSQL details, quoted values, e-mail addresses, errors.
_UNSAFE = re.compile(r'["@]|Key \(|Failing row|DETAIL|error|Traceback', re.IGNORECASE)
_HIDDEN = "(details in the encrypted backup)"


def public_lines(lines):
    kept, omitted = [], 0
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("== ") or line.startswith("RESULT: ") or not line:
            kept.append(line)
            continue
        check = _CHECK.match(line)
        if check:
            # Labels are the script's fixed text; only the detail after " — " carries output.
            label, _, detail = check.group(2).partition(" — ")
            if detail and (_UNSAFE.search(detail) or len(detail) > 160):
                detail = _HIDDEN
            kept.append(f"  [{check.group(1)}] {label}" + (f" — {detail}" if detail else ""))
            continue
        # The script's own information lines: two spaces, then text that cannot quote a row.
        if re.match(r"^  [a-z0-9\[]", line) and not _UNSAFE.search(line) and len(line) <= 200:
            kept.append(line)
            continue
        omitted += 1
    if omitted:
        kept.append(f"({omitted} lines of raw command output omitted here; {_HIDDEN[1:-1]})")
    return kept


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        print("\n".join(public_lines(fh)))
