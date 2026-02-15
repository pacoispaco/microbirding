# README file for the Microbirding SthlmBetong app

The idea for the Microbirding SthlmBetong app is to provide birders in Stockholm with a web app for getting bird observations from Artportalens API and:

  * Keeping track of bird observations done within the central parts of Stockholm.
  * Keeping tack of year and total lists for individual birders for that area, as well as keeping a total list of all birds seen in the area.
  * Providing a map of the area with the best birding spots.

This app could be both fun and could contribute to create awareness of the natural diversity in urban areas like central Stockholm. You can see it up and running at [app.sthlmbetong.se](https://app.sthlmbetong.se).

![Image of web app](./app/assets/app.sthlmbetong.se.png)

Eventually it will support more microbirding and urban locations in Sweden. You can read more about the aim and background in the [ROADMAP](./ROADMAP.md).

# Design and implementation

This web app is a HDA (Hypermedia Driven Application) and mobile-first web application written in Python using FastAPI and HTMX & Tailwind CSS. It will eventually need to persist some data to a database like SQLite, DuckDB or MongoDB. Due to rate limiting and performance issues with the Artportalen API:s it will probably need to have a caching implementation, probably using Valkey/Redis.

It uses the Swedish Artportalen APIs to get information on registered observations and species data. Due to limitations in the Artportalen Observations API there are also limitations in what this app will be able to do.

There exist two major blockers:

  * The Artportalen API only provides the presentation name of observers, and not a unique observer id. That means that certain identification of observers with common names, like "Anders Svensson", can't be done.
  * Observations of more rare birds in Artportalen, are grouped in a main observation and then sub-observations made of the same bird by other observers. The API only provides information on the main observation, not sub-observations. That means that some observations of rare birds made by some observers can't be retrieved from the API.

Apart from those two blockers, there are other limitations in the Artportalen that make it cumbersome to compile lists. Challenges exist with handling personal data in the current implementation of both Artportalen and the Artportalen API in a GDPR compliant way. These challenges also makes it difficult for clients of the API to handle personal data in a GDPR compliant way.

# To get started

Clone the repository:
```
git clone <URL-TO-REPO>
```

Create a virtual environment:
```
virtualenv -p python3 env
```

Jump into the environment:
```
source env/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```

Install the Tailwind CLI tool, version 4 (chose the relevant binary for your OS and architecture):
```
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.13/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss
```

# API keys

Both the web app and the CLI app requires two secrets as environment variables, to be able to access Artportalens API:s:
 * ARTPORTALEN_SPECIES_API_KEY. For accessing the Artportalen Species API.
 * ARTPORTALEN_OBSERVATIONS_API_KEY. For accessing the Artportalen Observations API.

You get these keys by registering at https://www.slu.se/artdatabanken/rapportering-och-fynd/oppna-data-och-apier/om-slu-artdatabankens-apier/

# Build

## Locally

Make sure you are in the Python virtual environment.

To build the app locally, you must regenerate to TailwindCSS file if you've edited CSS classes in the template files:
```
./tailwindcss -i ./tailwind.config.css -o ./app/assets/tailwind.css
```

To build the Docker image locally:
```
docker build -t microbirding-app
```

Before you commit and push code, you should lint your Python code:
```
flake8 --config flake8.conf
```
Flake8 errors will stop the CI/CD build.

## CI/CD-pipeline using GitHub Actions

A GitHub actions script builds, version-tags and publishes the app as a Docker image, on git push and git tags on the main trunk. See https://github.com/pacoispaco/microbirding/blob/main/.github/workflows/cicd-dev.yml for details.

The [CHANGELOG.md](./CHANGELOG.md) file contains information on the released versions of the web app and changes to every release. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the versioning convention is [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The main build script (./.github/workflows/cicd-dev.yml) uses the CHANGELOG.md file, and will extract the release version number in the first "double hash-mark title" with square brackets at the top of this Markdown-file. It will use that to tag the built Docker image with the extracted release version number and the latest git commit hash. It will also create a **version tag file**  containing that tag, and include that in the Docker image so the app can show the build version.

# Run and debug

Make sure you are in the Python virtual environment.

To run the app locally as a Docker container, first make sure you have set the API keys as environment variables:
```
export ARTPORTALEN_SPECIES_API_KEY=<ARTPORTALEN_SPECIES_API_KEY>
export ARTPORTALEN_OBSERVATIONS_API_KEY=<ARTPORTALEN_OBSERVATIONS_API_KEY>
```
Then just run:
```
./scripts/run-dev.sh
```
Which will 1) regenerate the `tailwind.css` file, 2) build the Docker file and 3) Run the Docker file locally.

Note that the app reads the environment variable `ENVIRONMENT` which tells the app what runtime environment it's running in. Currently it will show an orange banner and icon and also show Tailwind breakpoints if `ENVIRONMENT=DEV`. If it's anything else, it will assume it's running in a production environment. You can set `ENVIRONMENT=PROD` if you want to be explicit. In that case the app will turn off showing OpenAPI documentation at the `/docs`, `/redoc`and `/openapi.json` URL:s. 

To run the app locally, but not as a Docker container, and automatically restart the app on changed files:
```
uvicorn app.main:app --reload
```

Remember that if you change CSS classes in the template files, you need to regenerate the `tailwind.css` file.

# The apps

This repository has two apps. One is command line program `apget.py` which can get observations and info on species from the Artportalen Observations API and the Artportalen Species API. The other is a prototype web app interacts with the Artportalen API:s.

Both programs use the same Python module **artportalen.py** for interacting with Artportalens API:s.

## The apget app

This shows what apget can do:
```
./apget.py --help
```

To get the latest 200 observations of Tajgasångare (Yellow-browed warbler):
```
./apget.py -g --taxon-name Tajgasångare
```

To get the latest 200 observations in the SthlmBetong area:
```
./apget.py -g --polygon-file ./conf/polygon.sthlmbetong.json
```

# The web app

The web app runs as Docker container.

The core file for the app is **main.py**. It imports the module **artportalen.py** which has methods for accessing the Artportalen API:s. The **main.py** file has functions for serving both the web application and the HTMX resources.

For serving the HTML and HTMX resources, the **main.py** file uses Jinja2 templates that live in the directory **templates**.
