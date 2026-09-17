"""Pure v0.1 and v0.2 recipe verification."""

import json
import pathlib
import re

from flashguard.guidance import get_guidance

_VOCABULARY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "vocabulary.json"


def _load_vocabulary():
    if _VOCABULARY_PATH.is_file():
        with open(_VOCABULARY_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "operation_kinds": {
            "write-image": {"requires_unlock": True},
            "boot-recovery": {"requires_unlock": True},
            "unlock_bootloader": {"requires_unlock": True},
            "unlock": {"requires_unlock": True},
        },
        "unlock_classes": ["command", "out_of_band"],
        "refused_prerequisite_names": {"bootloader_unlocked": "bootloader_state"},
        "prerequisite_comparisons": ["equal", "exact_major", "minimum"],
    }


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
    if recipe.get("schema_version") != "0.1":
        if recipe.get("schema_version") != "0.2":
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
    if recipe.get("schema_version") == "0.2":
        required_v2 = ("source", "install_method", "source_fields_unused")
        if any(key not in recipe for key in required_v2):
            return "Invalid recipe: v0.2 is missing a required field."
        if not isinstance(recipe["source"], dict) or not isinstance(recipe["source_fields_unused"], list):
            return "Invalid recipe: v0.2 source and source_fields_unused are invalid."
        absent = object()
        prerequisites = recipe.get("prerequisites", absent)
        if prerequisites is not absent and prerequisites is not None and not isinstance(prerequisites, dict):
            return "Invalid recipe: prerequisites must be an object, null, or absent."
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
    """Return a verdict for a fingerprint and a validated recipe."""
    invalid = _validate_recipe(recipe)
    if invalid:
        return _invalid_recipe_reason(invalid, fingerprint)

    if recipe.get("schema_version") == "0.2":
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
    if fingerprint is None:
        fingerprint = {}
    reasons = []
    target = recipe["target"]
    fields_consumed = []
    identity_mismatch = False
    supported_aliases = target.get("supported_device_codes", [])

    observed_device = fingerprint.get("product_device")
    fields_consumed.append("product_device")
    expected_device = target.get("product_device")

    if observed_device in (None, "", "unknown", "not_applicable"):
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
        reasons.append(
            _reason("device-mismatch", "fail", ["product_device", "target.product_device"], "Fingerprint value contradicts the recipe target.")
        )
        identity_mismatch = True

    observed_scheme = fingerprint.get("partition_scheme")
    fields_consumed.append("partition_scheme")
    expected_scheme = target.get("partition_scheme")

    if observed_scheme in (None, "", "unknown", "not_applicable"):
        reasons.append(
            _reason("missing-partition_scheme", "abstain", ["partition_scheme"], "Required fingerprint evidence is absent or unknown.")
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

    # Hardware model matching against allowlist
    # The previous DISPUTED marker asked whether an alias hit in supported_device_codes could
    # confirm a variant. That question no longer needs asking: hardware identity is confirmed
    # directly by checking product_model against target.models. Ruled by Ranaji on 16 September
    # on the evidence in docs/Research/variant-danger-findings.md.
    observed_model = fingerprint.get("product_model")
    target_models = target.get("models")

    if "models" not in target or target_models is None or not isinstance(target_models, list) or len(target_models) == 0:
        reasons.append(
            _reason("models-unestablished", "abstain", ["target.models"], "Recipe model coverage is unestablished.")
        )
    elif observed_model in (None, "", "unknown", "not_applicable"):
        fields_consumed.append("product_model")
        reasons.append(
            _reason("missing-product_model", "abstain", ["product_model", "target.models"], "Target product_model is unconfirmed from fingerprint.")
        )
    elif observed_model not in target_models:
        fields_consumed.append("product_model")
        reasons.append(
            _reason("model-mismatch", "fail", ["product_model", "target.models"], f"Fingerprint model '{observed_model}' contradicts the recipe target models.")
        )
        identity_mismatch = True
    else:
        fields_consumed.append("product_model")
        reasons.append(
            _reason("match-product_model", "pass", ["product_model", "target.models"], f"Fingerprint model '{observed_model}' matches recipe target models.")
        )

    if identity_mismatch:
        return {
            "verdict": "unsafe",
            "reasons": reasons,
            "coverage": {"schema_version": "0.2"},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    if any(reason["result"] == "abstain" for reason in reasons) and "prerequisites" not in recipe:
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": "0.2"},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    if "prerequisites" not in recipe:
        reasons.append(_reason("prerequisites-unrecorded", "abstain", ["prerequisites"], "Prerequisite consideration is absent from the recipe."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": "0.2"},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }
    if recipe["prerequisites"] is None:
        reasons.append(_reason("prerequisites-invalid", "abstain", ["prerequisites"], "Prerequisite authoring state is null and cannot be checked."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": "0.2"},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }
    if not recipe["prerequisites"]:
        reasons.append(_reason("prerequisites-none-declared", "abstain", ["prerequisites"], "The recipe declares no prerequisites, but v0.2 has no proof that the procedure needs none."))
        return {
            "verdict": "cannot-verify",
            "reasons": reasons,
            "coverage": {"schema_version": "0.2"},
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
            "coverage": {"schema_version": "0.2"},
            "evidence": _build_evidence(fingerprint, fields_consumed),
        }

    known_op_kinds = _VOCABULARY.get("operation_kinds", {})
    unlock_classes = _VOCABULARY.get("unlock_classes", [])
    has_unlock_class_prereq = any(
        isinstance(req, dict) and req.get("unlock_class") in unlock_classes
        for req in (recipe["prerequisites"] or {}).values()
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
        elif known_op_kinds[kind].get("requires_unlock") is True and not has_unlock_class_prereq:
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

        is_unlock = _is_unlock_prerequisite(name, requirement)
        unlock_class = requirement.get("unlock_class") if isinstance(requirement, dict) else None

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
            reasons.append(
                _reason(
                    "unlock-out-of-band",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' requires an out-of-band unlock procedure that cannot be established from device state.",
                )
            )
            continue

        if is_unlock and unlock_class != "command":
            reasons.append(
                _reason(
                    "unlock-class-undeclared",
                    "abstain",
                    ["prerequisites." + name],
                    f"Prerequisite '{name}' has unrecognized unlock_class: {unlock_class!r}.",
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
                        "fail",
                        [name],
                        "Fingerprint prerequisite state contradicts the recipe.",
                    )
                )
                return {
                    "verdict": "unsafe",
                    "reasons": reasons,
                    "coverage": {"schema_version": "0.2"},
                    "evidence": _build_evidence(fingerprint, fields_consumed),
                }
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
                        "fail",
                        [name],
                        "Fingerprint version is below the required minimum.",
                    )
                )
                return {
                    "verdict": "unsafe",
                    "reasons": reasons,
                    "coverage": {"schema_version": "0.2"},
                    "evidence": _build_evidence(fingerprint, fields_consumed),
                }
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
                            "fail",
                            [name],
                            "Fingerprint prerequisite state contradicts the recipe.",
                        )
                    )
                    return {
                        "verdict": "unsafe",
                        "reasons": reasons,
                        "coverage": {"schema_version": "0.2"},
                        "evidence": _build_evidence(fingerprint, fields_consumed),
                    }
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
                            "fail",
                            [name],
                            "Fingerprint prerequisite state contradicts the recipe.",
                        )
                    )
                    return {
                        "verdict": "unsafe",
                        "reasons": reasons,
                        "coverage": {"schema_version": "0.2"},
                        "evidence": _build_evidence(fingerprint, fields_consumed),
                    }

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

    verdict = "cannot-verify" if any(reason["result"] == "abstain" for reason in reasons) else "safe"
    evidence = _build_evidence(fingerprint, fields_consumed)
    if guidance is not None:
        evidence["guidance"] = guidance
    return {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": {"schema_version": "0.2"},
        "evidence": evidence,
    }


