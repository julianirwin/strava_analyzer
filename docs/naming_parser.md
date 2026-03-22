# Naming Parser Rules (v2)

The parser is deterministic and commute-specific.

It parses only bike-like activities whose names match one of these structured schemes:

`Week <week number> Commute <commute number> <am|pm> [labels]`

`Commute <commute number> (Week <week number> / <am|pm> / [labels])`

Examples:
- `Week 44 Commute 245 pm sw`
- `Week 0.5 Commute 3 am sw`
- `Week 8 Commute 38am sw` (lenient: missing space)
- `Commute 9 (Week 2 / AM / Arb)`

## Parse Scope

- Structured parsing runs only for bike-like activity types (`ride`, `bike`, `cycling` family).
- All other names (including Strava defaults and freeform titles) remain unparsed and are treated as generic names.

## Extracted Fields

Backward-compatible existing fields:
- `name_category`: `structured_commute` for parsed commute names, otherwise `general`/`unknown`
- `time_of_day_label`: `morning` for `am`, `evening` for `pm` on parsed commute names
- `name_tag`: parsed label text when available, otherwise original activity name

New commute fields:
- `is_structured_commute` (boolean)
- `commute_week_label` (raw week token, supports decimals like `0.5`)
- `commute_week_number` (float)
- `commute_number` (integer)
- `commute_period` (`am` or `pm`)
- `commute_direction` (`to_work` for `am`, `from_work` for `pm`)
- `commute_label_raw` (raw trailing label text)
- `commute_label_key` (normalized lowercase key for grouping)
- `commute_parse_notes` (nullable notes such as `missing_space_before_period`, `fractional_week`)
