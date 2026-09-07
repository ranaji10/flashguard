"""Classify prerequisite evidence in one supplied upstream config."""

import re


def _has_key(text, pattern):
    return re.search(pattern, text, re.MULTILINE) is not None


def _prose_unlock(text):
    return re.search(
        r"\b(unlock(ed|ing)?|must unlock|bootloader (must|should|needs|required))\b",
        text,
        re.IGNORECASE,
    ) is not None


def _prose_partition(text):
    return re.search(r"\b(A/B|single[- ]slot|inactive slot|active slot)\b", text, re.IGNORECASE) is not None


def survey_text(text, source):
    """Return evidence classes for one config's text and declared source format."""
    if source == "yaml":
        source = "openandroidinstaller"
    if source == "openandroidinstaller":
        unlock_structured = _has_key(
            text, r"^(?:\s*)(unlock_bootloader|bootloader_state|unlockable):"
        )
        partition_structured = _has_key(
            text, r"^(?:\s*)(is_ab_device|partition_scheme|partition_layout):"
        )
        identity_structured = _has_key(
            text, r"^(?:\s*)(device_code|supported_device_codes|device_name|codename):"
        )
    elif source == "postmarketos":
        unlock_structured = _has_key(
            text, r"^deviceinfo_[A-Za-z0-9_]*(unlock|bootloader)[A-Za-z0-9_]*="
        )
        partition_structured = _has_key(
            text, r"^deviceinfo_(partition_type|super_partitions)="
        )
        identity_structured = _has_key(
            text, r"^deviceinfo_(codename|name|manufacturer)="
        )
    elif source == "lineage_metadata":
        unlock_structured = _has_key(
            text, r"^(?:\s*)(custom_unlock_cmd|bootloader_state|unlockable):"
        )
        partition_structured = _has_key(
            text, r"^(?:\s*)(is_ab_device|partition_scheme|partition_layout):"
        )
        identity_structured = _has_key(
            text, r"^(?:\s*)(codename|name|vendor|device):"
        )
    elif source == "lineage_prose":
        unlock_structured = False
        partition_structured = False
        identity_structured = False
    else:
        raise ValueError("unknown source format: %s" % source)

    prose_allowed = source != "lineage_metadata"
    unlock = "structured" if unlock_structured else "prose-only" if prose_allowed and _prose_unlock(text) else "none"
    partition = "structured" if partition_structured else "prose-only" if prose_allowed and _prose_partition(text) else "none"
    identity = "structured" if identity_structured else "prose-only" if prose_allowed and re.search(
        r"\b(device|model|codename|phone|tablet)\b", text, re.IGNORECASE
    ) else "none"
    return {
        "unlock": unlock,
        "partition_scheme": partition,
        "identity": identity,
    }