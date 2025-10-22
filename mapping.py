"""
Module for handling mapping stuff.
"""

from typing import Dict, Any


# Simple bounding box for fit (SW lng,lat, NE lng,lat)
STYLE_BOUNDS = [18.041, 59.317, 18.096, 59.336]


def some_pins() -> Dict[str, Any]:
    """Here are som pins."""
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"name": "Gamla stan"},
             "geometry": {"type": "Point", "coordinates": [18.0725, 59.325]}},
            {"type": "Feature", "properties": {"name": "Kungsträdgården"},
             "geometry": {"type": "Point", "coordinates": [18.0739, 59.3310]}}
        ]
    }


def some_areas(polygon: list[float]) -> Dict[str, Any]:
    """Here are some areas."""
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "Central Stockholm"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            }
        }]
    }


def some_style() -> Dict[str, Any]:
    """Here is some style."""
    return {
        "version": 8,
        # Optional: center & zoom so you don't write client-side fitBounds
        "center": [18.0686, 59.3293],
        "zoom": 12,
        # Optional: keep bounds in metadata (you can also omit if center/zoom suffice)
        "metadata": {"bounds": STYLE_BOUNDS},

        "sources": {
            "osm": {
                "type": "raster",
                "tiles": [
                    "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
                ],
                "tileSize": 256,
                "attribution": "© OpenStreetMap contributors"
            },
            "pins":  {"type": "geojson", "data": "/mapping/pins"},
            "areas": {"type": "geojson", "data": "/mapping/areas"}
        },
        "layers": [
            {"id": "osm", "type": "raster", "source": "osm"},

            {"id": "areas-fill", "type": "fill", "source": "areas",
             "paint": {"fill-color": "#3b82f6", "fill-opacity": 0.18}},

            {"id": "areas-outline", "type": "line", "source": "areas",
             "paint": {"line-color": "#1d4ed8", "line-width": 2}},

            {"id": "pins", "type": "circle", "source": "pins",
             "paint": {
                "circle-radius": 5,
                "circle-color": "#1d4ed8",
                "circle-stroke-color": "#ffffff",
                "circle-stroke-width": 1.5}
             }
        ]
    }
