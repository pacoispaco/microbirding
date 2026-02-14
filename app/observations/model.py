"""
Application model of observations independent of sources
"""

from datetime import datetime as dtime
from .sources.artportalen import client


def transformed_observations(artportalen_observations):
    """List of transformed observations suitable for rendering in HTML with a Jinja2 template.
       Here we can add rarity data and other stuff which affects how observations is presented.
       THIS SHOULD LIVE IN ./app/observations/model.py"""
    result = []
    for o in artportalen_observations["records"]:
        # Establish what name of the taxon to use
        if "vernacularName" in o.get("taxon", {}):
            name = o["taxon"]["vernacularName"].capitalize()
        else:
            name = o["taxon"]["scientificName"]
        info = {"name": name}

        # Fix a compact representation of the time of the observation
        d = dtime.fromisoformat(o["event"]["startDate"])
        starttime = d.astimezone().strftime("%H:%M")
        d = dtime.fromisoformat(o["event"]["endDate"])
        endtime = d.astimezone().strftime("%H:%M")
        if starttime == "00:00" and endtime == "23:59":
            t = ""
        elif starttime == endtime:
            t = starttime
        else:
            t = f"{starttime}-{endtime}"
        info["time"] = t

        # Establish observers or data source
        if "recordedBy" in o.get("occurrence", {}):
            observers = o["occurrence"]["recordedBy"]
        else:
            observers = o["datasetName"]
        info["observers"] = observers

        # Establish longitude and latitude
        info["longitude"] = o["location"]["decimalLongitude"]
        info["latitude"] = o["location"]["decimalLatitude"]

        # Establish dataset name, eg. "Artportalen", "iNaturalist" etc.
        info["data_source"] = o["datasetName"]
        if info["data_source"] == "Artportalen":
            info["data_source_abbreviation"] = "AP"
        elif info["data_source"] == "iNaturalist":
            info["data_source_abbreviation"] = "IN"
        elif info["data_source"] == "Bird ringing centre in Sweden, via GBIF":
            info["data_source_abbreviation"] = "BR"
        else:
            info["data_source_abbreviation"] = info["data_source"]

        # Establish id in data set
        info["id"] = o["occurrence"]["occurrenceId"]

        # Get additional data on the observation from Artportalen
        if o["datasetName"] == "Artportalen":
            info["occurrence"] = o["occurrence"]
            locality = o["location"]["locality"].split(",")[0]
            is_redlisted = o["taxon"]["attributes"]["isRedlisted"]
            if is_redlisted:
                redlist_category = o["taxon"]["attributes"]["redlistCategory"]
            else:
                redlist_category = None

            # Set redlist info
            info["isRedlisted"] = is_redlisted
            info["redlistCategory"] = redlist_category

            # Set number of individuals, sex, age and activity
            info["number"] = o["occurrence"]["organismQuantity"]
            if "sex" in o["occurrence"]:
                sex = o["occurrence"]["sex"]["id"]
                info["sex"] = client.vocabulary_sex[sex]
            else:
                info["sex"] = None
            if "lifeStage" in o["occurrence"]:
                info["age"] = o["occurrence"]["lifeStage"]["value"]
            else:
                info["age"] = None
            if "activity" in o["occurrence"]:
                info["activity"] = o["occurrence"]["activity"]["value"]
            else:
                info["activity"] = None

        # Set locality info
            info["locality"] = locality
            info["longitude"] = None
            info["latitude"] = None

            # Set URL to observation info at source
            info["data_source_observation_url"] = o["occurrence"]["url"]

        elif o["datasetName"] == "iNaturalist":
            # Set number of indviduals, sex, age and activity
            info["number"] = None
            info["sex"] = None
            info["age"] = None
            info["activity"] = None
            # There's no info in these records about redlisting, sof or now we just ignore it

            # Set locality info
            municipality = o['location']['municipality']['name']
            county = o['location']['county']['name']
            info["locality"] = f"{municipality}, {county}"

            # Set URL to observation info at source
            info["data_source_observation_url"] = o["occurrence"]["occurrenceId"]

        elif o["datasetName"] == "Bird ringing centre in Sweden, via GBIF":
            # No info on observers
            info["observers"] = ""

            # Set redlist info
            info["isRedlisted"] = is_redlisted
            info["redlistCategory"] = redlist_category

            # Set number of indviduals, sex, age and activity
            info["number"] = o["occurrence"]["individualCount"]
            info["sex"] = None
            info["age"] = None
            info["activity"] = None

            # Set locality info
            municipality = o['location']['municipality']['name']
            county = o['location']['county']['name']
            info["locality"] = f"{municipality}, {county}"

            # Set URL to observation info at source. The Jinja2 template will only create links
            # if info["id"] begins with "http".
            info["data_source_observation_url"] = info["id"]

        elif o["datasetName"] == "Lund University Biological Museum - Animal Collections":
            info["occurrence"] = o["occurrence"]
            locality = o["location"]["locality"].split(",")[0]
            is_redlisted = o["taxon"]["attributes"]["isRedlisted"]
            if is_redlisted:
                redlist_category = o["taxon"]["attributes"]["redlistCategory"]
            else:
                redlist_category = None

            # Set redlist info
            info["isRedlisted"] = is_redlisted
            info["redlistCategory"] = redlist_category

            # Set number of individuals, sex, age and activity
            if "organismQuantity" not in o["occurrence"].keys():
                if "individualCount" not in o["occurrence"].keys():
                    info["number"] = "?"
                else:
                    info["number"] = o["occurrence"]["individualCount"]
            else:
                info["number"] = o["occurrence"]["organismQuantity"]

            if "sex" in o["occurrence"]:
                sex = o["occurrence"]["sex"]["id"]
                info["sex"] = client.vocabulary_sex[sex]
            else:
                info["sex"] = None
            if "lifeStage" in o["occurrence"]:
                info["age"] = o["occurrence"]["lifeStage"]["value"]
            else:
                info["age"] = None
            if "activity" in o["occurrence"]:
                info["activity"] = o["occurrence"]["activity"]["value"]
            else:
                info["activity"] = None

            # Set locality info
            info["locality"] = locality
            info["longitude"] = None
            info["latitude"] = None

            # Set URL to observation info at source
            info["data_source_observation_url"] = o["occurrence"]["occurrenceId"]

        # Add the rarity level according to some model not yet decided!
        # TBD
#        if info["name"] == "Ringnäbbad mås":
#            info["rarity"] = 10
#        else:
#            info["rarity"] = 1

        result.append(info)
    return result
