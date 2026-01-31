from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class GpxPoint:
    lat: float
    lon: float


_FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""

    # Avoid filesystem/HTTP header issues; keep it simple.
    name = name.replace("..", ".")
    name = _FILENAME_SAFE_RE.sub("_", name)
    name = name.strip("._-")
    return name[:80]


def build_content_disposition(filename_base: str, ext: str = "gpx") -> str:
    """Build an attachment Content-Disposition with UTF-8 filename* and ASCII fallback."""
    base = (filename_base or "route").strip() or "route"
    # Prevent header injection / invalid characters
    base = base.replace("\r", " ").replace("\n", " ").replace('"', "'")
    base = " ".join(base.split())
    base = base[:120]

    ascii_base = sanitize_filename(base) or "route"
    full_utf8 = f"{base}.{ext}"
    full_ascii = f"{ascii_base}.{ext}"
    encoded = quote(full_utf8, safe="")

    return f'attachment; filename="{full_ascii}"; filename*=UTF-8\'\'{encoded}'


def build_gpx_xml(track_name: str, points: list[GpxPoint]) -> str:
    # Minimal GPX 1.1 track
    gpx = ET.Element(
        "gpx",
        {
            "version": "1.1",
            "creator": "my_app",
            "xmlns": "http://www.topografix.com/GPX/1/1",
        },
    )

    trk = ET.SubElement(gpx, "trk")
    name_el = ET.SubElement(trk, "name")
    name_el.text = (track_name or "route").strip() or "route"

    trkseg = ET.SubElement(trk, "trkseg")
    for p in points:
        ET.SubElement(
            trkseg,
            "trkpt",
            {
                "lat": f"{p.lat:.7f}",
                "lon": f"{p.lon:.7f}",
            },
        )

    xml_bytes = ET.tostring(gpx, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")
