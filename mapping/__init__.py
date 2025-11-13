"""
Mapping module. Consists of two sub-modules; "models" and "repository" and contains Pydantic model
classes for Coordinate, Geopolygon, BoundingBox and MicrobirdingArea as well as an AreaRepository
class for reading and saving MicrobirdingArea representations in JSON-format from and to JSON
files. This module is meant to be imported and then invoked with the "configure" method which takes
as parameter the directory where the MicrobirdingArea JSON-files are stored.
"""

from .models import Coordinate, Geopolygon, BoundingBox, MicrobirdingArea, MapLibreStyle, GeoJSON
from .repository import AreaRepository

__all__ = [
    "Coordinate",
    "Geopolygon",
    "BoundingBox",
    "MicrobirdingArea",
    "areas",
    "area_by_name",
]


_repo: AreaRepository | None = None


def configure(storage_dir: str) -> None:
    """Initialize the mapping module with a storage directory. Must be called before using the
       convenience functions below."""
    global _repo
    _repo = AreaRepository(storage_dir)


def areas() -> list[str]:
    """Returns a list of the area names."""
    return _repo.areas()


def area_by_name(name: str) -> MicrobirdingArea | None:
    """Returns the MicrobirdingArea with the given `name`."""
    return _repo.area_by_name(name)


def geojson_area_by_name(name: str) -> GeoJSON:
    """Returns the GeoJSON area with the given name."""
    area = area_by_name(name)
    polygon = area.geopolygons[0].serialize_as_list()
    gjarea = GeoJSON(type="FeatureCollection",
                     features=[{"type": "Feature",
                                "properties": {"name": "SthlmBetong"},
                                "geometry": {"type": "Polygon",
                                             "coordinates": [polygon]}}])
    return gjarea


def default_maplibre_style() -> MapLibreStyle:
    """Returns the default MapLibre style."""
    mls = MapLibreStyle(version=8,
                        name="Microbirding default style",
                        # Optional: center & zoom so you don't write client-side fitBounds
                        center=[18.0686, 59.3293],
                        zoom=12,
                        # Optional: keep bounds in metadata (omit if center/zoom suffice)
                        # Simple bounding box for fit (SW lng,lat, NE lng,lat)
                        metadata={"bounds": [18.041, 59.317, 18.096, 59.336]},
                        sources={"osm": {"type": "raster",
                                         "tiles": [
                                             "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                             "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                             "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                         ],
                                         "tileSize": 256,
                                         "attribution": "© OpenStreetMap contributors"},
                                 "areas": {"type": "geojson", "data": "/mapping/areas"}},
                        layers=[
                                {"id": "osm", "type": "raster", "source": "osm"},
                                {"id": "areas-fill", "type": "fill", "source": "areas",
                                 "paint": {"fill-color": "#3b82f6", "fill-opacity": 0.18}},
                                {"id": "areas-outline", "type": "line", "source": "areas",
                                 "paint": {"line-color": "#1d4ed8", "line-width": 2}},
                               ])
    return mls
