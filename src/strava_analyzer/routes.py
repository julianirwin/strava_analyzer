from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from fitparse import FitFile
except Exception:  # pragma: no cover
    FitFile = None


RouteSummary = dict[str, float | int | str | None]


def _empty_summary() -> RouteSummary:
    return {
        "route_point_count": 0,
        "route_start_lat": None,
        "route_start_lon": None,
        "route_end_lat": None,
        "route_end_lon": None,
        "route_bbox_min_lat": None,
        "route_bbox_max_lat": None,
        "route_bbox_min_lon": None,
        "route_bbox_max_lon": None,
        "route_polyline_hint": None,
    }


def _polyline_hint(points: list[tuple[float, float]]) -> str | None:
    if not points:
        return None
    if len(points) == 1:
        chosen = [points[0]]
    elif len(points) == 2:
        chosen = [points[0], points[1]]
    else:
        chosen = [points[0], points[len(points) // 2], points[-1]]
    return " | ".join(f"{lat:.5f},{lon:.5f}" for lat, lon in chosen)


def _finalize(points: list[tuple[float, float]]) -> RouteSummary:
    summary = _empty_summary()
    if not points:
        return summary

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]

    summary.update(
        {
            "route_point_count": len(points),
            "route_start_lat": points[0][0],
            "route_start_lon": points[0][1],
            "route_end_lat": points[-1][0],
            "route_end_lon": points[-1][1],
            "route_bbox_min_lat": min(lats),
            "route_bbox_max_lat": max(lats),
            "route_bbox_min_lon": min(lons),
            "route_bbox_max_lon": max(lons),
            "route_polyline_hint": _polyline_hint(points),
        }
    )
    return summary


def _parse_gpx(path: Path) -> list[tuple[float, float]]:
    tree = ET.parse(path)
    root = tree.getroot()
    points: list[tuple[float, float]] = []
    for elem in root.iter():
        if elem.tag.endswith("trkpt"):
            lat = elem.attrib.get("lat")
            lon = elem.attrib.get("lon")
            if lat is None or lon is None:
                continue
            points.append((float(lat), float(lon)))
    return points


def _parse_fit(path: Path) -> list[tuple[float, float]]:
    if FitFile is None:
        return []

    points: list[tuple[float, float]] = []
    fit = FitFile(path)
    for record in fit.get_messages("record"):
        fields = {field.name: field.value for field in record}
        lat = fields.get("position_lat")
        lon = fields.get("position_long")
        if lat is None or lon is None:
            continue
        points.append((float(lat), float(lon)))
    return points


def summarize_route_file(path: Path) -> RouteSummary:
    if not path.exists():
        return _empty_summary()

    ext = path.suffix.lower()
    try:
        if ext == ".gpx":
            points = _parse_gpx(path)
        elif ext == ".fit":
            points = _parse_fit(path)
        else:
            points = []
    except Exception:
        points = []

    return _finalize(points)
