"""Pure v0.1 and v0.2 recipe verification."""


_FINGERPRINT_FIELDS = (
    ("product_device", "target.product_device", "device-mismatch"),
    ("variant", "target.variant", "variant-mismatch"),
    ("partition_scheme", "target.partition_scheme", "partition-scheme-mismatch"),
)


def _reason(code, result, fields, message):
    return {
        "code": code,
        "result": result,
        "fields": list(fields),
        "message": message,
    }


def _invalid_recipe_reason(message):
    return {
        "verdict": "cannot-verify",
        "reasons": [_reason("invalid-recipe", "abstain", ["recipe"], message)],
        "coverage": {"schema_version": None, "modelled_operations": [], "safe_case_available": False},
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
    if recipe.get("schema_version") == "0.1":
        target_fields = target_fields + ("variant",)
    if any(field not in target for field in target_fields):
        return "Invalid recipe: target is missing a required field."
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
        if any(field not in asset for field in ("asset_id", "role", "product_device", "variant")):
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
    """Return a verdict for a fingerprint and a validated v0.1 recipe."""
    invalid = _validate_recipe(recipe)
    if invalid:
        return _invalid_recipe_reason(invalid)

    if recipe.get("schema_version") == "0.2":
        return _verify_v2(fingerprint, recipe)

    reasons = []
    unsafe = False
    abstained = False
    target = recipe.get("target", {})

    for fingerprint_key, target_path, code in _FINGERPRINT_FIELDS:
        expected = target.get(fingerprint_key)
        observed = fingerprint.get(fingerprint_key)
        fields = [fingerprint_key, target_path]
        if observed in (None, "", "unknown", "not_applicable"):
            abstained = True
            reasons.append(
                _reason(
                    "missing-" + fingerprint_key,
                    "abstain",
                    fields,
                    "Required fingerprint evidence is absent or unknown.",
                )
            )
        elif observed != expected:
            unsafe = True
            reasons.append(
                _reason(
                    code,
                    "fail",
                    fields,
                    "Fingerprint value contradicts the recipe target.",
                )
            )
        else:
            reasons.append(
                _reason(
                    "match-" + fingerprint_key,
                    "pass",
                    fields,
                    "Fingerprint value matches the recipe target.",
                )
            )

    for asset in recipe.get("assets", []):
        asset_id = asset.get("asset_id", "")
        for key in ("product_device", "variant"):
            if asset.get(key) != target.get(key):
                unsafe = True
                reasons.append(
                    _reason(
                        "asset-" + key + "-mismatch",
                        "fail",
                        ["assets." + asset_id + "." + key, "target." + key],
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

    return {"verdict": verdict, "reasons": reasons, "coverage": coverage}


def _verify_v2(fingerprint, recipe):
    reasons = []
    target = recipe["target"]
    identity_mismatch = False
    for key, code in (("product_device", "device-mismatch"), ("partition_scheme", "partition-scheme-mismatch")):
        observed = fingerprint.get(key)
        expected = target[key]
        if observed in (None, "", "unknown", "not_applicable"):
            reasons.append(_reason("missing-" + key, "abstain", [key], "Required fingerprint evidence is absent or unknown."))
        elif observed != expected:
            reasons.append(_reason(code, "fail", [key, "target." + key], "Fingerprint value contradicts the recipe target."))
            identity_mismatch = True
        else:
            reasons.append(_reason("match-" + key, "pass", [key, "target." + key], "Fingerprint value matches the recipe target."))
    if identity_mismatch:
        return {"verdict": "unsafe", "reasons": reasons, "coverage": {"schema_version": "0.2"}}
    if any(reason["result"] == "abstain" for reason in reasons) and "prerequisites" not in recipe:
        return {"verdict": "cannot-verify", "reasons": reasons, "coverage": {"schema_version": "0.2"}}

    if "prerequisites" not in recipe:
        reasons.append(_reason("prerequisites-unrecorded", "abstain", ["prerequisites"], "Prerequisite consideration is absent from the recipe."))
        return {"verdict": "cannot-verify", "reasons": reasons, "coverage": {"schema_version": "0.2"}}
    if recipe["prerequisites"] is None:
        reasons.append(_reason("prerequisites-invalid", "abstain", ["prerequisites"], "Prerequisite authoring state is null and cannot be checked."))
        return {"verdict": "cannot-verify", "reasons": reasons, "coverage": {"schema_version": "0.2"}}
    if not recipe["prerequisites"]:
        reasons.append(_reason("prerequisites-none-declared", "abstain", ["prerequisites"], "The recipe declares no prerequisites, but v0.2 has no proof that the procedure needs none."))
        return {"verdict": "cannot-verify", "reasons": reasons, "coverage": {"schema_version": "0.2"}}

    for name, requirement in recipe["prerequisites"].items():
        observed = fingerprint.get(name)
        required = requirement.get("required")
        if observed in (None, "", "unknown", "not_applicable"):
            reasons.append(_reason("missing-" + name, "abstain", [name, "prerequisites." + name], "Required prerequisite fingerprint evidence is missing."))
        elif isinstance(required, (int, float)) and isinstance(observed, (int, float)) and observed < required:
            reasons.append(_reason("prerequisite-" + name + "-below-minimum", "fail", [name], "Fingerprint version is below the required minimum."))
            return {"verdict": "unsafe", "reasons": reasons, "coverage": {"schema_version": "0.2"}}
        elif observed != required:
            reasons.append(_reason("prerequisite-" + name + "-mismatch", "fail", [name], "Fingerprint prerequisite state contradicts the recipe."))
            return {"verdict": "unsafe", "reasons": reasons, "coverage": {"schema_version": "0.2"}}
        else:
            reasons.append(_reason("prerequisite-" + name + "-confirmed", "pass", [name], "Fingerprint confirms the required prerequisite state."))
    verdict = "cannot-verify" if any(reason["result"] == "abstain" for reason in reasons) else "safe"
    return {"verdict": verdict, "reasons": reasons, "coverage": {"schema_version": "0.2"}}
