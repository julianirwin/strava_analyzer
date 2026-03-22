# Catalog Data Model

Primary table: `activities`

Key core fields:
- `activity_id`: Strava activity identifier
- `activity_datetime`: parsed timestamp
- `activity_type`: Run/Ride/Ski/etc
- `distance_m`: distance in meters
- `elapsed_time_s`: elapsed seconds
- `moving_time_s`: moving seconds
- `average_speed_mps`: speed value from export when present
- `elevation_gain_m`: elevation gain in meters
- `equipment_name`: activity gear label from Strava export
- `equipment_type`: inferred `bike`/`shoe`/`unknown`

Name parsing fields:
- `name_category`
- `time_of_day_label`
- `name_tag`

Commute-specific fields:
- `is_structured_commute`
- `commute_week_label`
- `commute_week_number`
- `commute_number`
- `commute_period`
- `commute_direction`
- `commute_label_raw`
- `commute_label_key`
- `commute_parse_notes`

Route summary fields:
- `route_file`
- `route_point_count`
- `route_start_lat`/`route_start_lon`
- `route_end_lat`/`route_end_lon`
- `route_bbox_min_lat`/`route_bbox_max_lat`/`route_bbox_min_lon`/`route_bbox_max_lon`
- `route_polyline_hint`

Compatibility note:
- Existing name fields are retained for notebook compatibility.
- Structured parsing is intentionally limited to commute-pattern bike activities.
