"""
Module for accessing and using the mapping services. An instance of class MappingService should
be created and initialized once in any app using the mapping module.
"""

from __future__ import annotations
from .repository import AreaRepository
from .models import MicrobirdingArea, GeoJSON, MapLibreStyle


class MappingService:
    def __init__(self, storage_dir: str) -> None:
        self._repo = AreaRepository(storage_dir)

    def areas(self) -> list[str]:
        return self._repo.areas()

    def area_by_name(self, name: str) -> MicrobirdingArea | None:
        return self._repo.area_by_name(name)

    def geojson_area_by_name(self, name: str) -> GeoJSON:
        area = self.area_by_name(name)
        if area is None:
            raise KeyError(f"Unknown area: {name}")

        polygon = area.geopolygons[0].serialize_as_list()
        return GeoJSON(
            type="FeatureCollection",
            features=[{
                "type": "Feature",
                "properties": {"name": name},
                "geometry": {"type": "Polygon", "coordinates": [polygon]},
            }],
        )

    def default_maplibre_style(self) -> MapLibreStyle:
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
