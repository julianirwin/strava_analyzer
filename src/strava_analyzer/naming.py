from __future__ import annotations

import re

_COMMUTE_PATTERN = re.compile(
    r"^\s*week\s+(?P<week>\d+(?:\.\d+)?)\s+commute\s+(?P<number>\d+)(?P<sep>\s*)(?P<period>am|pm)\b(?:\s+(?P<labels>.*?))?\s*$",
    re.IGNORECASE,
)
_COMMUTE_PATTERN_2024 = re.compile(
    r"^\s*commute\s+(?P<number>\d+)\s*\(\s*week\s+"
    r"(?P<week>\d+(?:\.\d+)?)\s*(?:/\s*)?(?P<period>am|pm)"
    r"(?:\s*(?:/\s*)?(?P<labels>[^)]*?))?\s*\)\s*$",
    re.IGNORECASE,
)

_LABEL_KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def _is_bike_like(activity_type: str | None) -> bool:
    lowered = (activity_type or "").strip().lower()
    return any(token in lowered for token in ["ride", "bike", "cycling"])


def _normalize_label_key(label: str | None) -> str | None:
    if not label:
        return None
    normalized = _LABEL_KEY_PATTERN.sub("_", label.lower()).strip("_")
    return normalized or None


def _empty_commute_fields() -> dict[str, object]:
    return {
        "is_structured_commute": False,
        "commute_week_label": None,
        "commute_week_number": None,
        "commute_number": None,
        "commute_period": None,
        "commute_direction": None,
        "commute_label_raw": None,
        "commute_label_key": None,
        "commute_parse_notes": None,
    }


def parse_activity_name(name: str | None, activity_type: str | None = None) -> dict[str, object]:
    raw = (name or "").strip()
    out: dict[str, object] = {
        "name_category": "general" if raw else "unknown",
        "time_of_day_label": None,
        "name_tag": raw or None,
    }
    out.update(_empty_commute_fields())

    if not raw or not _is_bike_like(activity_type):
        return out

    match = _COMMUTE_PATTERN.match(raw)
    style = "week_prefix"
    if not match:
        match = _COMMUTE_PATTERN_2024.match(raw)
        style = "legacy_parenthesized"
    if not match:
        return out

    week_label = match.group("week")
    commute_number = int(match.group("number"))
    period = match.group("period").lower()
    labels = (match.group("labels") or "").strip()

    notes: list[str] = []
    sep = match.groupdict().get("sep")
    if sep == "":
        notes.append("missing_space_before_period")
    if "." in week_label:
        notes.append("fractional_week")
    if style == "legacy_parenthesized":
        notes.append("legacy_parenthesized_format")

    direction = "to_work" if period == "am" else "from_work"
    time_of_day = "morning" if period == "am" else "evening"

    out.update(
        {
            "name_category": "structured_commute",
            "time_of_day_label": time_of_day,
            "name_tag": labels or raw,
            "is_structured_commute": True,
            "commute_week_label": week_label,
            "commute_week_number": float(week_label),
            "commute_number": commute_number,
            "commute_period": period,
            "commute_direction": direction,
            "commute_label_raw": labels or None,
            "commute_label_key": _normalize_label_key(labels),
            "commute_parse_notes": ";".join(notes) if notes else None,
        }
    )
    return out
