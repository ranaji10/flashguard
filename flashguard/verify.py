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


def verify(fingerprint, recipe):
    """Return a verdict for a fingerprint and a validated v0.1 recipe."""
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
