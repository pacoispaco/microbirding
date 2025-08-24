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

# The apps

There are two apps here. One is command line program `apget.py` which can get observations and info on species from the Artportalen Observations API and the Artportalen Species API. The other is a prototype web app interacts with the Artportalen API:s.

The app requires two environment variables to be set in order to be able to access Artportalens API:s:
 * ARTPORTALEN_SPECIES_API_KEY. For accessing the Artportalen Species API.
 * ARTPORTALEN_OBSERVATIONS_API_KEY. For accessing the Artportalen Observations API.

You obtain these keys by registering at https://www.slu.se/artdatabanken/rapportering-och-fynd/oppna-data-och-apier/om-slu-artdatabankens-apier/

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

For serving the HTML and HTMX resources, the **main.py** file uses Jinja templates that live in the directory **templates**. The main application Jinja file **index.html** includes the Tailwind CSS files needed for styling the app.
