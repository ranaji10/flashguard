"""Pure v0.1, v0.2 and v0.3 recipe verification.

verify() is a pure function: no device I/O, and deterministic given its two arguments.
Its modules read three data files (vocabulary, reason texts, unlock guidance) once at
import; that is not device I/O.
"""

import json
import pathlib
import re

from flashguard.guidance import get_guidance
from flashguard.reasons import describe, scope as verdict_scope

_VOCABULARY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "vocabulary.json"


def _load_vocabulary():
    if not _VOCABULARY_PATH.is_file():
        raise RuntimeError("data/vocabulary.json is missing or invalid: the verifier refuses to guess its vocabulary")
    try:
        with open(_VOCABULARY_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        raise RuntimeError("data/vocabulary.json is missing or invalid: the verifier refuses to guess its vocabulary") from exc


_VOCABULARY = _load_vocabulary()


def _is_numeric_or_version(val):
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        val = val.strip()
        if re.match(r"^\d+(\.\d+)*$", val):
            return True
    return False


def _parse_version(val):
    """Parse integer, float, or version string into a tuple of ints, or None if unparseable."""
    if isinstance(val, bool):
        return None
    if isinstance(val, int):
        return (val,)
    if isinstance(val, float):
        val = str(val)
    if isinstance(val, str):
        val = val.strip()
        parts = val.split(".")
        try:
            return tuple(int(p) for p in parts if p)
        except ValueError:
            return None
    return None


_EMPTY = (None, "", "unknown", "not_applicable", "not_recorded")


# Ruled 17 Oct 2026 (docs/reasoning/layout-absence-rule.md). No Android property says
# "single". A/B phones say A/B through three independent markers: ro.build.ab_update (written
# by the build system whenever AB_OTA_UPDATER is set), ro.boot.slot_suffix (passed by the
# bootloader on every A/B boot) and, for virtual A/B, ro.virtual_ab.enabled. derive.sh writes
# _ABSENT_BASIS only when it queried all three and all three were empty. Within the scope
# below, that absence is read as single. Outside it the verifier abstains as before.
_ABSENT_BASIS = "no ab_update, no slot_suffix, no virtual_ab -- absent is not the same as single"


def _inferred_single(fingerprint):
    """True when the absence rule reads this phone's layout as single."""
    if fingerprint.get("partition_scheme") not in _EMPTY:
        return False
    if fingerprint.get("partition_basis") != _ABSENT_BASIS:
        return False
    if fingerprint.get("slot_suffix") not in _EMPTY:
        return False
    if fingerprint.get("firmware_origin") != "stock":
        return False
    # Widened the same evening from Android 8+ to every version. AOSP's A/B FAQ: the platform
    # code is "public in Android 7.1 and higher", and the first A/B phones were the Pixel and
    # Pixel XL of October 2016. Older stock firmware had no public A/B to carry. The SDK must
    # still be readable, as evidence that the phone's properties were read.
    try:
        int(str(fingerprint.get("sdk")).strip())
    except (TypeError, ValueError):
        return False
    build_type = fingerprint.get("build_type")
    build_tags = fingerprint.get("build_tags")
    fingerprint_text = str(fingerprint.get("build_fingerprint") or "")
    if build_type in _EMPTY or build_tags in _EMPTY:
        # Captures before kit 2026-10-08 did not read these; the fingerprint carries both.
        return fingerprint_text.endswith(":user/release-keys")
    return build_type == "user" and build_tags == "release-keys"


def _public_model_source(sources):
    """True when at least one entry names an https URL on a domain in the vocabulary.

    Ruled 8 Oct 2026: a model list is credible only with a public source behind it. The
    verifier cannot judge credibility, so it checks the source against a fixed list of
    domains held in data/vocabulary.json, which a person maintains.
    """
    domains = _VOCABULARY.get("model_source_domains", [])
    if not isinstance(sources, list):
        return False
    for entry in sources:
        url = entry.get("url") if isinstance(entry, dict) else None
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        host = url[len("https://"):].split("/", 1)[0].split(":", 1)[0].lower()
        if host.split(".", 1)[0] in _VOCABULARY.get("model_source_excluded_subdomains", []):
            continue  # a community forum on a maker's domain is not the maker speaking
        if any(host == d or host.endswith("." + d) for d in domains):
            return True
    return False


# Ruled 8 Oct 2026, evening: when the sources cannot settle the model, the verdict is
# not-ready pending the person's confirmation, never cannot-verify for that reason alone.
_PENDING_CODES = ("model-needs-confirmation", "model-ambiguous-variant", "device-code-differs")


def _norm_model(value):
    return " ".join(str(value).upper().split())


def _model_forms(model, manufacturer):
    """A reported model as the sources may write it: case and spacing ignored, and the
    manufacturer's own name dropped from the front (OnePlus reports "ONEPLUS A6013" where
    GSMArena writes "A6013"). Only the phone's own manufacturer name is ever dropped."""
    forms = {_norm_model(model)}
    if manufacturer not in _EMPTY:
        prefix = _norm_model(manufacturer) + " "
        for f in list(forms):
            if f.startswith(prefix) and len(f) > len(prefix):
                forms.add(f[len(prefix):])
    return forms


def _reason(code, result, fields, message):
    return {
        "code": code,
        "result": result,
        "fields": list(fields),
        "message": message,
    }


def _build_evidence(fingerprint, fields_consumed):
    if not isinstance(fingerprint, dict):
        return {"record_id": None, "capture_timestamp": None, "fields_consumed": []}
    consumed = []
    seen = set()
    for f in fields_consumed:
        if f not in seen:
            seen.add(f)
            consumed.append(f)
    return {
        "record_id": fingerprint.get("record_id"),
        "capture_timestamp": (
            fingerprint.get("capture_timestamp")
            or fingerprint.get("timestamp")
            or fingerprint.get("date")
        ),
        "fields_consumed": consumed,
    }


def _invalid_recipe_reason(message, fingerprint=None):
    return {
        "verdict": "cannot-verify",
        "reasons": [_reason("invalid-recipe", "abstain", ["recipe"], message)],
        "coverage": {"schema_version": None, "modelled_operations": [], "safe_case_available": False},
        "evidence": _build_evidence(fingerprint, []),
    }


def _validate_recipe(recipe):
    if not isinstance(recipe, dict):
        return "Invalid recipe: expected a JSON object."
    required = ("schema_version", "recipe_id", "target", "operations")
    missing = [key for key in required if key not in recipe]
    if missing:
        return "Invalid recipe: missing required field(s): " + ", ".join(missing) + "."
    if recipe.get("schema_version") not in ("0.1", "0.2", "0.3"):
        return "Invalid recipe: unsupported schema_version."
    target = recipe.get("target")
    if not isinstance(target, dict):
        return "Invalid recipe: target must be an object."
    target_fields = ("product_device", "partition_scheme")
    if any(field not in target for field in target_fields):
        return "Invalid recipe: target is missing a required field."
    if "models" in target and not isinstance(target["models"], list):
        return "Invalid recipe: models must be an array."
    if "supported_device_codes" in target and not isinstance(target["supported_device_codes"], list):
        return "Invalid recipe: supported_device_codes must be an array."
    operations = recipe.get("operations")
    if not isinstance(operations, list):
        return "Invalid recipe: operations must be an array."
    if recipe.get("schema_version") in ("0.2", "0.3"):
        required_v2 = ("source", "install_method", "source_fields_unused")
        if any(key not in recipe for key in required_v2):
            return "Invalid recipe: v0.2 is missing a required field."
        if not isinstance(recipe["source"], dict) or not isinstance(recipe["source_fields_unused"], list):
            return "Invalid recipe: v0.2 source and source_fields_unused are invalid."
        absent = object()
        prerequisites = recipe.get("prerequisites", absent)
        if prerequisites is not absent and prerequisites is not None and not isinstance(prerequisites, dict):
            return "Invalid recipe: prerequisites must be an object, null, or absent."
        if recipe.get("schema_version") == "0.2" and isinstance(prerequisites, dict):
            for req in prerequisites.values():
                if isinstance(req, dict) and (
                    "unlock_readback" in req or "requirement" in req or req.get("compare") == "one_of"
                    or "unlock_route" in req
                ):
                    return "Invalid recipe: a v0.2 recipe uses a v0.3 field (unlock_readback, requirement, one_of or unlock_route)."
        for operation in operations:
            if not isinstance(operation, dict) or any(field not in operation for field in ("kind", "partition")):
                return "Invalid recipe: every v0.2 operation needs kind and partition."
        return None
    assets = recipe.get("assets")
    if not isinstance(assets, list):
        return "Invalid recipe: assets must be an array."
    asset_ids = []
    for asset in assets:
        if not isinstance(asset, dict):
            return "Invalid recipe: every asset must be an object."
        if any(field not in asset for field in ("asset_id", "role", "product_device")):
            return "Invalid recipe: every asset needs identity fields."
        asset_ids.append(asset["asset_id"])
    if len(asset_ids) != len(set(asset_ids)):
        return "Invalid recipe: asset_id values must be unique."
    for operation in operations:
        if not isinstance(operation, dict):
            return "Invalid recipe: every operation must be an object."
        if any(field not in operation for field in ("kind", "partition", "asset_id")):
            return "Invalid recipe: every operation needs kind, partition, and asset_id."
        if operation["asset_id"] not in asset_ids:
            return "Invalid recipe: operation refers to an unknown asset_id."
    return None


def verify(fingerprint, recipe):
    """Return a verdict for a fingerprint and a recipe.

    Every result carries a plain-language description and a kind on each reason, and
    the scope of what was and was not checked, so no consumer can render a verdict
    without also rendering its limits.
    """
    result = _verify_core(fingerprint, recipe)
    for reason in result.get("reasons", []):
        kind, plain = describe(reason.get("code"), reason.get("result"))
        reason["kind"] = kind
        reason["plain"] = plain
    result["scope"] = verdict_scope()
    return result


def _verify_core(fingerprint, recipe):
    invalid = _validate_recipe(recipe)
    if invalid:
        return _invalid_recipe_reason(invalid, fingerprint)

    if recipe.get("schema_version") in ("0.2", "0.3"):
        return _verify_v2(fingerprint, recipe)

    if fingerprint is None:
        fingerprint = {}
    reasons = []
    unsafe = False
    abstained = False
    target = recipe.get("target", {})
    fields_consumed = []

    # Check product_device
    observed_device = fingerprint.get("product_device")
    fields_consumed.append("product_device")
    expected_device = target.get("product_device")
    if observed_device in (None, "", "unknown", "not_applicable"):
        abstained = True
        reasons.append(
            _reason(
                "missing-product_device",
                "abstain",
                ["product_device", "target.product_device"],
                "Required fingerprint evidence is absent or unknown.",
            )
        )
    elif observed_device != expected_device:
        unsafe = True
        reasons.append(
            _reason(
                "device-mismatch",
                "fail",
                ["product_device", "target.product_device"],
                "Fingerprint value contradicts the recipe target.",
            )
        )
    else:
        reasons.append(
            _reason(
                "match-product_device",
                "pass",
                ["product_device", "target.product_device"],
                "Fingerprint value matches the recipe target.",
            )
        )

    # Check partition_scheme
    observed_scheme = fingerprint.get("partition_scheme")
    fields_consumed.append("partition_scheme")
    expected_scheme = target.get("partition_scheme")
    if observed_scheme in (None, "", "unknown", "not_applicable"):
        abstained = True
        reasons.append(
            _reason(
                "missing-partition_scheme",
                "abstain",
                ["partition_scheme", "target.partition_scheme"],
                "Required fingerprint evidence is absent or unknown.",
            )
        )
    elif observed_scheme != expected_scheme:
        unsafe = True
        reasons.append(
            _reason(
                "partition-scheme-mismatch",
                "fail",
                ["partition_scheme", "target.partition_scheme"],
                "Fingerprint value contradicts the recipe target.",
            )
        )
    else:
        reasons.append(
            _reason(
                "match-partition_scheme",
                "pass",
                ["partition_scheme", "target.partition_scheme"],
                "Fingerprint value matches the recipe target.",
            )
        )

    # Check models
    observed_model = fingerprint.get("product_model")
    target_models = target.get("models")
    if "models" not in target or target_models is None or not isinstance(target_models, list) or len(target_models) == 0:
        abstained = True
        reasons.append(
            _reason(
                "models-unestablished",
                "abstain",
                ["target.models"],
                "Recipe model coverage is unestablished.",
            )
        )
    elif observed_model in (None, "", "unknown", "not_applicable"):
        fields_consumed.append("product_model")
        abstained = True
        reasons.append(
            _reason(
                "missing-product_model",
                "abstain",
                ["product_model", "target.models"],
                "Target product_model is unconfirmed from fingerprint.",
            )
        )
    elif observed_model not in target_models:
        fields_consumed.append("product_model")
        unsafe = True
        reasons.append(
            _reason(
                "model-mismatch",
                "fail",
                ["product_model", "target.models"],
                f"Fingerprint model '{observed_model}' contradicts the recipe target models.",
            )
        )
    else:
        fields_consumed.append("product_model")
        reasons.append(
            _reason(
                "match-product_model",
                "pass",
                ["product_model", "target.models"],
                f"Fingerprint model '{observed_model}' matches recipe target models.",
            )
        )

    # Asset identity decision: Assets in v0.1 are pinned per codename (product_device).
    # Each asset's product_device must match target.product_device. Model eligibility
    # is enforced at the recipe target.models level.
    for asset in recipe.get("assets", []):
        asset_id = asset.get("asset_id", "")
        if asset.get("product_device") != target.get("product_device"):
            unsafe = True
            reasons.append(
                _reason(
                    "asset-product_device-mismatch",
                    "fail",
                    ["assets." + asset_id + ".product_device", "target.product_device"],
                    "Asset identity contradicts the recipe target.",
                )
            )

    known_assets = {asset.get("asset_id") for asset in recipe.get("assets", [])}
    for operation in recipe.get("operations", []):
        if operation.get("kind") != "write-image":
            abstained = True
            reasons.append(
                _reason(
                    "unsupported-operation",
                    "abstain",
                    ["operations"],
                    "The operation is outside the v0.1 model.",
                )
            )
        elif operation.get("asset_id") not in known_assets:
            abstained = True
            reasons.append(
                _reason(
                    "unknown-asset",
                    "abstain",
                    ["operations.asset_id", "assets"],
                    "The operation refers to an unidentified asset.",
                )
            )

    coverage = {
        "schema_version": recipe.get("schema_version"),
        "modelled_operations": ["write-image"],
        "safe_case_available": False,
    }
    if unsafe:
        verdict = "unsafe"
    elif abstained:
        verdict = "cannot-verify"
    else:
        reasons.append(
            _reason(
                "v0.1-incomplete-safety-model",
                "abstain",
                ["recipe", "prerequisites", "asset_identity"],
                "V0.1 cannot establish procedure completeness or prerequisite state.",
            )
        )
        verdict = "cannot-verify"

    return {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": coverage,
        "evidence": _build_evidence(fingerprint, fields_consumed),
    }


def _is_unlock_prerequisite(name, req):
    if not isinstance(req, dict):
        return False
    if req.get("unlock_step") is True:
        return True
    if "unlock_class" in req:
        return True
    declared_by = req.get("declared_by")
    if isinstance(declared_by, str) and "unlock" in declared_by.lower():
        return True
    return False


def _verify_v2(fingerprint, recipe):
    ctx = {}
    result = _verify_v2_inner(fingerprint, recipe, ctx)
    if result.get("verdict") in ("cannot-verify", "not-ready") and ctx.get("confirmation_request"):
        result.setdefault("evidence", {})["confirmation_request"] = ctx["confirmation_request"]
    return result


def _verify_v2_inner(fingerprint, recipe, ctx):
    if fingerprint is None:
        fingerprint = {}
    reasons = []
    target = recipe["target"]
    fields_consumed = []
    identity_mismatch = False
    device_reason_index = None
    supported_aliases = target.get("supported_device_codes", [])

    observed_device = fingerprint.get("product_device")
    fields_consumed.append("product_device")
    expected_device = target.get("product_device")
    # Ruled 8 Oct 2026: custom firmware is in scope. A ROM writes ro.product.* itself, so on
    # custom firmware those values can confirm an identity but never contradict one.
    custom_firmware = fingerprint.get("firmware_origin") == "custom"
    if custom_firmware:
        fields_consumed.append("firmware_origin")
    rom_candidates = [fingerprint.get(k) for k in ("product_device", "lineage_device", "vendor_device")]
    rom_candidates = [c for c in rom_candidates if c not in _EMPTY]

    if custom_firmware and any(c == expected_device or c in supported_aliases for c in rom_candidates):
        fields_consumed.extend(["lineage_device", "vendor_device"])
        reasons.append(
            _reason("match-device-custom-firmware", "pass", ["product_device", "lineage_device", "vendor_device", "target.product_device"],
                    "On custom firmware, a device code the ROM reports matches the recipe target.")
        )
    elif custom_firmware:
        reasons.append(
            _reason("identity-custom-firmware", "abstain", ["product_device", "firmware_origin"],
                    "The phone runs custom firmware whose device code does not match; a ROM's own identity cannot show the recipe is wrong.")
        )
    elif observed_device in (None, "", "unknown", "not_applicable"):
        reasons.append(
            _reason("missing-product_device", "abstain", ["product_device"], "Required fingerprint evidence is absent or unknown.")
        )
    elif observed_device == expected_device:
        reasons.append(
            _reason("match-product_device", "pass", ["product_device", "target.product_device"], "Fingerprint value matches the recipe target.")
        )
    elif observed_device in supported_aliases:
        reasons.append(
            _reason("match-device-alias", "pass", ["product_device", "target.supported_device_codes"], f"Device code matches supported alias '{observed_device}'.")
        )
    else:
        # Held open until the model is read: stock firmware often reports an internal code
        # (OP5958L1) where upstream uses a codename (larry). Credible sources settle it below.
        device_reason_index = len(reasons)
        reasons.append(
            _reason("device-mismatch", "fail", ["product_device", "target.product_device"], "Fingerprint value contradicts the recipe target.")
        )
        identity_mismatch = True

    observed_scheme = fingerprint.get("partition_scheme")
    fields_consumed.append("partition_scheme")
    expected_scheme = target.get("partition_scheme")
    inferred_fields = ["partition_scheme", "partition_basis", "slot_suffix", "firmware_origin", "sdk",
                       "build_type", "build_tags", "build_fingerprint", "target.partition_scheme"]

    if observed_scheme in _EMPTY and _inferred_single(fingerprint):
        fields_consumed.extend(inferred_fields[1:-1])
        if expected_scheme == "single":
            reasons.append(
                _reason("match-partition_scheme-inferred-single", "pass", inferred_fields,
                        "Stock firmware shows none of the three A/B markers, so the layout is read as single, which the recipe expects.")
            )
        else:
            reasons.append(
                _reason("partition-scheme-mismatch-inferred", "fail", inferred_fields,
                        "Stock firmware shows none of the three A/B markers, so the layout is read as single; the recipe expects slots.")
            )
            identity_mismatch = True
    elif observed_scheme in (None, "", "unknown", "not_applicable"):
        reasons.append(
            _reason("missing-partition_scheme", "abstain", ["partition_scheme"], "Required fingerprint evidence is absent or unknown.")
        )
    elif expected_scheme == "A/B" and observed_scheme == "virtual_A/B":
        # Upstream records only whether a device has slots (is_ab_device). Virtual A/B has
        # slots; a recipe written for A/B therefore fits it. The reverse does not hold.
        reasons.append(
            _reason("match-partition_scheme-slots", "pass", ["partition_scheme", "target.partition_scheme"],
                    "The recipe is for a phone with A/B slots, and virtual A/B has them.")
        )
    elif observed_scheme != expected_scheme:
        reasons.append(
            _reason("partition-scheme-mismatch", "fail", ["partition_scheme", "target.partition_scheme"], "Fingerprint value contradicts the recipe target.")
        )
        identity_mismatch = True
    else:
        reasons.append(
            _reason("match-partition_scheme", "pass", ["partition_scheme", "target.partition_scheme"], "Fingerprint value matches the recipe target.")
        )

    # Ruled 8 Oct 2026, revised the same day: capture asks the tester nothing about the model.
    # The verifier settles it from credible public sources, each of which records the model
    # codes it lists. Only when no credible source lists any model does it ask, and then it
    # returns a confirmation_request naming the phone's reported models, the links this
    # recipe rests on, and the upstream entries it cannot tell apart from them. The person's
    # answer comes back as model_confirmation plus the link they recognised, and counts
    # only for a link of this recipe. An answer never overrides a credible list.
    sources = target.get("models_sources") if isinstance(target.get("models_sources"), list) else []
    credible = [src for src in sources if _public_model_source([src])]
    credible_models = set()
    for src in credible:
        if isinstance(src.get("models"), list):
            credible_models.update(m for m in src["models"] if isinstance(m, str) and m)
    recipe_models = target.get("models") if isinstance(target.get("models"), list) else []
    effective = (credible_models & set(recipe_models)) if recipe_models else credible_models

    software = [] if custom_firmware else [fingerprint.get("product_model")]
    observed_models = software + [fingerprint.get("hardware_sku"), fingerprint.get("vendor_model")]
    model_fields = (["product_model"] if not custom_firmware else []) + ["hardware_sku", "vendor_model"]
    observed_models = [m for m in observed_models if m not in _EMPTY]

    source_names = {str(src.get("name")).lower() for src in credible if src.get("name")}
    manufacturer = fingerprint.get("manufacturer")
    reported_names = {m.lower() for m in observed_models}
    if manufacturer not in _EMPTY:
        reported_names |= {(manufacturer + " " + m).lower() for m in observed_models}
    name_hit = bool(source_names & reported_names)

    competing = [c for c in (target.get("competing_sources") or []) if isinstance(c, dict)]

    def config(src, own):
        out = {k: src.get(k) for k in ("project", "name", "url", "install_method") if src.get(k)}
        out["models"] = src.get("models") if src.get("models") else "no model codes listed"
        out["this_recipe"] = own
        return out

    def ask_or_accept(code_if_unanswered, message, mismatch=None):
        """The sources cannot settle the model: take the person's answer, or ask for it."""
        answer = fingerprint.get("model_confirmation")
        answered_url = fingerprint.get("model_confirmed_source")
        own_urls = {src.get("url") for src in credible}
        fields_consumed.append("model_confirmation")
        if answer == "human_confirmed" and answered_url in own_urls:
            reasons.append(
                _reason("match-model-confirmed-by-person", "pass", ["model_confirmation", "model_confirmed_source"],
                        "The sources could not settle the model; the person holding the phone recognised it as the device at " + str(answered_url) + ".")
            )
            return True
        if answer == "human_rejected":
            code, msg = "model-rejected-by-person", "The person holding the phone said it is not the device this recipe describes."
        elif answer == "human_confirmed":
            code, msg = "model-confirmed-elsewhere", "The person recognised the phone at a link this recipe does not rest on."
        else:
            code, msg = code_if_unanswered, message
        reason = _reason(code, "abstain", model_fields + ["target.models_sources"], msg)
        reasons.append(reason)
        found = list(mismatch or [])
        if device_reason_index is not None:
            found.insert(0, {"field": "product_device", "phone_reports": observed_device,
                             "recipe_expects": expected_device,
                             "aliases_known": list(supported_aliases)})
        ctx["confirmation_request"] = {
            "mismatch": found,
            "possible_configs": [config(src, True) for src in (credible or sources)] + [config(c, False) for c in competing],
            "observed_models": observed_models,
            "device": target.get("product_device"),
            "recipe_sources": [{k: src.get(k) for k in ("project", "url", "name") if src.get(k)} for src in credible]
                              or [{k: src.get(k) for k in ("project", "url", "name") if src.get(k)} for src in sources],
            "cannot_tell_apart_from": [{k: src.get(k) for k in ("project", "url", "name") if src.get(k)}
                                       for src in (target.get("competing_sources") or []) if isinstance(src, dict)],
            "question": "Your phone reports itself as %s. Is it the device described at the link%s above, and not one of the others listed?"
                        % (" / ".join(observed_models), "" if len(credible) == 1 else "s"),
        }
        if code in _PENDING_CODES:
            reason["remedy"] = ctx["confirmation_request"]["question"] + " Confirm it, then run the check again."
        return False

    def settle_device(by_model):
        """Resolve a held-open codename mismatch once the model has been read."""
        if device_reason_index is None:
            return
        if by_model:
            reasons[device_reason_index] = _reason(
                "match-device-by-model", "pass", ["product_device", "product_model", "target.models_sources"],
                "The phone's own device code differs from upstream's, and a credible source lists its model code for this recipe.")
        else:
            reasons[device_reason_index] = _reason(
                "device-code-differs", "abstain", ["product_device", "target.product_device"],
                "The phone's own device code differs from upstream's, and its model name matches the recipe's sources, so the person is asked.")

    if not observed_models:
        if effective:
            fields_consumed.append("product_model")
        reasons.append(
            _reason("missing-product_model", "abstain", ["product_model", "target.models"], "Target product_model is unconfirmed from fingerprint.")
        )
    elif effective:
        fields_consumed.extend(model_fields)
        effective_norm = {_norm_model(m) for m in effective}
        hit = next((m for m in observed_models
                    if _model_forms(m, fingerprint.get("manufacturer")) & effective_norm), None)
        hit_forms = _model_forms(hit, fingerprint.get("manufacturer")) if hit is not None else set()
        unexcluded = [c for c in competing
                      if not c.get("models") or ({_norm_model(m) for m in c["models"]} & hit_forms)]
        if hit is not None and unexcluded:
            # The code is listed for this recipe, but a device configuration that shares the
            # codename either lists no codes or lists the same one: the sources cannot tell
            # which of them the phone is (the 6T and the 6T T-Mobile are both A6013).
            settle_device(by_model=True)
            listed_by = [src.get("url") for src in credible
                         if {_norm_model(m) for m in (src.get("models") or [])} & hit_forms]
            ask_or_accept("model-ambiguous-variant",
                          "The model is listed for this recipe, but another device configuration with the same codename cannot be ruled out from the sources.",
                          [{"field": "product_model", "phone_reports": hit, "listed_for_this_recipe_by": listed_by,
                            "not_excluded_by": [{"name": c.get("name"), "url": c.get("url"),
                                                 "lists": c.get("models") or "no model codes"} for c in unexcluded]}])
        elif hit is not None:
            settle_device(by_model=True)
            reasons.append(
                _reason("match-product_model", "pass", model_fields + ["target.models_sources"],
                        f"Model '{hit}' is listed by a credible source for this recipe.")
            )
        elif custom_firmware:
            reasons.append(
                _reason("identity-custom-firmware", "abstain", model_fields + ["firmware_origin"],
                        "The phone runs custom firmware and no model it reports is in the credible list; a ROM's own model cannot show the recipe is wrong.")
            )
        elif name_hit:
            # A model NAME where the sources list model CODES (Motorola: "motorola edge 30 ultra"
            # against XT2241-1). The device is recognised, the variant is not: ask.
            settle_device(by_model=False)
            ask_or_accept("model-needs-confirmation",
                          "The phone reports a model name where the sources list model codes, so the person holding it is asked.",
                          [{"field": "product_model", "phone_reports": observed_models,
                            "problem": "a model name where the sources list model codes",
                            "sources_list": {src.get("url"): src.get("models") for src in credible if src.get("models")}}])
        else:
            reasons.append(
                _reason("model-mismatch", "fail", model_fields + ["target.models_sources"],
                        f"Fingerprint model '{observed_models[0]}' is not among the models credible sources list for this recipe.")
            )
            identity_mismatch = True
    else:
        fields_consumed.extend(model_fields)
        if device_reason_index is None or name_hit:
            settle_device(by_model=False)
            ask_or_accept("model-needs-confirmation",
                          "No credible source lists model codes for this recipe, so the person holding the phone is asked.",
                          [{"field": "product_model", "phone_reports": observed_models,
                            "problem": "no credible source lists model codes for this recipe"}])

    identity_mismatch = any(r["result"] == "fail" for r in reasons)

    if identity_mismatch:
        return {
            "verdict": "unsafe",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    identity_abstained = any(reason["result"] == "abstain" and reason["code"] not in _PENDING_CODES for reason in reasons)

    if any(reason["result"] == "abstain" for reason in reasons) and "prerequisites" not in recipe:
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    if "prerequisites" not in recipe:
        reasons.append(_reason("prerequisites-unrecorded", "abstain", ["prerequisites"], "Prerequisite consideration is absent from the recipe."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }
    if recipe["prerequisites"] is None:
        reasons.append(_reason("prerequisites-invalid", "abstain", ["prerequisites"], "Prerequisite authoring state is null and cannot be checked."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }
    if not recipe["prerequisites"]:
        reasons.append(_reason("prerequisites-none-declared", "abstain", ["prerequisites"], "The recipe declares no prerequisites, but v0.2 has no proof that the procedure needs none."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    operations = recipe.get("operations")
    if operations is None or len(operations) == 0:
        reasons.append(
            _reason(
                "operations-none-declared",
                "abstain",
                ["operations"],
                "The recipe declares no operations, but v0.2 has no proof that the procedure does nothing.",
            )
        )
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": recipe.get("schema_version")},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    known_op_kinds = _VOCABULARY.get("operation_kinds", {})
    unlock_classes = _VOCABULARY.get("unlock_classes", [])
    unlock_evidence_fields = _VOCABULARY.get("unlock_evidence_fields", {})
    has_unlock_evidence_prereq = any(
        isinstance(req, dict)
        and name in unlock_evidence_fields
        and req.get("required") == unlock_evidence_fields[name]
        and req.get("unlock_class") in unlock_classes
        for name, req in (recipe["prerequisites"] or {}).items()
    ) or any(
        isinstance(req, dict) and name in unlock_evidence_fields and req.get("requirement") == "no_step"
        for name, req in (recipe["prerequisites"] or {}).items()
    )

    for op in operations:
        kind = op.get("kind") if isinstance(op, dict) else None
        if kind not in known_op_kinds:
            reasons.append(
                _reason(
                    "operation-kind-unrecognized",
                    "abstain",
                    ["operations"],
                    f"Operation kind '{kind}' is not recognized in vocabulary.",
                )
            )
        elif known_op_kinds[kind].get("requires_unlock") is True and not has_unlock_evidence_prereq:
            reasons.append(
                _reason(
                    "unlock-undeclared-for-operation",
                    "abstain",
                    ["operations", "prerequisites"],
                    f"Operation '{kind}' requires unlock, but no prerequisite declares an unlock_class.",
                )
            )

    guidance = None
    refused_names = _VOCABULARY.get("refused_prerequisite_names", {})
    allowed_comparisons = _VOCABULARY.get("prerequisite_comparisons", ["equal", "exact_major", "minimum"])

    for name, requirement in recipe["prerequisites"].items():
        if name in refused_names:
            replacement = refused_names[name]
            reasons.append(
                _reason(
                    "prerequisite-name-refused",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' is refused; use '{replacement}' instead.",
                )
            )
            continue

        if isinstance(requirement, dict) and "requirement" in requirement:
            if (
                requirement.get("requirement") == "no_step"
                and name in unlock_evidence_fields
                and requirement.get("source_evidence")
            ):
                reasons.append(
                    _reason(
                        "unlock-no-step-declared",
                        "abstain",
                        ["prerequisites." + name],
                        f"The source declares no unlock step for '{name}'. v0.3 records the claim and does not yet rely on it.",
                    )
                )
            else:
                reasons.append(
                    _reason(
                        "unlock-requirement-unrecognized",
                        "abstain",
                        ["prerequisites." + name],
                        f"Prerequisite '{name}' carries an unrecognized requirement or one without source evidence.",
                    )
                )
            continue

        unlock_class = requirement.get("unlock_class") if isinstance(requirement, dict) else None

        if unlock_class and name not in unlock_evidence_fields:
            reasons.append(
                _reason(
                    "unlock-class-on-non-unlock-field",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' carries unlock_class, but '{name}' is not an unlock evidence field.",
                )
            )
            continue

        is_unlock = _is_unlock_prerequisite(name, requirement)

        if is_unlock and not unlock_class:
            reasons.append(
                _reason(
                    "unlock-class-undeclared",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' is an unlock step but specifies no unlock_class.",
                )
            )
            continue

        if unlock_class == "out_of_band":
            method_name = requirement.get("unlock_method") or recipe.get("install_method")
            method_guidance = get_guidance(method_name)
            if method_guidance:
                guidance = method_guidance
            readback = requirement.get("unlock_readback")
            if readback is None:
                reasons.append(
                    _reason(
                        "unlock-out-of-band",
                        "abstain",
                        ["prerequisites." + name],
                        f"Prerequisite '{name}' requires an out-of-band unlock procedure that cannot be established from device state.",
                    )
                )
                continue
            if readback not in _VOCABULARY.get("unlock_readback_values", []):
                reasons.append(
                    _reason(
                        "unlock-readback-unrecognized",
                        "abstain",
                        ["prerequisites." + name],
                        f"Prerequisite '{name}' has unrecognized unlock_readback: {readback!r}.",
                    )
                )
                continue
            # unlock_readback "device": the unlock happens off the phone, but its result is
            # read back from the phone's own state, so it is compared like any other field.

        if is_unlock and unlock_class not in ("command", "out_of_band"):
            reasons.append(
                _reason(
                    "unlock-class-undeclared",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' has unrecognized unlock_class: {unlock_class!r}.",
                )
            )
            continue

        # Ruled 17 Oct 2026: some makers withdrew every official unlock route. The recipe says so
        # with unlock_route; absent means available. An unknown value is never read as available.
        unlock_route = requirement.get("unlock_route") if isinstance(requirement, dict) else None
        if unlock_route is not None and unlock_route not in _VOCABULARY.get("unlock_route_values", []):
            reasons.append(
                _reason(
                    "unlock-route-unrecognized",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' has unrecognized unlock_route: {unlock_route!r}.",
                )
            )
            continue

        required = requirement.get("required") if isinstance(requirement, dict) else None
        compare = requirement.get("compare") if isinstance(requirement, dict) else None
        is_numeric_or_version_req = _is_numeric_or_version(required)

        if is_numeric_or_version_req and not compare:
            reasons.append(
                _reason(
                    f"prerequisite-{name}-comparison-undeclared",
                    "abstain",
                    [name, "prerequisites." + name],
                    f"Prerequisite '{name}' required value is numeric or version string, but 'compare' is not declared.",
                )
            )
            continue

        if compare and compare not in allowed_comparisons:
            reasons.append(
                _reason(
                    f"prerequisite-{name}-comparison-unrecognized",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' has unrecognized comparison mode: {compare!r}.",
                )
            )
            continue

        if not compare:
            compare = "equal"

        if custom_firmware and name in _VOCABULARY.get("stock_firmware_prerequisites", []):
            # The recipe states what the vendor's firmware must be before installing. A phone
            # already running something else does not report that, whatever it says.
            fields_consumed.append("firmware_origin")
            reasons.append(
                _reason(
                    "firmware-version-custom-rom",
                    "abstain",
                    [name, "firmware_origin", "prerequisites." + name],
                    f"Prerequisite '{name}' is about the vendor's firmware, and this phone runs custom firmware.",
                )
            )
            continue

        observed = fingerprint.get(name)
        fields_consumed.append(name)

        if observed in (None, "", "unknown", "not_applicable"):
            reasons.append(
                _reason(
                    "missing-" + name,
                    "abstain",
                    [name, "prerequisites." + name],
                    "Required prerequisite fingerprint evidence is missing.",
                )
            )
            continue

        if unlock_route == "withdrawn_by_maker" and observed != required:
            # not-ready would say "unlock first", and there is no official way to. A phone that
            # already reports the required state is compared as usual below.
            reasons.append(
                _reason(
                    "unlock-route-withdrawn",
                    "abstain",
                    [name, "prerequisites." + name],
                    f"Prerequisite '{name}' is unmet, and the maker no longer offers an official way to meet it.",
                )
            )
            continue

        if compare == "one_of":
            options = required if isinstance(required, list) else None
            parsed = [_parse_version(o) for o in options] if options else None
            obs_ver = _parse_version(observed)
            if not parsed or any(p is None for p in parsed):
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        ["prerequisites." + name],
                        f"Required values for prerequisite '{name}' must be a list of versions for one_of.",
                    )
                )
            elif obs_ver is None:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        [name],
                        f"Observed value '{observed}' for prerequisite '{name}' cannot be parsed as a version.",
                    )
                )
            elif any(obs_ver[0] == p[0] for p in parsed):
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-confirmed",
                        "pass",
                        [name],
                        "Fingerprint confirms the required prerequisite state.",
                    )
                )
            else:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-mismatch",
                        "unmet",
                        [name],
                        "Fingerprint prerequisite state contradicts the recipe.",
                    )
                )
            continue

        if compare == "exact_major":
            req_ver = _parse_version(required)
            obs_ver = _parse_version(observed)
            if obs_ver is None:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        [name],
                        f"Observed value '{observed}' for prerequisite '{name}' cannot be parsed as a version.",
                    )
                )
            elif req_ver is None:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        ["prerequisites." + name],
                        f"Required value '{required}' for prerequisite '{name}' cannot be parsed as a version.",
                    )
                )
            elif obs_ver[0] == req_ver[0]:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-confirmed",
                        "pass",
                        [name],
                        "Fingerprint confirms the required prerequisite state.",
                    )
                )
            else:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-mismatch",
                        "unmet",
                        [name],
                        "Fingerprint prerequisite state contradicts the recipe.",
                    )
                )
                continue
        elif compare == "minimum":
            req_ver = _parse_version(required)
            obs_ver = _parse_version(observed)
            if obs_ver is None:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        [name],
                        f"Observed value '{observed}' for prerequisite '{name}' cannot be parsed as a version.",
                    )
                )
            elif req_ver is None:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-unparseable",
                        "abstain",
                        ["prerequisites." + name],
                        f"Required value '{required}' for prerequisite '{name}' cannot be parsed as a version.",
                    )
                )
            elif obs_ver >= req_ver:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-confirmed",
                        "pass",
                        [name],
                        "Fingerprint confirms the required prerequisite state.",
                    )
                )
            else:
                reasons.append(
                    _reason(
                        f"prerequisite-{name}-below-minimum",
                        "unmet",
                        [name],
                        "Fingerprint version is below the required minimum.",
                    )
                )
                continue
        else:  # compare == "equal"
            if is_numeric_or_version_req:
                req_ver = _parse_version(required)
                obs_ver = _parse_version(observed)
                if obs_ver is None:
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-unparseable",
                            "abstain",
                            [name],
                            f"Observed value '{observed}' for prerequisite '{name}' cannot be parsed as a version.",
                        )
                    )
                elif req_ver is None:
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-unparseable",
                            "abstain",
                            ["prerequisites." + name],
                            f"Required value '{required}' for prerequisite '{name}' cannot be parsed as a version.",
                        )
                    )
                elif obs_ver == req_ver:
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-confirmed",
                            "pass",
                            [name],
                            "Fingerprint confirms the required prerequisite state.",
                        )
                    )
                else:
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-mismatch",
                            "unmet",
                            [name],
                            "Fingerprint prerequisite state contradicts the recipe.",
                        )
                    )
                    continue
            else:
                if str(observed) == str(required):
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-confirmed",
                            "pass",
                            [name],
                            "Fingerprint confirms the required prerequisite state.",
                        )
                    )
                else:
                    reasons.append(
                        _reason(
                            f"prerequisite-{name}-mismatch",
                            "unmet",
                            [name],
                            "Fingerprint prerequisite state contradicts the recipe.",
                        )
                    )
                    continue

    source = recipe.get("source", {})
    if "untested" in source:
        reasons.append(
            _reason(
                "recipe-untested-legacy-field",
                "abstain",
                ["source.untested"],
                "Recipe carries deprecated source.untested field.",
            )
        )
    elif "upstream_untested" in source:
        upstream_untested = source.get("upstream_untested")
        source_field = "source.upstream_untested"
        if upstream_untested is False or upstream_untested is None or upstream_untested == "unestablished":
            pass
        elif upstream_untested is True or upstream_untested in ("untested", "true", "marked_untested"):
            reasons.append(
                _reason(
                    "recipe-untested-upstream",
                    "abstain",
                    [source_field],
                    "Upstream marked this configuration as untested on physical hardware.",
                )
            )
        else:
            reasons.append(
                _reason(
                    "recipe-untested-unrecognized",
                    "abstain",
                    [source_field],
                    f"Recipe specifies unrecognized upstream_untested value: {upstream_untested!r}.",
                )
            )

    unmet = [reason for reason in reasons if reason["result"] == "unmet"]
    for reason in unmet:
        reason["remedy"] = _remedy(reason, fingerprint, recipe)
    pending = [r for r in reasons if r["result"] == "abstain" and r["code"] in _PENDING_CODES]
    other_abstain = [r for r in reasons if r["result"] == "abstain" and r["code"] not in _PENDING_CODES]
    if pending and not other_abstain:
        # Everything the phone can show fits; the sources cannot settle which device
        # configuration it is. Not ready until the person confirms (evening ruling, 8 Oct).
        verdict = "not-ready"
    elif unmet and not identity_abstained:
        # The recipe fits this phone, and the phone is not in the state it needs yet.
        verdict = "not-ready"
    elif unmet or any(reason["result"] == "abstain" for reason in reasons):
        # Unmet but the phone's identity is not fully confirmed: the recipe may not fit,
        # so the verifier cannot say "not ready". The unmet reason stays in the list.
        verdict = "cannot-verify"
    else:
        verdict = "safe"
    evidence = _build_evidence(fingerprint, fields_consumed)
    if guidance is not None:
        evidence["guidance"] = guidance
    result = {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": {"schema_version": recipe.get("schema_version")},
        "evidence": evidence,
    }
    if verdict == "not-ready" and pending:
        result["pending_confirmation"] = True
    return result




def _remedy(reason, fingerprint, recipe):
    """Plain next step for an unmet prerequisite. Guidance only; never evidence."""
    name = reason["fields"][0] if reason.get("fields") else ""
    requirement = (recipe.get("prerequisites") or {}).get(name) or {}
    required = requirement.get("required") if isinstance(requirement, dict) else None
    observed = (fingerprint or {}).get(name)
    if name == "bootloader_state":
        return ("The bootloader is locked. Unlock it first, which erases everything on the phone, "
                "then read the phone again.")
    if name == "android_version":
        wanted = " or ".join(str(r) for r in required) if isinstance(required, list) else str(required)
        return ("The phone runs Android %s and this recipe needs Android %s. Install that stock version first, "
                "then read the phone again. Going back to an older Android version is not always possible."
                % (observed, wanted))
    return "Change the phone so that %s is %s, then read the phone again." % (name, required)
