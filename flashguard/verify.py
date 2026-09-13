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
    if recipe.get("schema_version") == "0.1":
        target_fields = target_fields + ("variant",)
    if any(field not in target for field in target_fields):
        return "Invalid recipe: target is missing a required field."
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
    """Return a verdict for a fingerprint and a validated recipe."""
    invalid = _validate_recipe(recipe)
    if invalid:
        return _invalid_recipe_reason(invalid, fingerprint)

    if recipe.get("schema_version") == "0.2":
        return _verify_v2(fingerprint, recipe)

    reasons = []
    unsafe = False
    abstained = False
    target = recipe.get("target", {})
    fields_consumed = []

    for fingerprint_key, target_path, code in _FINGERPRINT_FIELDS:
        expected = target.get(fingerprint_key)
        observed = fingerprint.get(fingerprint_key)
        fields_consumed.append(fingerprint_key)
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

    return {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": coverage,
        "evidence": _build_evidence(fingerprint, fields_consumed),
    }


def _verify_v2(fingerprint, recipe):
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

    if "variant" in target:
        observed_variant = fingerprint.get("variant")
        fields_consumed.append("variant")
        expected_variant = target.get("variant")

        if observed_variant in (None, "", "unknown", "not_applicable"):
            # An unconfirmed variant ALWAYS abstains, alias or no alias.
            #
            # This branch used to be a bare `pass` when the device code appeared in
            # supported_device_codes, which recorded no reason at all -- so an unknown
            # variant contributed nothing, everything else passed, and the verdict came out
            # SAFE while fields_consumed still claimed the variant had been consumed. An
            # auditor reading the evidence would have believed it was checked. That is the
            # tier-3 case the contract says can never be safe, reached silently.
            #
            # supported_device_codes asserts something about the DEVICE CODE, not about the
            # variant. Whether it is a variant-level or a family-level claim is unsettled,
            # and while it is unsettled the answer is to abstain rather than to assume the
            # generous reading.
            #
            # DISPUTED: is `supported_device_codes` a variant-level or a family-level claim?
            #   position A: variant-level -- upstream lists the exact codes a recipe covers,
            #               so an alias hit is as strong as an exact variant match.
            #   position B: family-level -- hero2lte and hero2ltexx share a base code and
            #               differ in radio hardware, so an alias hit says nothing about the
            #               variant and a wrong flash can cost the modem.
            #   settles it: no test can. It needs a reading of what upstream MEANS by the
            #               field, which is a question for the OpenAndroidInstaller
            #               maintainers, not for us.
            alias_note = (" The device code is a declared alias, which does not confirm the"
                          " variant.") if observed_device in supported_aliases else ""
            reasons.append(
                _reason("missing-variant", "abstain", ["variant", "target.variant"],
                        "Target variant is unconfirmed." + alias_note)
            )
        elif observed_variant == expected_variant:
            # ONE explicit, variant-specific field. Nothing else counts.
            #
            # This used to also accept identity_source in ("tester_identified", ...), which
            # is a REAL schema field carried by 8 of the 10 records in the matrix and set
            # whenever a tester names the device at capture time. It says the tester named
            # the DEVICE. It says nothing about the variant. Reading it as variant
            # confirmation meant almost every real record silently upgraded itself to
            # "human-confirmed" without any human confirming a variant -- wiring the exact
            # limitation recorded in the tracker (a tester who says A5 about an A3) directly
            # into the path to `safe`.
            #
            # variant_source and human_confirmed were invented here and appear in no schema.
            # There is one field now, it is defined in data/schema.md, and its absence means
            # no confirmation rather than an unknown one.
            if "variant_confirmed_by" in fingerprint:
                fields_consumed.append("variant_confirmed_by")
            is_human = fingerprint.get("variant_confirmed_by") == "human"
            if is_human:
                reasons.append(
                    _reason(
                        "match-variant-human-confirmed",
                        "pass",
                        ["variant", "target.variant", "variant_confirmed_by"],
                        f"Fingerprint variant matches recipe target (human-supplied confirmation: {observed_variant}).",
                    )
                )
            else:
                reasons.append(
                    _reason("match-variant", "pass", ["variant", "target.variant"], "Fingerprint variant matches recipe target.")
                )
        elif observed_variant in supported_aliases:
            reasons.append(
                _reason("match-device-alias", "pass", ["variant", "target.supported_device_codes"], f"Device code matches supported alias '{observed_variant}'.")
            )
        else:
            reasons.append(
                _reason("variant-mismatch", "fail", ["variant", "target.variant"], "Fingerprint variant contradicts the recipe target.")
            )
            identity_mismatch = True

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

    for name, requirement in recipe["prerequisites"].items():
        observed = fingerprint.get(name)
        fields_consumed.append(name)
        required = requirement.get("required")
        if observed in (None, "", "unknown", "not_applicable"):
            reasons.append(_reason("missing-" + name, "abstain", [name, "prerequisites." + name], "Required prerequisite fingerprint evidence is missing."))
        elif isinstance(required, (int, float)) and isinstance(observed, (int, float)) and observed < required:
            reasons.append(_reason("prerequisite-" + name + "-below-minimum", "fail", [name], "Fingerprint version is below the required minimum."))
            return {
                "verdict": "unsafe",
                "reasons": reasons,
                "coverage": {"schema_version": "0.2"},
                "evidence": _build_evidence(fingerprint, fields_consumed),
            }
        elif observed != required:
            reasons.append(_reason("prerequisite-" + name + "-mismatch", "fail", [name], "Fingerprint prerequisite state contradicts the recipe."))
            return {
                "verdict": "unsafe",
                "reasons": reasons,
                "coverage": {"schema_version": "0.2"},
                "evidence": _build_evidence(fingerprint, fields_consumed),
            }
        else:
            reasons.append(_reason("prerequisite-" + name + "-confirmed", "pass", [name], "Fingerprint confirms the required prerequisite state."))

    verdict = "cannot-verify" if any(reason["result"] == "abstain" for reason in reasons) else "safe"
    return {
        "verdict": verdict,
        "reasons": reasons,
        "coverage": {"schema_version": "0.2"},
        "evidence": _build_evidence(fingerprint, fields_consumed),
    }

