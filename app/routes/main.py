# app/routes/main.py
from __future__ import annotations

from flask import Blueprint, Response, current_app, render_template, request

from app.services.gpx import GpxPoint, build_content_disposition, build_gpx_xml

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return render_template("index.html")

@main_bp.post("/directions")
def directions():
    origin = request.form.get("origin", "").strip()
    distance = request.form.get("distance", "20-30")
    road_type = request.form.get("road_type", "flat")

    if not origin:
        return render_template("index.html", error="出発地を入力してね")

    return render_template(
        "directions.html",
        api_key=current_app.config.get("MAP_JAVA_API_KEY", ""),
        origin=origin,
        distance=distance,
        road_type=road_type,
    )
@main_bp.post("/results")
def results():
    return render_template("results.html")                                                                                  


@main_bp.post("/gpx")
def gpx_download() -> Response:
    payload = request.get_json(silent=True) or {}

    name = str(payload.get("name") or "route")
    points_raw = payload.get("points") or []
    if not isinstance(points_raw, list):
        return Response("Invalid points", status=400)

    if len(points_raw) < 2:
        return Response("Not enough points", status=400)

    if len(points_raw) > 10000:
        return Response("Too many points", status=413)

    points: list[GpxPoint] = []
    for item in points_raw:
        if not isinstance(item, dict):
            return Response("Invalid point", status=400)
        if "lat" not in item or ("lng" not in item and "lon" not in item):
            return Response("Invalid point", status=400)
        try:
            lat = float(item["lat"])
            lon = float(item.get("lng", item.get("lon")))
        except (TypeError, ValueError):
            return Response("Invalid point", status=400)
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            return Response("Invalid point", status=400)
        points.append(GpxPoint(lat=lat, lon=lon))

    gpx_xml = build_gpx_xml(track_name=name, points=points)
    content_disposition = build_content_disposition(name, ext="gpx")

    return Response(
        gpx_xml,
        status=200,
        mimetype="application/gpx+xml; charset=utf-8",
        headers={"Content-Disposition": content_disposition},
    )