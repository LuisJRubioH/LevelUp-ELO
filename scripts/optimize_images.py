"""Serves the app's pictures as WebP: converts them and points every reference at the new file.

The lesson art and KatIA's pictures under `frontend/public/` were exported as lossless PNG and
GIF: about 3 MB a scene, 6.5 MB for an avatar shown at most 128 px wide, 2 MB for the GIF on the
login page. WebP at quality 90 cannot be told apart at 2x zoom (luma SSIM >= 0.99 on the scenes)
and weighs about a sixth. Every supported browser decodes it (Safari since 14).

    python scripts/optimize_images.py            # lists what --apply would convert; writes nothing
    python scripts/optimize_images.py --apply    # writes each .webp, deletes the original and
                                                 # rewrites the references in the code
    python scripts/optimize_images.py --check    # exit 1 if a served picture still needs it

A new picture for the app: put the PNG in `frontend/public/`, reference it from the code
(`/leccion/...png`), run `--apply` and commit the result. Pictures up to `LEGACY_MAX_BYTES`
(logos, course banners) stay as they are. `tests/unit/test_served_images.py` runs the check.

Run from the repository root. `--apply` needs Pillow (requirements-api.txt); the list and the
check use the standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend" / "public"

# Where the code names a served picture by its URL path ("/leccion/...", "/katia/...").
REFERENCE_ROOTS = (
    ROOT / "src" / "domain" / "learning",
    ROOT / "frontend" / "src",
    ROOT / "frontend" / "index.html",
)
REFERENCE_SUFFIXES = {".py", ".ts", ".tsx", ".css", ".html"}

LEGACY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif"}
# A PNG, JPEG or GIF above this size is converted; below it (logos, banners) the gain is noise.
LEGACY_MAX_BYTES = 150_000
WEBP_QUALITY = 90
WEBP_METHOD = 6  # slowest, smallest; quality is unaffected

# Widest the picture needs to be, where the source is far larger than any screen shows it.
MAX_WIDTH = {
    # KatIA's portrait: at most 128 CSS px (KatIAAvatar "lg"); 800 px covers a 3x screen twice over.
    "katia/katIA.png": 800,
}


def pending(public: Path = PUBLIC) -> list[Path]:
    """The served pictures that still need converting, sorted."""
    return sorted(
        path
        for path in public.rglob("*")
        if path.is_file()
        and path.suffix.lower() in LEGACY_SUFFIXES
        and path.stat().st_size > LEGACY_MAX_BYTES
    )


def url_path(path: Path, public: Path = PUBLIC) -> str:
    """The URL path the app requests a public file by: `/leccion/x/y.png`."""
    return "/" + path.relative_to(public).as_posix()


def reference_files(roots=REFERENCE_ROOTS) -> list[Path]:
    files = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(
                p for p in root.rglob("*") if p.is_file() and p.suffix in REFERENCE_SUFFIXES
            )
    return sorted(files)


def convert(source: Path, public: Path = PUBLIC) -> Path:
    """Writes `source` as WebP next to it and returns the new path. Does not delete `source`."""
    from PIL import Image, ImageSequence

    target = source.with_suffix(".webp")
    with Image.open(source) as image:
        if getattr(image, "n_frames", 1) > 1:
            frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
            durations = [frame.info.get("duration", 100) for frame in ImageSequence.Iterator(image)]
            if all(frame.getchannel("A").getextrema()[0] == 255 for frame in frames):
                frames = [frame.convert("RGB") for frame in frames]
            frames[0].save(
                target,
                "WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=image.info.get("loop", 0),
                quality=WEBP_QUALITY,
                method=WEBP_METHOD,
            )
            return target

        has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
        picture = image.convert("RGBA" if has_alpha else "RGB")
        if has_alpha and picture.getchannel("A").getextrema()[0] == 255:
            picture = picture.convert("RGB")  # an alpha channel that hides nothing
        max_width = MAX_WIDTH.get(source.relative_to(public).as_posix())
        if max_width and picture.width > max_width:
            height = round(picture.height * max_width / picture.width)
            picture = picture.resize((max_width, height), Image.Resampling.LANCZOS)
        picture.save(target, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
    return target


def rewrite_references(old: str, new: str, files: list[Path]) -> int:
    """Replaces the URL path `old` with `new` in `files`; returns how many it replaced. Only the
    whole path: `/a.png` does not touch `/leccion/a.png`."""
    pattern = re.compile(r"(?<![\w./-])" + re.escape(old) + r"(?![\w.-])")
    count = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        text, replaced = pattern.subn(new, text)
        if replaced:
            count += replaced
            path.write_text(text, encoding="utf-8")
    return count


def _kb(size: int) -> str:
    return f"{size / 1024:,.0f} KB"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="convert and rewrite the references")
    mode.add_argument("--check", action="store_true", help="exit 1 if anything needs converting")
    args = parser.parse_args(argv)

    todo = pending()
    if args.check:
        for path in todo:
            print(f"needs converting: {url_path(path)} ({_kb(path.stat().st_size)})")
        if todo:
            print("run: python scripts/optimize_images.py --apply")
        return 1 if todo else 0

    if not todo:
        print("nothing to convert")
        return 0
    if not args.apply:
        for path in todo:
            print(f"{url_path(path)}  {_kb(path.stat().st_size)}")
        print(f"{len(todo)} file(s), {_kb(sum(p.stat().st_size for p in todo))}; --apply converts")
        return 0

    files = reference_files()
    before = after = 0
    unreferenced = []
    for path in todo:
        size = path.stat().st_size
        target = convert(path)
        old, new = url_path(path), url_path(target)
        replaced = rewrite_references(old, new, files)
        path.unlink()
        before += size
        after += target.stat().st_size
        print(f"{old} -> {new}  {_kb(size)} -> {_kb(target.stat().st_size)}  ({replaced} ref.)")
        if not replaced:
            unreferenced.append(new)
    print(f"{len(todo)} file(s): {_kb(before)} -> {_kb(after)} ({1 - after / before:.0%} less)")
    for new in unreferenced:
        print(f"warning: nothing in the code names {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
