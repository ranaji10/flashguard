"""Out-of-band unlock guidance data loader."""

import json
import pathlib

_GUIDANCE_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "unlock_guidance.json"


def load_guidance():
    if _GUIDANCE_PATH.is_file():
        with open(_GUIDANCE_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"methods": {}, "exclusions": {}}


_GUIDANCE_DATA = load_guidance()


def get_guidance(method_name):
    """Return structured out-of-band unlock guidance for a method, or None if unknown."""
    if not method_name or not isinstance(method_name, str):
        return None
    methods = _GUIDANCE_DATA.get("methods", {})
    entry = methods.get(method_name)
    if not entry or not isinstance(entry, dict) or not entry.get("steps"):
        return None
    res = {
        "steps": list(entry["steps"]),
    }
    if entry.get("link"):
        res["link"] = entry["link"]
    return res
