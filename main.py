#!/usr/bin/env python

"""This is the SthlmBetong web app."""

# FastAPI and Pydantic
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings
# Basic Python modules
from typing import Optional
import sys
import os.path
import locale
import json
import logging
import logging.config
import time
from datetime import date as dt
# Application modules
import artportalen


# Constants
secrets = ["ARTPORTALEN_OBSERVATIONS_API_KEY",
           "ARTPORTALEN_SPECIES_API_KEY"]


def file_secret_as_env(var_name: str):
    """Reads a secret from a textfile - if that file exists - and then ads the secret to the
       "environment" of this program. This is used to enable this program to read secrets from
       textfiles when it is packaged as a Docker image and run as a Docker container."""
    # The convention for Docker compose files is to name these files *_FILE and provide that name
    # and its value - a file path - as an environment variable.
    file_var = f"{var_name}_FILE"
    if file_path := os.getenv(file_var):
        with open(file_path) as f:
            value = f.read().strip()
            os.environ[var_name] = value
        print(f"Secrets file '{file_var}' contains '{value}'")
    else:
        print(f"No secrets file: '{file_var}'")


# Read in the secrets from files, if they exist, as environment variables. They will then be picked
# up by Settings below.
[file_secret_as_env(var) for var in secrets]


class Settings(BaseSettings):
    """Provides configuration and environment variables via the Pydantic BaseSettings class. Values
       are read in this order:
       1) Environment variables. If they are not set then from
       2) Key/values from a ".env" file. If they are not set there then from
       3) Default values set in this class."""
    VERSION: str = "0.0.1"
    TEMPLATES_DIR: str = "templates"
    DATE_FORMAT: str = "Date: %a, %d %b %Y %H:%M:%S"
    ARTPORTALEN_OBSERVATIONS_API_KEY: Optional[str] = None
    ARTPORTALEN_SPECIES_API_KEY: Optional[str] = None
    POLYGON_FILE: str = "./conf/polygon.sthlmbetong.json"
    DEFAULT_TAXON_SEARCH_ID: int = 4000104  # Id of the taxon "Aves" in the Artportalen Species API.
    DEFAULT_NUMBER_OF_OBSERVATIONS: int = 50
    LOGGING_LEVEL: str = "DEBUG"
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

    class ConfigDict:
        env_file = ".env"


def polygon_coordinates(filename):
    """The list of polygon coordinates in WGS84 from the file `filename` to use when searching
       for observations in the Artportalen Observations API. Return None if it fails."""
    result = None
    if not os.path.exists(filename):
        settings.logger.error(f"Polygon file {filename} not found.")
    else:
        with open(filename) as f:
            try:
                result = json.load(f)
            except json.decoder.JSONDecodeError:
                settings.logger.error(f"Polygon file {filename} is not a valid JSON file.")
    return result


# Set up some application globals
settings = Settings()
if not settings.ARTPORTALEN_OBSERVATIONS_API_KEY:
    settings.logger.error("Environment variable 'ARTPORTALEN_OBSERVATIONS_API_KEY' not set")
    sys.exit(1)
if not settings.ARTPORTALEN_SPECIES_API_KEY:
    settings.logger.error("Environment variable 'ARTPORTALEN_SPECIES_API_KEY' not set")
    sys.exit(2)
if not settings.POLYGON_FILE:
    settings.logger.error("Environment variable 'POLYGON_FILE' not set")
    sys.exit(3)
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
sapi = artportalen.SpeciesAPI(settings.ARTPORTALEN_SPECIES_API_KEY)
oapi = artportalen.ObservationsAPI(settings.ARTPORTALEN_OBSERVATIONS_API_KEY)
polygon = polygon_coordinates(settings.POLYGON_FILE)
if not polygon:
    settings.logger.error(f"Failed to read polygon coordinates from {settings.POLYGON_FILE}.")
locale.setlocale(locale.LC_TIME, 'sv_SE.UTF-8')


def get_observations(from_date, to_date, taxon_name=None, observer_name=None):
    """Get observations from the Artportalen API, make them tidy and consumable by the Jinja2
       templates and put them into a list."""
    # Get the taxa ids that match the given `taxon_name`.
    taxon_ids = [settings.DEFAULT_TAXON_SEARCH_ID]
    if taxon_name:
        taxa = sapi.taxa_by_name(taxon_name,
                                 exact_match=True)
        if not taxa:
            settings.debug(f"No taxa matching {taxon_name} found in Artportalen Species API")
        else:
            taxon_ids = [t["taxonId"] for t in taxa]

    # Set up the search filter for the Artportalen Observations API
    sfilter = artportalen.SearchFilter()
    sfilter.set_taxon(ids=taxon_ids)
    sfilter.set_geographics_geometries(geometries=[{"type": "polygon",
                                                    "coordinates": [polygon]}])
    sfilter.set_verification_status()
    sfilter.set_output()
    sfilter.set_date(startDate=from_date,
                     endDate=to_date,
                     dateFilterType="OverlappingStartDateAndEndDate",
                     timeRanges=[])
    sfilter.set_modified_date()
    sfilter.set_dataProvider()
    observations = oapi.observations(sfilter,
                                     skip=0,
                                     take=1000,
                                     sort_descending=True,
                                     verbose=False)
    return observations


def transformed_observations(artportalen_observations):
    """List of transformed observations. We transform every observation to a object representation
       suitable for the Jinja2 template to consume and generate a nice UI representation of."""
    result = []
    for o in artportalen_observations["records"]:
        # Fix a compact representation of the time of the observation
        t = o["event"]["endDate"]
        x = {"name": o["taxon"]["vernacularName"].capitalize(),
             "location": o["location"],
             "time": t,
             "observers": o["occurrence"]["recordedBy"]}
        # Add the rarity level
        if x["name"] == "Ringnäbbad mås":
            x["rarity"] = 10
        else:
            x["rarity"] = 1
        result.append(x)
    return result


# Set up FastAPI
app = FastAPI(
    title="Microbirding SthlmBetong",
    version=settings.VERSION)
app.mount("/resources", StaticFiles(directory="resources"), name="resources")


# Implement the application resources
@app.get("/", response_class=HTMLResponse)
async def get_index_file(request: Request, date: str = Query(None)):
    """The main application page (index.html)."""
    tic = time.perf_counter_ns()

    # Redirect to "/" if there are unrecognized query parameters
    # TBD

    # Figure out which date to get observations for
    if date:
        try:
            observations_date = dt.fromisoformat(date)
            if observations_date > dt.today():
                return RedirectResponse(url="/", status_code=302)
        except ValueError:
            # Redirect to root without query parameters
            return RedirectResponse(url="/", status_code=302)
    else:
        observations_date = dt.today()
    is_today = observations_date == dt.today()

    # Get obeservations from the Artportalen API
    observations = get_observations(observations_date.isoformat(),
                                    observations_date.isoformat(),
                                    None,
                                    None)
    daystr = observations_date.strftime('%A, %-d %B').capitalize()
    print("========================")
    print(f"date: {date}")
    print(f"observations_date: {observations_date}")
    print(f"Today: {observations_date.strftime('%A, %-d %B').capitalize()}")
    print(f"Query parameters: {request.query_params}")
    print(f"Query parameters: {type(request.query_params)}")
    print("========================")
    # Filter the observations so we can display them nicely in the UI
    observations = transformed_observations(observations)
    result = templates.TemplateResponse("index.html",
                                        {"request": request,
                                         "day": daystr,
                                         "is_today": is_today,
                                         "observations": observations})

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result
