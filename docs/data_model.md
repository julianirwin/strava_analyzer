# Catalog Data Model

Primary table: `activities`

Key fields:
- `activity_id`: Strava activity identifier
- `activity_datetime`: parsed timestamp
- `activity_type`: Run/Ride/Ski/etc
- `distance_m`: distance in meters
- `elapsed_time_s`: elapsed seconds
- `moving_time_s`: moving seconds
- `elevation_gain_m`: elevation gain in meters
- `equipment_name`: activity gear label from Strava export
- `equipment_type`: inferred `bike`/`shoe`/`unknown`
- `name_category`: parser-derived category
- `time_of_day_label`: parser-derived morning/afternoon/evening/lunch
- `name_tag`: parser-derived freeform residual tag
- `route_file`: relative route filename
- `route_point_count`: number of points in route file
- `route_start_lat`/`route_start_lon`: start coordinate
- `route_end_lat`/`route_end_lon`: end coordinate
- `route_bbox_min_lat`/`route_bbox_max_lat`/`route_bbox_min_lon`/`route_bbox_max_lon`
- `route_polyline_hint`: compact 3-point coarse geometry hint
