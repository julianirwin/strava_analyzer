from strava_analyzer.naming import parse_activity_name


def test_parse_activity_name_structured_commute_exact() -> None:
    out = parse_activity_name("Week 44 Commute 245 pm sw", "Ride")
    assert out["is_structured_commute"] is True
    assert out["commute_week_number"] == 44.0
    assert out["commute_number"] == 245
    assert out["commute_period"] == "pm"
    assert out["commute_direction"] == "from_work"
    assert out["commute_label_key"] == "sw"


def test_parse_activity_name_lenient_variants() -> None:
    out = parse_activity_name("Week 0.5 Commute 38am SW", "ride")
    assert out["is_structured_commute"] is True
    assert out["commute_week_number"] == 0.5
    assert out["commute_period"] == "am"
    assert "fractional_week" in (out["commute_parse_notes"] or "")
    assert "missing_space_before_period" in (out["commute_parse_notes"] or "")


def test_parse_activity_name_2024_parenthesized_format() -> None:
    out = parse_activity_name("Commute 9 (Week 2 / AM / Arb)", "Ride")
    assert out["is_structured_commute"] is True
    assert out["commute_week_number"] == 2.0
    assert out["commute_number"] == 9
    assert out["commute_period"] == "am"
    assert out["commute_direction"] == "to_work"
    assert out["commute_label_raw"] == "Arb"
    assert out["commute_label_key"] == "arb"
    assert "legacy_parenthesized_format" in (out["commute_parse_notes"] or "")


def test_parse_activity_name_2024_parenthesized_without_slashes() -> None:
    out = parse_activity_name("Commute 10 (Week 3 AM Arb)", "Ride")
    assert out["is_structured_commute"] is True
    assert out["commute_week_number"] == 3.0
    assert out["commute_number"] == 10
    assert out["commute_period"] == "am"
    assert out["commute_label_raw"] == "Arb"
    assert out["commute_label_key"] == "arb"


def test_parse_activity_name_requires_bike_type() -> None:
    out = parse_activity_name("Week 44 Commute 245 pm sw", "Run")
    assert out["is_structured_commute"] is False
    assert out["name_category"] == "general"


def test_parse_activity_name_non_structured_defaults_to_general() -> None:
    out = parse_activity_name("Morning Ride", "Ride")
    assert out["is_structured_commute"] is False
    assert out["name_category"] == "general"
    assert out["time_of_day_label"] is None
