from __future__ import annotations

import re

_TIME_PATTERNS = {
    "morning": re.compile(r"\bmorning\b", re.IGNORECASE),
    "afternoon": re.compile(r"\bafternoon\b", re.IGNORECASE),
    "evening": re.compile(r"\bevening\b", re.IGNORECASE),
    "lunch": re.compile(r"\blunch\b", re.IGNORECASE),
}

_REMOVE_TOKENS = re.compile(
    r"\b(morning|afternoon|evening|lunch|ride|run|ski|nordic|activity|commute)\b",
    re.IGNORECASE,
)


def parse_activity_name(name: str | None) -> dict[str, str | None]:
    raw = (name or "").strip()
    lowered = raw.lower()

    time_of_day = None
    for label, pattern in _TIME_PATTERNS.items():
        if pattern.search(raw):
            time_of_day = label
            break

    if lowered.startswith("week"):
        category = "week_plan"
    elif lowered.startswith("commute") or "commute" in lowered:
        category = "commute"
    elif any(token in raw for token in ["Ride", "Run", "Ski"]):
        category = "sport_labeled"
    elif raw:
        category = "general"
    else:
        category = "unknown"

    tag = _REMOVE_TOKENS.sub("", raw)
    tag = re.sub(r"\s+", " ", tag).strip(" -_,")
    if not tag:
        tag = raw

    return {
        "name_category": category,
        "time_of_day_label": time_of_day,
        "name_tag": tag or None,
    }
