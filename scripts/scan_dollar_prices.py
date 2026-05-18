"""
Escanea items/bank/ buscando pares $...$ donde el contenido es prosa
en español (no expresión matemática). Patrón típico: precios como
"$10.000" que abren math mode y rompen el render hasta otro "$".
"""

import json
import re
import glob
import sys

PAIR = re.compile(r"(?<!\\)\$([^$\n]{1,500})\$")
LATEX_CMD = re.compile(r"\\[a-zA-Z]+")

# Phrases multi-palabra que solo aparecen en prosa, nunca en matemáticas
PROSE_PHRASES = re.compile(
    r"\b(cada \w+|por \w+|de \w+|y \w{4,}|que \w+|los \w+|las \w+|"
    r"para \w+|con \w+|sin \w+|cuesta\w*|compr\w+|pag[óaa]?|"
    r"tien[ea]n?|cuántos?|cu[aá]nto|libros?|cuentos?|amig[oa]s?|"
    r"persona\w*|porque|también|todo[s]?|misma?o?s?)\b",
    re.IGNORECASE,
)


def is_prose(s: str) -> bool:
    has_latex = bool(LATEX_CMD.search(s))
    has_prose = bool(PROSE_PHRASES.search(s))
    return has_prose and not has_latex


def main() -> int:
    hits = []
    for f in glob.glob("items/bank/**/*.json", recursive=True):
        data = json.load(open(f, encoding="utf8"))
        if not isinstance(data, list):
            continue
        for item in data:
            content = item.get("content", "")
            # Show the FULL surrounding context for each hit
            for m in PAIR.finditer(content):
                inner = m.group(1)
                if is_prose(inner):
                    hits.append((f, item["id"], inner, content))
                    break

    print(f"{len(hits)} ítems sospechosos:")
    for f, iid, inner, content in hits:
        print(f"  {f}  {iid}")
        print(f"    inner ({len(inner)}c): {inner[:140]}")
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
