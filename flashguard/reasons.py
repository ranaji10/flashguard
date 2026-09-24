"""Plain-language descriptions and kinds for verifier reason codes.

Loaded once from data/reason_codes.json. Descriptions are for people; codes stay the
stable machine interface. Every abstention is one of two kinds:

  honest   the phone or the world does not give the evidence. The tool is doing its job.
  our_gap  the recipe or the format is missing something this project can fix.
"""

import fnmatch
import json
import pathlib

_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "reason_codes.json"


def _load():
    if not _PATH.is_file():
        raise RuntimeError("data/reason_codes.json is missing: the verifier refuses to describe reasons it cannot name")
    with open(_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


_DATA = _load()
KINDS = tuple(_DATA["kinds"].keys())


def describe(code, result=None):
    """Return (kind, plain text) for a reason code. Unknown codes are 'unclassified'."""
    code = code or ""
    for entry in _DATA["codes"]:
        if fnmatch.fnmatchcase(code, entry["match"]):
            return entry["kind"], entry["plain"]
    return "unclassified", "No plain description exists for this reason yet: " + code


def kind_label(kind):
    return _DATA["kinds"].get(kind, {}).get("label", kind)


def scope():
    return json.loads(json.dumps(_DATA["scope"]))
