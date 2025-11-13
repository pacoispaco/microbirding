"""
Pydantic models for the mapping module.
"""

from typing import List, Any
from pydantic import BaseModel, Field, model_serializer, model_validator


class Coordinate(BaseModel):
    """Represents a WGS84 coordinate with latitude and longitude."""
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in degrees (-180 to 180)"
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in degrees (-90 to 90)"
    )

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, v):
        # Accept [lon, lat]
        if isinstance(v, (list, tuple)) and len(v) == 2:
            lon, lat = v
            return {"latitude": float(lat), "longitude": float(lon)}
        return v

    @model_serializer
    def serialize_as_tuple(self):
        """Emit as a JSON array instead of an object."""
        return (self.longitude, self.latitude)


class Geopolygon(BaseModel):
    """Represents a geopolygon with at least 3 coordinates. The coordinates are implicitly
       connected in the order they appear, and the last coordinate is implicitly connected
       to the first coordinate."""
    polygon: List[Coordinate] = Field(
        ...,
        description="List of coordinates that define a closed polygon."
    )

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, v):
        # If we get a raw list of coordinate pairs, treat it as the polygon field
        if isinstance(v, list):
            return {"polygon": v}
        return v

    @model_validator(mode="after")
    def check_polygon(self):
        if len(self.polygon) < 3:
            raise ValueError("A Geopolygon must contain at least 3 coordinates.")
        return self

    @model_serializer
    def serialize_as_list(self):
        """Emit as a list of [longitude, latitude] pairs."""
        return [[c.longitude, c.latitude] for c in self.polygon]


class BoundingBox(BaseModel):
    """Represents a bounding box with a SW coordinate and a NE coordinate."""
    sw_coordinate: Coordinate
    ne_coordinate: Coordinate

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, v):
        # Accept flat 4-list or 2-list-of-pairs
        if isinstance(v, (list, tuple)):
            if len(v) == 4:  # [sw_lon, sw_lat, ne_lon, ne_lat]
                sw_lon, sw_lat, ne_lon, ne_lat = map(float, v)
                return {
                    "sw_coordinate": [sw_lon, sw_lat],
                    "ne_coordinate": [ne_lon, ne_lat],
                }
            if len(v) == 2 and all(isinstance(p, (list, tuple)) and len(p) == 2 for p in v):
                # [[sw_lon, sw_lat], [ne_lon, ne_lat]]
                return {"sw_coordinate": v[0], "ne_coordinate": v[1]}
        return v

    @model_validator(mode="after")
    def check_bounding_box(self):
        """Check that SW coordinate is south-west of the NE coordinate."""
        if self.sw_coordinate.latitude >= self.ne_coordinate.latitude:
            raise ValueError(
                "Invalid bounding box: SW latitude "
                f"{self.sw_coordinate.latitude} must be < "
                f"NE latitude {self.ne_coordinate.latitude}"
            )
        if self.sw_coordinate.longitude >= self.ne_coordinate.longitude:
            raise ValueError(
                "Invalid bounding box: SW longitude "
                f"{self.sw_coordinate.longitude} must be < "
                f"NE longitude {self.ne_coordinate.longitude}"
            )
        return self

    @model_serializer
    def serialize_as_list(self):
        """Emit as a list containing [SW longitude, SW latitude, NE longitude, NE latitude]."""
        return [self.sw_coordinate.longitude, self.sw_coordinate.latitude,
                self.ne_coordinate.longitude, self.ne_coordinate.latitude]


class MicrobirdingArea(BaseModel):
    """Represents a microbirding area."""
    name: str = Field(..., description="The name of the microbirding area.")
    geopolygons: List[Geopolygon] = Field(
        ...,
        description="The geopolygons that define the microbirding area."
    )
    center: Coordinate = Field(
        ...,
        description="The centre coordinate of the map when visualizing the microbirding area."
    )
    bounding_box: BoundingBox = Field(
        ...,
        description="The bounding box of the map when visualizing the microbirding area."
    )

    @model_validator(mode="after")
    def check_geopolygons(self):
        if len(self.geopolygons) == 0:
            raise ValueError("A MicrobirdingArea must contain at least 1 Geopolygon.")
        return self

    def geopolygon_count(self) -> int:
        """The number of geopolygons in this area."""
        return len(self.geopolygons)


class GeoJSON(BaseModel):
    """Represents A GeoJSON object.
       See: https://maplibre.org/spatial-k/geojson/#feature."""
    type: str  # "type" is a kyword but can be used as a class attribute
    features: list[dict[str, Any]]


class MapLibreStyle(BaseModel):
    """Represents a MapLibre style JSON document which defines the visual appearance of a map.
       See: https://maplibre.org/maplibre-style-spec/."""
    version: int = 8
    name: str
    metadata: dict[str, Any]
    center: Coordinate
    zoom: int
    sources: dict[str, Any]
    layers: list[dict[str, Any]]
