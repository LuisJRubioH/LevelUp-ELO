"""
scripts/verify_deployment.py — end-to-end checks of a deployment with the test accounts.

docs/transfer.md § 6 ("after the switch") as one command. It writes through the test accounts
only: a diagnostic, one practice answer and one procedure (uploaded, then graded by the teacher).

    python scripts/verify_deployment.py --api-url https://levelup-elo.onrender.com \\
        --frontend-url https://luislevelupelo.vercel.app --report verify-YYYYMMDD.txt

Accounts default to the seeded test users documented in AGENTS.md; override with
VERIFY_STUDENT, VERIFY_DIAGNOSTIC_STUDENT and VERIFY_TEACHER as "user:password".
The practice/procedure student must belong to a group of the teacher.
Exit code 0 only if every check passes (warnings do not fail).
"""

import argparse
import os
import random
import struct
import sys
import time
import zlib

import httpx

LESSON_COURSE = "algebra_basica"
IMAGE_TYPES = ("image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml")


class Run:
    def __init__(self):
        self.failures, self.warnings, self.lines = [], [], []

    def log(self, msg=""):
        print(msg, flush=True)
        self.lines.append(msg)

    def check(self, ok, label, detail=""):
        self.log(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' — ' + str(detail)) if detail else ''}")
        if not ok:
            self.failures.append(label)
        return ok

    def warn(self, label, detail=""):
        self.log(f"  [WARN] {label}{(' — ' + str(detail)) if detail else ''}")
        self.warnings.append(label)


def _account(var, default):
    user, _, password = os.environ.get(var, default).partition(":")
    return user, password


def _png(seed: int) -> bytes:
    """A small, unique PNG (the API rejects a file whose hash it has already seen)."""
    rng = random.Random(seed)
    width = height = 32
    raw = b"".join(
        b"\x00" + bytes(rng.randrange(256) for _ in range(width * 3)) for _ in range(height)
    )

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _images(value, found):
    """Every lesson image path ('/leccion/...', '/katia/...') inside a lesson payload."""
    if isinstance(value, dict):
        for v in value.values():
            _images(v, found)
    elif isinstance(value, list):
        for v in value:
            _images(v, found)
    elif (
        isinstance(value, str)
        and value.startswith("/")
        and value.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"))
    ):
        found.add(value)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--api-url", required=True)
    ap.add_argument("--frontend-url", required=True)
    ap.add_argument("--wait", type=int, default=180, help="seconds to wait for a cold start")
    ap.add_argument("--report")
    args = ap.parse_args()
    api, front = args.api_url.rstrip("/"), args.frontend_url.rstrip("/")
    origin = front
    r = Run()
    c = httpx.Client(base_url=api, timeout=90)

    r.log(f"== API {api} · frontend {front}")
    r.log("== 1. Health and public data")
    deadline, health = time.monotonic() + args.wait, None
    while True:
        try:
            health = c.get("/api/health")
            if health.status_code == 200:
                break
        except httpx.HTTPError:
            pass
        if time.monotonic() > deadline:
            break
        time.sleep(10)
    r.check(
        health is not None and health.status_code == 200,
        "GET /api/health → 200",
        health.text[:200] if health is not None else "no answer",
    )
    ranks = c.get("/api/meta/ranks")
    body = ranks.json() if ranks.status_code == 200 else []
    body = body.get("ranks", body) if isinstance(body, dict) else body
    r.check(
        ranks.status_code == 200 and len(body) == 16,
        "GET /api/meta/ranks → 16 ranks",
        f"{ranks.status_code}, {len(body)}",
    )
    pre = c.options(
        "/api/auth/login", headers={"Origin": origin, "Access-Control-Request-Method": "POST"}
    )
    r.check(
        pre.headers.get("access-control-allow-origin") == origin
        and pre.headers.get("access-control-allow-credentials") == "true",
        "CORS allows the frontend origin with credentials",
        pre.headers.get("access-control-allow-origin"),
    )
    home = httpx.get(front + "/", timeout=60)
    r.check(
        home.status_code == 200 and '<div id="root"' in home.text,
        "frontend serves the SPA",
        home.status_code,
    )

    def login(var, default):
        user, password = _account(var, default)
        res = c.post(
            "/api/auth/login",
            json={"username": user, "password": password},
            headers={"Origin": origin},
        )
        ok = r.check(
            res.status_code == 200 and "access_token" in res.json(),
            f"login {user}",
            res.status_code,
        )
        if not ok:
            return user, None
        headers = {"Authorization": f"Bearer {res.json()['access_token']}", "Origin": origin}
        me = c.get("/api/auth/me", headers=headers)
        r.check(me.status_code == 200, f"GET /api/auth/me as {user}", me.status_code)
        return user, headers

    r.log("== 2. Login")
    student, hs = login("VERIFY_STUDENT", "estudiante_colegio_1:test1234")
    diag_student, hd = login("VERIFY_DIAGNOSTIC_STUDENT", "estudiante_colegio_2:test1234")
    teacher, ht = login("VERIFY_TEACHER", "profesor1:demo1234")
    if not (hs and hd and ht):
        return finish(r, args)

    r.log(f"== 3. Diagnostic ({diag_student})")
    courses = c.get("/api/student/courses", headers=hd).json()
    # The diagnostic needs an enrolment (spec 001 FR-037): the enrolled courses first, then one
    # catalogue course without a diagnostic, enrolled here.
    candidates = [x for x in courses if x.get("enrolled")] + [
        x for x in courses if not x.get("enrolled") and not x.get("diagnostic_done")
    ][:1]
    pending = None
    for course in candidates:
        if not course.get("enrolled"):
            c.post("/api/student/enroll", headers=hd, json={"course_id": course["id"]})
        status = c.get(f"/api/student/diagnostic/{course['id']}", headers=hd)
        if (
            status.status_code == 200
            and not status.json()["completed"]
            and status.json().get("questions")
        ):
            pending = (course, status.json())
            break
    if pending is None:
        r.warn("every catalogue course already has a diagnostic; re-taking one is not tested")
    else:
        course, status = pending
        answers = [
            {"item_id": q["id"], "selected_option": q["options"][0]} for q in status["questions"]
        ]
        res = c.post(
            f"/api/student/diagnostic/{course['id']}/submit",
            headers=hd,
            json={"answers": answers, "course_name": course.get("name", "")},
        )
        ok = res.status_code == 200
        r.check(
            ok and res.json().get("completed"),
            f"diagnostic submitted for {course['id']}",
            f"initial_elo {res.json().get('initial_elo')}" if ok else res.text[:150],
        )
        again = c.get(f"/api/student/diagnostic/{course['id']}", headers=hd).json()
        r.check(again.get("completed") is True, "diagnostic recorded as completed")

    r.log(f"== 4. Practice and rating update ({student})")
    enrolled = [x for x in c.get("/api/student/courses", headers=hs).json() if x.get("enrolled")]
    item = None
    for course in enrolled:
        nq = c.post("/api/student/next-question", headers=hs, json={"course_id": course["id"]})
        if nq.status_code == 200 and nq.json().get("item"):
            item, preview, practice_course = nq.json()["item"], nq.json()["preview"], course
            break
    if not r.check(
        item is not None,
        "next-question returns an item with a preview",
        [x["id"] for x in enrolled],
    ):
        return finish(r, args)
    ans = c.post(
        "/api/student/answer",
        headers=hs,
        json={"item_id": item["id"], "selected_option": item["options"][0], "time_taken": 25},
    )
    if r.check(ans.status_code == 200, "POST /api/student/answer", ans.status_code):
        a = ans.json()
        expected = preview["on_correct"] if a["is_correct"] else preview["on_wrong"]
        r.check(
            a["elo_valid"] and round(a["delta_elo"], 1) == expected,
            "rating moved by the previewed amount",
            f"{a['elo_before']:.2f} → {a['elo_after']:.2f} (Δ {a['delta_elo']:+.2f},"
            f" preview {expected:+.1f})",
        )
        stats = c.get("/api/student/stats", headers=hs).json()
        topics = [
            t
            for cr in stats.get("course_ratings", [])
            if cr["course_id"] == practice_course["id"]
            for t in cr["topics"]
        ]
        # /answer rounds elo_after to 2 decimals; stats return full precision.
        r.check(
            any(abs(t["rating"] - a["elo_after"]) <= 0.005 for t in topics),
            "stats show the new topic rating",
            f"{len(topics)} topics in {practice_course['id']}",
        )

    r.log(f"== 5. Map and lesson images ({LESSON_COURSE})")
    c.post("/api/student/enroll", headers=hs, json={"course_id": LESSON_COURSE})
    mp = c.get(f"/api/student/map/{LESSON_COURSE}", headers=hs)
    nodes = mp.json().get("nodes", []) if mp.status_code == 200 else []
    r.check(mp.status_code == 200 and nodes, "GET map", f"{len(nodes)} nodes")
    ids = [n["node_id"] for n in nodes if n.get("node_id")]
    first = c.get(f"/api/student/lessons/{LESSON_COURSE}/{ids[0]}", headers=hs) if ids else None
    r.check(
        first is not None and first.status_code == 200,
        "first lesson loads",
        ids[0] if ids else "no lesson nodes",
    )
    if len(ids) > 1:
        gated = c.get(f"/api/student/lessons/{LESSON_COURSE}/{ids[-1]}", headers=hs)
        r.check(
            gated.status_code in (200, 403),
            "later lessons answer (403 until unlocked)",
            gated.status_code,
        )
    # Lessons unlock in sequence, so the images are read from the lesson content of this
    # checkout (run it at the deployed commit) and requested from the frontend.
    images = set()
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.domain.learning.prealgebra import get_lesson

        for node_id in ids:
            _images(get_lesson(node_id) or {}, images)
    except Exception as exc:  # the API checks above still stand
        r.warn("could not read lesson content from this checkout", exc)
    missing = []
    for path in sorted(images):
        res = httpx.get(front + path, timeout=60)
        if res.status_code != 200 or not res.headers.get("content-type", "").startswith(
            IMAGE_TYPES
        ):
            missing.append(f"{path} ({res.status_code} {res.headers.get('content-type', '')})")
    r.check(
        images and not missing,
        "every lesson image is served by the frontend",
        f"{len(images) - len(missing)}/{len(images)} ok"
        + (f"; missing: {missing[:5]}" if missing else ""),
    )

    r.log(f"== 6. Procedure review ({student} → {teacher})")
    png = _png(int(time.time() * 1000))
    sub = c.post(
        "/api/student/procedure",
        headers={k: v for k, v in hs.items()},
        data={"item_id": item["id"], "item_content": "verify_deployment"},
        files={"file": ("verify.png", png, "image/png")},
    )
    if not r.check(
        sub.status_code in (200, 201) and sub.json().get("submission_id"),
        "student uploads a procedure",
        sub.text[:150],
    ):
        return finish(r, args)
    sid = sub.json()["submission_id"]
    queue = c.get("/api/teacher/procedures", headers=ht).json()
    r.check(
        any(p["submission_id"] == sid for p in queue),
        "teacher sees it in the queue",
        f"submission {sid}",
    )
    img = c.get(f"/api/teacher/procedures/{sid}/image", headers=ht)
    r.check(
        img.status_code == 200 and img.content == png,
        "teacher gets the same image bytes back (storage)",
        img.status_code,
    )
    before = c.get("/api/student/stats", headers=hs).json()
    grade = c.post(
        "/api/teacher/procedures/grade",
        headers=ht,
        json={"submission_id": sid, "teacher_score": 80, "teacher_feedback": "verify_deployment"},
    )
    if r.check(grade.status_code == 200, "teacher grades it", grade.text[:150]):
        delta = grade.json()["elo_delta"]
        after = c.get("/api/student/stats", headers=hs).json()
        moved = (after.get("global_elo") or 0) - (before.get("global_elo") or 0)
        r.check(
            delta > 0 and moved > 0,
            "the validated grade moves the student's rating",
            f"elo_delta {delta:+.2f}, overall {before.get('global_elo')} →"
            f" {after.get('global_elo')}",
        )
    return finish(r, args)


def finish(r, args):
    r.log("")
    verdict = "PASS" if not r.failures else f"FAIL ({len(r.failures)} checks)"
    r.log(f"RESULT: {verdict}" + (f" with {len(r.warnings)} warnings" if r.warnings else ""))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("\n".join(r.lines) + "\n")
    return 0 if not r.failures else 1


if __name__ == "__main__":
    sys.exit(main())
