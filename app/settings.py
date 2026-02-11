"""
Module to handle settings, configgs and version info for the app.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Mapping

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Release and build info files
# These are created in:
# a) the Github actions script when it's triggered to run.
# b) the ./scripts/rund-dev.sh when run locally
RELEASE_TAG_FILE = Path("./RELEASE_TAG_FILE")
BUILD_DATETIME_FILE = Path("./BUILD_DATETIME_FILE")
GIT_HASH_FILE = Path("./GIT_HASH_FILE")


def _read_tag_file(path: Path, missing: str) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return missing


def release_tag() -> str:
    return _read_tag_file(RELEASE_TAG_FILE, "No RELEASE_TAG_FILE found")


def build_datetime_tag() -> str:
    return _read_tag_file(BUILD_DATETIME_FILE, "No BUILD_DATETIME_FILE found")


def git_hash_tag() -> str:
    return _read_tag_file(GIT_HASH_FILE, "No GIT_HASH_FILE found")


class Settings(BaseSettings):
    """Settings sources precedence (pydantic-settings v2 default):
      1) init kwargs
      2) environment variables
      3) .env (dotenv)
      4) secrets_dir
    (Exact ordering depends on your customise_sources; this default is usually fine.)"""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        secrets_dir="/run/secrets")

    # App
    VERSION: str = "0.0.1"
    ENVIRONMENT: str | None = None
    UMAMI_WEBSITE_ID: str | None = None

    # Paths
    TEMPLATES_DIR: Path = Path("./app/page-templates")
    MICROBIRDING_AREA_DIRECTORY: Path = Path("./data/areas")
    LOGGING_CONFIG_FILE: Path = Path("./conf/logging-config.json")
    CONTENT_DIRECTORY: Path = Path("./content")

    # Domain config
    DATE_FORMAT: str = "Date: %a, %d %b %Y %H:%M:%S"
    DEFAULT_TAXON_SEARCH_ID: int = 4000104
    DEFAULT_NUMBER_OF_OBSERVATIONS: int = 50

    ABOUT_SECTIONS: Mapping[str, str] = {
        "about-app": "about-app.md",
        "personal-data-policy": "personal-data-policy.md",
        "terms-of-use": "terms-of-use.md",
        "team": "team.md",
    }
    ABOUT_DEFAULT_SLUG: str = "about-app"

    # Secrets
    ARTPORTALEN_OBSERVATIONS_API_KEY: SecretStr | None = None
    ARTPORTALEN_SPECIES_API_KEY: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    # One instance per process; tests can call get_settings.cache_clear()
    return Settings()
