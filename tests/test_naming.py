from strava_analyzer.naming import parse_activity_name


def test_parse_activity_name_time_and_category() -> None:
    out = parse_activity_name("Morning Ride")
    assert out["time_of_day_label"] == "morning"
    assert out["name_category"] == "sport_labeled"


def test_parse_activity_name_week_plan() -> None:
    out = parse_activity_name("Week 8 Long Run")
    assert out["name_category"] == "week_plan"
