import os
import re
import requests
from dotenv import load_dotenv
from modules.cache import cache_get, cache_set

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

PLACES_KEY = os.getenv("PLACES_API_KEY")
PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
IMG_DIR = os.path.join(EXPORTS_DIR, "images")

def _safe_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)
    return s[:80] if s else "place"

def download_photo(photo_reference: str, place_name: str, max_width: int = 900) -> str | None:
    if not PLACES_KEY or not photo_reference:
        return None

    os.makedirs(IMG_DIR, exist_ok=True)
    fname = f"{_safe_name(place_name)}_{_safe_name(photo_reference)}.jpg"
    fpath = os.path.join(IMG_DIR, fname)

    if os.path.exists(fpath):
        return fpath

    cache_key = f"photo:{photo_reference}:{max_width}"
    cached_path = cache_get(cache_key, max_age_seconds=7 * 24 * 3600)
    if cached_path and os.path.exists(cached_path):
        return cached_path

    params = {"maxwidth": max_width, "photoreference": photo_reference, "key": PLACES_KEY}
    r = requests.get(PHOTO_URL, params=params, timeout=60)
    if r.status_code != 200:
        return None

    with open(fpath, "wb") as f:
        f.write(r.content)

    cache_set(cache_key, fpath)
    return fpath
