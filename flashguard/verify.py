"""Pure v0.1 recipe verification."""


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
    required = ("schema_version", "recipe_id", "target", "assets", "operations")
    missing = [key for key in required if key not in recipe]
    if missing:
        return "Invalid recipe: missing required field(s): " + ", ".join(missing) + "."
    if recipe.get("schema_version") != "0.1":
        return "Invalid recipe: unsupported schema_version."
    target = recipe.get("target")
    if not isinstance(target, dict):
        return "Invalid recipe: target must be an object."
    target_fields = ("product_device", "variant", "partition_scheme")
    if any(field not in target for field in target_fields):
        return "Invalid recipe: target is missing a required field."
    assets = recipe.get("assets")
    operations = recipe.get("operations")
    if not isinstance(assets, list) or not isinstance(operations, list):
        return "Invalid recipe: assets and operations must be arrays."
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
