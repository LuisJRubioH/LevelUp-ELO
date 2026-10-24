"""Account rules without I/O (spec 004): the password rule, the display name and its filter (E2),
and the last day of access (E3)."""

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone

from src.domain.entities import LEVEL_SEMILLERO, VALID_LEVELS, valid_semillero_grade

PASSWORD_MIN_LENGTH = 6


def valid_new_password(password) -> bool:
    """FR-026: PASSWORD_MIN_LENGTH characters or more after trimming — the account rule today."""
    return isinstance(password, str) and len(password.strip()) >= PASSWORD_MIN_LENGTH


# ── Display name (FR-020 … FR-022, N5, N17) ──────────────────────────────────────────────────────

DISPLAY_NAME_MIN_LENGTH = 2
DISPLAY_NAME_MAX_LENGTH = 80
_SEPARATORS = " -'’"
_TOKEN_SPLIT = re.compile(r"[ \-'’]+")

# Offensive or mocking words in Spanish and English (N17), compared without accents or letter case
# (ñ is kept: «coño» is not «cono»). Whole words only, so a name that merely contains one — Vergara
# — is a name. Words that are also real names or surnames (Dick, Butt, Morón, Cuca) are left out on
# purpose: the admin corrects whatever this list misses (N17).
_REFUSED_WORDS = frozenset(
    """
    puta puto putas putos putita putito putona hijueputa hijoeputa hijodeputa hp
    malparido malparida malparidos gonorrea gonorreas carechimba careverga careculo chimba
    marica marico maricon maricones pendejo pendeja pendejos huevon huevona guevon guevona webon
    cabron cabrona mamaguevo mamahuevo mamon mamona verga vergas pinga polla pene penes vagina
    culo culos culon culona culicagado culiao culiado culear coño joder follar pajero pajera
    mierda mierdas caca popo pedo pedorro teta tetas sexo porno violador violar idiota imbecil
    estupido estupida tonto tonta retrasado mongolico mongolo nazi hitler
    fuck fucker fucking motherfucker shit bitch bitches bastard asshole ass dumbass jackass cunt
    pussy whore slut fag faggot nigger nigga retard penis boobs tits sex porn rape rapist idiot
    stupid dumb loser poop piss wanker twat prick douche dildo cum jizz
    """.split()
)

# Well-known mocking full names, compared with their letters run together.
_REFUSED_PHRASES = (
    "elvergalarga",
    "elvergacorta",
    "rosamelano",
    "analisamelano",
    "doloresdelano",
    "deboramelo",
    "aquilescastro",
    "zoylavaca",
    "mikehunt",
    "hughjass",
    "bendover",
    "mikeoxlong",
    "mikeoxmall",
    "seymourbutz",
    "jennytalia",
    "philmccracken",
    "moelester",
    "amandahugginkiss",
    "hughgrection",
    "ivanatinkle",
    "dixienormous",
    "heywoodjablowme",
)

_REPEATED = re.compile(r"(.)\1+")


def normalize_display_name(name) -> str | None:
    """FR-020: outer spaces removed and inner runs of spaces made one; None when nothing is left."""
    if not isinstance(name, str):
        return None
    name = unicodedata.normalize("NFC", " ".join(name.split()))
    return name or None


def _comparable(text: str) -> str:
    """Lower case without accents; the tilde of ñ stays."""
    decomposed = unicodedata.normalize("NFD", text)
    kept = []
    for ch in decomposed:
        if unicodedata.category(ch) == "Mn" and not (ch == "̃" and kept and kept[-1] in "nN"):
            continue
        kept.append(ch)
    return unicodedata.normalize("NFC", "".join(kept)).casefold()


def _is_refused(name: str) -> bool:
    tokens = [t for t in _TOKEN_SPLIT.split(_comparable(name)) if t]
    joined = "".join(tokens)
    candidates = set(tokens) | {_REPEATED.sub(r"\1", t) for t in tokens}
    candidates |= {joined, _REPEATED.sub(r"\1", joined)}
    if candidates & _REFUSED_WORDS:
        return True
    return any(phrase in joined for phrase in _REFUSED_PHRASES)


def display_name_problem(name) -> str | None:
    """FR-020 (N17): why a normalised `name` cannot be a display name, or None when it can.

    2 to 80 characters of letters of any language, spaces, apostrophes and hyphens, with no
    offensive or mocking word in Spanish or English. The message never repeats the name.
    """
    if name is None:
        return "Escribe tu nombre."
    if not DISPLAY_NAME_MIN_LENGTH <= len(name) <= DISPLAY_NAME_MAX_LENGTH:
        return (
            f"El nombre debe tener entre {DISPLAY_NAME_MIN_LENGTH} y "
            f"{DISPLAY_NAME_MAX_LENGTH} caracteres."
        )
    letters = sum(1 for ch in name if unicodedata.category(ch).startswith("L"))
    allowed = all(unicodedata.category(ch)[0] in "LM" or ch in _SEPARATORS for ch in name)
    if not allowed or letters < DISPLAY_NAME_MIN_LENGTH:
        return "El nombre solo puede tener letras, espacios, apóstrofos y guiones."
    if _is_refused(name):
        return "Ese nombre no está permitido. Escribe tu nombre real."
    return None


def public_name(display_name, username) -> str:
    """FR-021, FR-022 (N5): what other people see — the display name, else the username."""
    return display_name or username


def student_level_problem(education_level, grade) -> str | None:
    """FR-040 (P9): why a level and a grade cannot go together on a new student, or None.

    A level is required; semillero takes a grade from 6.º to 11.º, and every other level takes
    none («No aplica») — a grade is never guessed for it.
    """
    if education_level not in VALID_LEVELS:
        return "Elige el nivel: colegio, universidad, concursos o semillero."
    if education_level == LEVEL_SEMILLERO:
        if not valid_semillero_grade(grade):
            return "Semillero requiere un grado de 6.º a 11.º."
    elif grade not in (None, ""):
        return "El grado solo aplica a semillero; para este nivel elige «No aplica»."
    return None


# ── Last day of access (FR-046 … FR-048, P7) ─────────────────────────────────────────────────────

# Colombia keeps UTC−5 all year, with no daylight saving time.
COLOMBIA = timezone(timedelta(hours=-5), "America/Bogota")

ACCESS_EXPIRED_MESSAGE = (
    "El período de acceso de tu cuenta terminó. Tu progreso está guardado. "
    "Contacta al administrador si necesitas ampliar el acceso."
)


def colombia_today(now_utc: datetime) -> date:
    """FR-046: the calendar day in Colombia at the instant `now_utc` (timezone-aware)."""
    return now_utc.astimezone(COLOMBIA).date()


def parse_last_day(value) -> date | None:
    """FR-046: a last day of access as a calendar date; None or "" means none.

    Accepts a date, a datetime (its date) or an ISO text `YYYY-MM-DD`; anything else raises
    ValueError, so a last day is never guessed from another format.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("El último día de acceso debe ser una fecha AAAA-MM-DD.")
    text = value.strip()
    if not text:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError("El último día de acceso debe ser una fecha AAAA-MM-DD.")
    return date.fromisoformat(text)


def access_expired(last_day, now_utc: datetime) -> bool:
    """FR-047: expired from the start of the day after the last day, Colombian time; an account
    without a last day never expires. `last_day` is read with `parse_last_day`."""
    day = parse_last_day(last_day)
    return day is not None and colombia_today(now_utc) > day
