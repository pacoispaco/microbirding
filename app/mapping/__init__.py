"""
Mapping module. Consists of three sub-modules; "models", "repository" and "service" and contains
Pydantic model classes for Coordinate, Geopolygon, BoundingBox and MicrobirdingArea as well as an
AreaRepository class for reading and saving MicrobirdingArea representations in JSON-format from
and to JSON files. And finally it contains the service.MappingService class which is the main class
for accessing the features in this module. That class is instantiated with the directory path where
the MicrobirdingArea JSON-files are stored.
"""

from .models import Coordinate, Geopolygon, BoundingBox, MicrobirdingArea
from .service import MappingService

__all__ = [
    "Coordinate",
    "Geopolygon",
    "BoundingBox",
    "MicrobirdingArea",
    "areas",
    "area_by_name",
    "MappingService"
]
