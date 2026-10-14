"""Every image a bank item points to is served by the API at the path the screens request
(`resolveImageUrl` prefixes the API's address to the item's `image_url`)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _item_images():
    images = set()
    for path in sorted((ROOT / "items" / "bank").rglob("*.json")):
        for item in json.loads(path.read_text(encoding="utf-8")):
            url = (item.get("image_url") or item.get("image_path") or "").strip()
            if url and not url.startswith(("http://", "https://")):
                images.add("/" + url.lstrip("/"))
    return sorted(images)


def test_the_bank_has_item_images():
    assert len(_item_images()) > 50


def test_every_item_image_is_served(api_client):
    missing = [url for url in _item_images() if api_client.get(url).status_code != 200]
    assert missing == []
