"""
Repository for accessing microbirding areas.
"""

from __future__ import annotations

import logging
from pathlib import Path
import slugify
from pydantic import BaseModel
from .models import MicrobirdingArea

logger = logging.getLogger(__name__)


class AreaRepositoryIndexEntry(BaseModel):
    """Index entry in the AreaRepository's index."""
    file_path: Path
    area: MicrobirdingArea


class AreaRepository:
    """Directory- and file-based repo for MicrobirdingArea objects (one JSON per file)."""

    def __init__(self, dir: str):
        """Initialize the AreaRepository and read MicrobirdingArea:s from JSON-files in `dir`."""
        self.storage_dir = Path(dir).expanduser().resolve()
        if not self.storage_dir.exists():
            logger.warning(f"Directory for AreaRepository {dir!r} does not exist.")
        self.index = {}
        for file_path in self.storage_dir.glob("*.json"):
            try:
                arie = AreaRepositoryIndexEntry(file_path=file_path,
                                                area=self.__load__(file_path))
            except Exception as e:
                logger.warning(f"Failed to read MicrobirdingArea JSON-file {file_path!r}.",
                               exc_info=True,
                               extra={"exception": e})
            self.index[arie.area.name] = arie

    def __load__(self, file_path: Path) -> MicrobirdingArea:
        """Load a MicrobirdingArea from the given `file_path`."""
        data = file_path.read_text(encoding="utf-8")
        return MicrobirdingArea.model_validate_json(data)

    def areas(self):
        """List of all area names."""
        return list(self.index.keys())

    def area_by_name(self, name: str) -> MicrobirdingArea:
        """Return the MicrobirdingArea by name (from the index)."""
        if name in self.index:
            return self.index[name].area
        else:
            return None

    def save(self, area: MicrobirdingArea, overwrite: bool = True):
        """Save the MicrobirdingArea `area` to a JSON-file to disk and update the index."""
        file_name = f"{slugify.slugify(area.name)}.json"
        file_path = self.storage_dir / file_name

        data = area.model_dump_json(indent=2)
        with open(file_path, 'w') as f:
            f.write(data)

        self.index[area.name] = {"file": file_path.name, "area": area}
