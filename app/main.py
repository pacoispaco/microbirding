#!/usr/bin/env python

"""This is the Microbirding/SthlmBetong web app."""

# FastAPI modules
from fastapi import FastAPI, status, Request, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Standard Python modules
from contextlib import asynccontextmanager
from pathlib import Path
import locale
import logging
import logging.config
import time
import csv
from datetime import date as dt, timedelta
from datetime import datetime as dtime

# Application modules
from .observations.sources.artportalen.provider import ArtportalenProvider
from .observations import model
import app.mapping as mapping
from app.utils.logging import setup_logging
from app.utils.changelog_renderer import mistune_markdown_instance
from .settings import get_settings, release_tag, build_datetime_tag, git_hash_tag

APP_LOGGER_NAME = "microbirding"
logger = logging.getLogger(APP_LOGGER_NAME)


def _require(value, name: str) -> None:
    if value is None:
        raise RuntimeError(f"Missing required setting: {name}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    setup_logging(str(settings.LOGGING_CONFIG_FILE))
    logger.info("Starting Microbirding app")
    logger.info(
        "Release: %s, Built: %s, Git hash: %s",
        release_tag(),
        build_datetime_tag(),
        git_hash_tag(),
    )

    # Ensure required settings exist
    _require(settings.ARTPORTALEN_OBSERVATIONS_API_KEY, "ARTPORTALEN_OBSERVATIONS_API_KEY")
    _require(settings.ARTPORTALEN_SPECIES_API_KEY, "ARTPORTALEN_SPECIES_API_KEY")

    # Create dependencies once
    app.state.settings = settings
    app.state.templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

    # Create the ArtportalenProvider
    app.state.artportalen_provider = ArtportalenProvider(
        settings=app.state.settings,
        logger=logger)

    mapping.configure(str(settings.MICROBIRDING_AREA_DIRECTORY))
    locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")

    logger.info("Application initialized.")
    yield
    logger.info("Stopping Microbirding app")


settings = get_settings()
if settings.ENVIRONMENT != "DEV":
    # Turn of API documentation
    app = FastAPI(title="Microbirding webapp",
                  lifespan=lifespan,
                  docs_url=None,
                  redoc_url=None,
                  openapi_url=None)
else:
    app = FastAPI(title="Microbirding webapp",
                  lifespan=lifespan)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
app.mount("/app/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


def observations_for_presentation(area_name: str, observations_date):
    """Dictionary with observations for the given `observations_date` (in "YYYY--MM-DD" format) and
       all attribute values needed for the Jinja2 template file
       "hx-observations-list.html" to render HTML.
       THIS SHOULD LIVE IN ./app/observations/model.py"""
    previous_date = (observations_date - timedelta(days=1)).isoformat()
    next_date = (observations_date + timedelta(days=1)).isoformat()

    # Get obeservations from the Artportalen API
    ap_provider = app.state.artportalen_provider
    observations = ap_provider.get_observations(area_name,
                                                observations_date.isoformat(),
                                                observations_date.isoformat(),
                                                None,
                                                None)
    if not observations:
        extra = {"info": "Failed to get data on observations for a given date",
                 "date": f"{observations_date.isoformat()}"}
        logger.warning("Call to main.observations_for_presentation()",
                       extra=extra)
        observations = ["Failed"]
    else:
        # Transform the observations to representations suitable for Jinja2
        observations = model.transformed_observations(observations)
    return {"day": observations_date.strftime('%A, %-d/%-m').capitalize(),
            "is_today": observations_date == dt.today(),
            "year": observations_date.year,
            "previous_date": previous_date,
            "date": observations_date.isoformat(),
            "next_date": next_date,
            "observations": observations}


# The application resources

@app.get("/", response_class=HTMLResponse)
def get_index_file(request: Request, date: str = Query(None), index_page: str = Query(None)):
    """The main application page (page-observations.html) with observations for the given `date`.
        The `index_page` query parameter is a development for easily chosing which Jinja2 template
       to use as the index_page."""
    tic = time.perf_counter_ns()

    # TBD: Redirect to this page removing unrecognized query parameters or simply remove them by
    # pushing a path that only contains the valid query parameters.

    if not date:
        today = dt.today().isoformat()
        url = request.url.include_query_params(date=today)
        return RedirectResponse(str(url), status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    if not index_page:
        index_page = "./observations/page-observations.html"

    # Figure out which date to get observations for
    if date:
        try:
            observations_date = dt.fromisoformat(date)
            if observations_date > dt.today():
                return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        except ValueError:
            # Redirect to root without query parameters
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    else:
        observations_date = dt.today()

    area_name = "SthlmBetong"
    obs = observations_for_presentation(area_name, observations_date)
    jinja2_data = {"request": request,
                   "day": obs["day"],
                   "year": observations_date.year,
                   "is_today": obs["is_today"],
                   "previous_date": obs["previous_date"],
                   "date": obs["date"],
                   "next_date": obs["next_date"],
                   "observations": obs["observations"],
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    result = app.state.templates.TemplateResponse(index_page, jinja2_data)

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/changelog", response_class=HTMLResponse)
def get_changelog(request: Request):
    """The changelog page page (page-changelog.html) displaying the version and changelog history
       of the app."""
    tic = time.perf_counter_ns()

    markdown = mistune_markdown_instance(disabled=True)

    with open("./CHANGELOG.md") as f:
        html = markdown(f.read())
    jinja2_data = {"request": request,
                   "changelog_html": html,
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    result = app.state.templates.TemplateResponse("./about/page-changelog.html", jinja2_data)

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/maps", response_class=HTMLResponse)
def get_maps(request: Request):
    """The maps page (page-maps.html) displaying the map of SthlmBetong."""
    tic = time.perf_counter_ns()

    jinja2_data = {"request": request,
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    result = app.state.templates.TemplateResponse("./maps/page-maps.html", jinja2_data)

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


SWEDISH_MONTHS = ["jan", "feb", "mar", "apr", "maj", "jun",
                  "jul", "aug", "sep", "okt", "nov", "dec"]
SWEDISH_RARITY_CATEGORIES = {"Very common": "M. vanlig",
                             "Common": "Vanlig",
                             "Uncommon": "Ovanlig",
                             "Rare": "Sällsynt",
                             "Very rare": "M. sällsynt"}


def format_mm_dd_swedish(mm_dd: str) -> str:
    """Change dates from MM-DD to numerical day of the month followed by the initial three letters
       of the name of the month in Swedish."""
    dt = dtime.strptime(f"2000-{mm_dd}", "%Y-%m-%d")
    return f"{dt.day} {SWEDISH_MONTHS[dt.month - 1]}"


def dummy_species_data():
    """Dummy species data."""
#    {"name": "Skrattmås",
#     "observations": 10164,
#     "earliest_date": "1950-07-21",
#     "latest_date": "2026-01-06",
#     "earliest_date_any_year": "01-01",
#     "median_earliest_date_per_year": "01-01",
#     "avg_earliest_date_per_year": "01-21",
#     "latest_date_any_year": "12-31",
#     "median_latest_date_per_year": "12-18",
#     "avg_latest_date_per_year": "09-29",
#     "rarity_classification": "TBD"}
    species = []
    with open("./data/test/sthlmbetong-1800-01-01--2026-01-06-summering.2.csv",
              newline="",
              encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Convert numeric fields if needed
            row["name"] = row["taxon.vernacularName"]
            obs = int(row["observations"])
            # Change rarity category to Swedish
            row["rarity_classification"] = SWEDISH_RARITY_CATEGORIES[row["rarity_classification"]]
            # Put spaces between every group of three digits
            row["observations"] = f"{obs:,}".replace(",", " ")
            d = format_mm_dd_swedish(row["earliest_date_any_year"])
            row["earliest_date_any_year"] = d
            d = format_mm_dd_swedish(row["median_earliest_date_per_year"])
            row["median_earliest_date_per_year"] = d
            d = format_mm_dd_swedish(row["avg_earliest_date_per_year"])
            row["avg_earliest_date_per_year"] = d
            d = format_mm_dd_swedish(row["latest_date_any_year"])
            row["latest_date_any_year"] = d
            d = format_mm_dd_swedish(row["median_latest_date_per_year"])
            row["median_latest_date_per_year"] = d
            d = format_mm_dd_swedish(row["avg_latest_date_per_year"])
            row["avg_latest_date_per_year"] = d
            species.append(row)
    return species


@app.get("/species", response_class=HTMLResponse)
def get_species(request: Request):
    """The species page (page-species.html) displaying info on all species that have been observed
       in the area."""
    tic = time.perf_counter_ns()

    species = dummy_species_data()
    jinja2_data = {"request": request,
                   "species": species,
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    result = app.state.templates.TemplateResponse("./species/page-species.html", jinja2_data)

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/about", response_class=HTMLResponse)
async def about_root():
    """The root resource for the about pages. Redirects to the default about page."""
    return RedirectResponse(
        url=f"/about/{app.state.settings.ABOUT_DEFAULT_SLUG}",
        status_code=307
    )


@app.get("/about/{slug}", response_class=HTMLResponse)
def get_about(request: Request, slug: str):
    """The about page (page-about.html) with information on the app."""
    tic = time.perf_counter_ns()

    if slug not in app.state.settings.ABOUT_SECTIONS:
        raise HTTPException(status_code=404, detail="Unknown section")

    markdown = mistune_markdown_instance(disabled=True)
    md_path = app.state.settings.CONTENT_DIRECTORY / app.state.settings.ABOUT_SECTIONS[slug]
    if not md_path.exists():
        raise HTTPException(status_code=500, detail="Missing content file")
    html = markdown(md_path.read_text(encoding="utf-8"))

    jinja2_data = {"request": request,
                   "active_slug": slug,
                   "section_html": html,
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    result = app.state.templates.TemplateResponse("./about/page-about.html", jinja2_data)

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


# The application hypermedia control resources.
# All of these resources have the prefix "/hx/" in their URL path.

@app.get("/hx/observations-section", response_class=HTMLResponse)
def hx_observations_section(request: Request, date: str = Query(None)):
    """The observations HTML <section> element with the observations for the given `date`."""
    # We only return this resource if it was triggered by an HTMX control. HTTP requests generated
    # by HTMX set the HTTP header "HX-request: true", so we can check for that.
    if request.headers.get("HX-Request") != "true":
        raise HTTPException(404)
    # We assume we have a valid date that isn't ahead of today's date.
    observations_date = dt.fromisoformat(date)
    area_name = "SthlmBetong"
    obs = observations_for_presentation(area_name, observations_date)
    jinja2_data = {"request": request,
                   "day": obs["day"],
                   "year": observations_date.year,
                   "is_today": obs["is_today"],
                   "previous_date": obs["previous_date"],
                   "date": obs["date"],
                   "next_date": obs["next_date"],
                   "observations": obs["observations"],
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    return app.state.templates.TemplateResponse("./observations/hx-observations-list.html",
                                                jinja2_data)


# MapLibre GL JS resources (experimental)

@app.get("/mapping/pins")
def get_mapping_pins():
    """Get some geo pins."""
    return JSONResponse(mapping.models.some_pins())


@app.get("/mapping/areas")
def get_mapping_areas():
    """Get a geo areas."""
    geojson = mapping.geojson_area_by_name("SthlmBetong")
    return JSONResponse(geojson.dict())


@app.get("/mapping/style")
def get_map_style():
    """Get a map style."""
    style = mapping.default_maplibre_style().dict()
    # Set low TTL if data changes often
    return JSONResponse(style, headers={"Cache-Control": "no-cache"})


# The application 404 exception handler

@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Render a 404 page for missing resources."""
    jinja2_data = {"request": request,
                   "path": request.url.path,
                   "version_info": {"release": release_tag(),
                                    "built": build_datetime_tag(),
                                    "git_hash": git_hash_tag()},
                   "environment": app.state.settings.ENVIRONMENT,
                   "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
    return app.state.templates.TemplateResponse("./page-404.html", jinja2_data, status_code=404)


# Resource only meant to bes served in DEV environment.None

if settings.ENVIRONMENT == "DEV":

    @app.get("/design-system", response_class=HTMLResponse)
    def get_design_system(request: Request):
        """The design system page (page-design-system.html) displaying UI stuff used in the app."""
        tic = time.perf_counter_ns()

        # We want to display an observation for development and debugging purposes
        date = "2025-12-15"
        area_name = "SthlmBetong"
        observations_date = dt.fromisoformat(date)
        obs = observations_for_presentation(area_name, observations_date)
        obs_no = 5
        jinja2_data = {"request": request,
                       "o": obs["observations"][obs_no],
                       "version_info": {"release": release_tag(),
                                        "built": build_datetime_tag(),
                                        "git_hash": git_hash_tag()},
                       "environment": app.state.settings.ENVIRONMENT,
                       "umami_website_id": app.state.settings.UMAMI_WEBSITE_ID}
        result = app.state.templates.TemplateResponse("./page-design-system.html", jinja2_data)

        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
