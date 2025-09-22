# README file for the Microbirding SthlmBetong app

The idea for the Microbirding SthlmBetong app is to provide birders in Stockholm with an web app for getting bird observations from Artportalens API and:

  * Keeping track of bird observations done within the central parts of Stockholm.
  * Keeping tack of year and total lists for individual birders for that area, as well as keeping a total list of all birds seen in the area.
  * Providing a map of the area with the best birding spots.

We believe that this would be both fun and would contribute to create awareness of the natural diversity in urban areas like central Stockholm.

Eventually it should support multiple different microbirding and urban locations in Sweden. You can read more about the aim and background in background.md.

[Images of web app]

**NOTE: Currently this app and code is very much in prototype status.**

# Design and implementation

This web app is meant to be a clean HDA (Hypermedia Driven Application) and mobile-first web application written in Python using FastAPI and HTMX & Tailwind CSS. It would eventually need to persist some data which could be stored in a SQLite or MongoDB database. 

It is meant to use the Swedish Artportalen APIs to get information on registered observations and species data. However due to limitations in the Artportalen Observations API it is currently not possible to develop an app like this with all the desired features.

There are two major blockers:

  * The Artportalen API provides only get the presentation name of observers, not unique observer id:s. That means, for common names, like "Anders Svensson", it is not possible to know with certainty who the observer is.
  * Observations of more rare birds in Artportalen, are grouped in a main observation and then subobservations made of the same bird by other observers. The API only provides information on the main observation, not subobservations. That means that some observations of rare birds made by some observers cannot be retrieved from the API.

Apart from those two blockers there is a limitation in the ability in searching for observations, which even if the two blockers were removed (and implemented), makes it very cumbersome to compile lists. There are also challenges with handling personal data in the current implementation of both Artportalen and the Artportalen API in a GDPR compliant way. These challenges also makes it impossible for clients of the API to handle personal data in a GDPR compliant way.

You can read more about the technical design, implementation ideas and the current blockers and problems with Artportalen in design.md.

# To get started

Clone the repo:
```
git clone URL-TO-REPO
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

Both the web app and the CLI app requires two environment variables to be set in order to be able to access Artportalens API:s:
 * ARTPORTALEN_SPECIES_API_KEY. For accessing the Artportalen Species API.
 * ARTPORTALEN_OBSERVATIONS_API_KEY. For accessing the Artportalen Observations API.

You obtain these keys by registering at https://www.slu.se/artdatabanken/rapportering-och-fynd/oppna-data-och-apier/om-slu-artdatabankens-apier/

# Build

## Locally

To build the app locally, you must regenerate to TailwindCSS file if you've edited CSS classes in the template files:
```
./tailwindcss -i ./tailwind.config.css -o ./resources/tailwind.css
```

To build the Docker image locally:
```
docker build -t microbirding-app
```

Before comitting and pushing code, you should lint your Python code:
```
flake8 --config flake8.conf
```
Flake8 errors, will stop the CI/CD build.

## CI/CD-pipeline using Github Actions

The app is built, version-tagged and published as a Docker image using Github actions, every time code is pushed to Github and the main trunk. See https://github.com/pacoispaco/microbirding/blob/main/.github/workflows/cicd-dev.yml for details.

# Run and debug

To run the app locally and automatically restart the app on changed files:
```
uvicorn main:app --reload
```

To run the app locally as a Docker container:
```
docker run --rm --name="sthlmbetong" -p 8000:8000 -e ARTPORTALEN_OBSERVATIONS_API_KEY=<SECRET-KEY> -e ARTPORTALEN_SPECIES_API_KEY=<SECRETKEY microbirding-app
```

Remember that if you change CSS classes in the template files, you need to regenerate the `tailwind.css` file.

# The apps

There are two apps here. One is command line program `apget.py` which can get observations and info on species from the Artportalen Observations API and the Artportalen Species API. The other is a prototype web app interacts with the Artportalen API:s.

Both programs use the same Python module "artportalen" for interacting with Artportalens API:s.

## The apget app

You can see what can be done with the app with:
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

To run the web app locally:
```
uvicorn main:app --reload
```

The app is meant to packaged as a Docker image, and run as a Docker container.

The web app is implemented in the file **main.py**. It imports the module **artportalen.py** which has methods for accessing the Artportalen API:s. The **main.py** file has functions for serving both the web application and the HTMX resources.

For serving the HTML and HTMX resources, the **main.py** file uses Jinja2 templates that live in the directory **templates**.
