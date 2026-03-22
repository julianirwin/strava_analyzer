# Naming Parser Rules (v1)

The parser is intentionally deterministic and hardcoded.

Extracted fields:
- `time_of_day_label`: inferred from presence of `morning`, `afternoon`, `evening`, `lunch`.
- `name_category`:
  - names starting with `Commute` or containing `commute` -> `commute`
  - names starting with `Week` -> `week_plan`
  - names containing `Ride`/`Run`/`Ski` -> `sport_labeled`
  - otherwise -> `general`
- `name_tag`: original name with detected time-of-day and generic sport words removed, trimmed.

Fallback: if parsing finds no meaningful tokens, `name_tag` falls back to original `Activity Name`.
