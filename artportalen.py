"""
Module for interacting with Artportalens API.
"""

from __future__ import annotations
import logging
import requests
from urllib3.exceptions import HTTPError
import json
from datetime import datetime
import httplogs

# Constants
DEFAULT_FROM_DATE_RFC3339 = '1900-01-01T00:00'
API_ROOT_URL = 'https://api.artdatabanken.se'
API_KEY_HTTP_HEADER = 'Ocp-Apim-Subscription-Key'
API_COORDINATSYSTEM_WGS_84_ID = 10
API_AVES_TAXON_ID = 4000104

API_OUTPUTFIELDSET_VALUES = ["Minimium", "Extended", "AllWithValues", "All", "None"]

# Character signs from here: https://en.wikipedia.org/wiki/Miscellaneous_Symbols
MALE_SIGN = "♂"
FEMALE_SIGN = "♀"
FEMALE_AND_MALE_SIGN = "♀♂"
FEMALE_COLORED = "♀-färgad(e)"
HERMAPHRODITE_SIGN = "⚥"  # Sign convention in entomology for hermafrodite
MERCURY_SIGN = "☿"        # Sign convention in entomology for worker or neuter insects

# Artportalen vocabularies (could/should be put in separate module)
# See: https://github.com/biodiversitydata-se/SOS/blob/master/Docs/Vocabularies.md
# We complement some vocabularies with symbols that can be used in an UI
vocabulary_sex = {0: {"sv": None, "en": None, "symbol": None},
                  1: {"sv": "hane", "en": "male", "symbol": MALE_SIGN},
                  2: {"sv": "hona", "en": "female", "symbol": FEMALE_SIGN},
                  3: {"sv": "honfärgad", "en": "female coloured", "symbol": FEMALE_COLORED},
                  4: {"sv": "i par", "en": "in pair", "symbol": FEMALE_AND_MALE_SIGN},
                  5: {"sv": "arbetare", "en": "worker", "symbol": MERCURY_SIGN},
                  6: {"sv": "hermafrodit", "en": "hermaphroditic", "symbol": HERMAPHRODITE_SIGN}}

# Example stuff to make prototyping easier
EXAMPLE_SPECIES = "Tajgasångare"
EXAMPLE_TAXON_ID = 205835  # Id för Tajgasångare
EXAMPLE_SEARCH_FILTER_STR = """{
    "dataProvider": {
        "ids": []
    },
    "dataStewardship": {
        "datasetIdentifiers": []
    },
    "date": {
        "startDate": "2025-04-18",
        "endDate": "2025-04-18",
        "dateFilterType": "OverlappingStartDateAndEndDate",
        "timeRanges": []
    },
    "geographics": {
        "areas": [{
            "areaType": "Municipality",
            "featureId": "180"
        }],
    },
    "modifiedDate": {
        "from": null,
        "to": null
    },
    "taxon": {
        "includeUnderlyingTaxa": true,
        "ids": [4000104],
        "taxonListIds": [],
        "redListCategories": [],
        "taxonCategories": [],
        "taxonListOperator": "Merge"
    },
    "verificationStatus": "BothVerifiedAndNotVerified",
    "output": {
        "fieldSet": "Minimum",
        "fields": []
    }
}"""

logger = logging.getLogger(__name__)


class Taxon:

    def __init__(self):
        self.id = None
        self.name = None


class Observation:

    def __init__(self):
        self.id = None


class Person:

    def __init__(self):
        self.id = None
        self.user_name = None
        self.full_name = None


def auth_headers(api_key, auth_token=None):
    """Dictionary of authentication headers for API requests."""
    h = {API_KEY_HTTP_HEADER: api_key}
    if auth_token:
        h['Authorization'] = 'Bearer {%s}' % (auth_token)
    return h


class SpeciesAPI:
    """Handles requests to Artportalens Artfakta - Species information API."""

    def __init__(self, api_key: str):
        """Initialization. The client is responsible for managing secrets."""
        self.key = api_key
        self.url = API_ROOT_URL + "/information/v1/speciesdataservice/v1/"
        self.search_url = self.url + "speciesdata"
        self.headers = auth_headers(self.key)

    def taxa_by_name(self, name, exact_match=True):
        """Returns list of all taxa that match the name."""
        url = self.search_url + f"/search?searchString={name}"
        r = requests.get(url, headers=self.headers)
        httplogs.log_request(logger,
                             r,
                             message="HTTP request to Species API",
                             request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
        if r.status_code == 200:
            for d in r.json():
                if exact_match:
                    if d['swedishName'] == name.lower():
                        return [d]
                else:
                    return r.json()
        else:
            return None

    def taxon_by_id(self, id):
        """Returns the taxon with the given id."""
        url = self.search_url + f"?taxa={id}"
        r = requests.get(url, headers=self.headers)
        httplogs.log_request(logger,
                             r,
                             message="HTTP request to Species API",
                             request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
        if r.json() == []:
            return None
        else:
            return r.json()


class SearchFilter:
    """Represents the search filter object that is used to search in the ObservationsAPI. An
       actual search filter must be sent as a literal JSON object in the body of the POST request
       to the ObservationsAPI."""

    def __init__(self):
        """Intitialization."""
        current_date = datetime.today().strftime('%Y-%m-%d')
        self.filter = {"dataProvider": {"ids": [1]},
                       "dataStewardship": {"datasetIdentifiers": []},
                       "date": {"startDate": current_date,
                                "endDate": current_date,
                                "dateFilterType": "OverlappingStartDateAndEndDate",
                                "timeRanges": []}
                       }

    def json_string(self):
        """Returns a JSON string representation of this filter."""
        return json.dumps(self.filter)

    def set_dataProvider(self, ids: list[str] = []):
        """Set the data providers by providing a list of id:s.
           Use `ObservationsAPI.data_providers()` to find out valid data providers."""
        self.filter["dataProvider"] = {"ids": ids}

    def set_dataStewardship(self, datasetIdentifiers: list[str] = []):
        """Set the dataStewardship by providing a list of id:s."""
        self.filter["dataStewardship"] = {"datasetIdentifiers": datasetIdentifiers}

    def set_date(self,
                 startDate: str = None,
                 endDate: str = None,
                 dateFilterType: str = None,
                 timeRanges: list[str] = None):
        """Set the start and end dates, date filter type and time range where time range can be
           one of "Morning", "Forenoon", "Afternoon", "Evening" or Night."""
        self.filter["date"] = {"startDate": startDate,
                               "endDate": endDate,
                               "dateFilterType": dateFilterType,
                               "timeRanges": timeRanges}

    def set_modified_date(self, from_date: str = None, to_date: str = None):
        """Set the modified date criteria."""
        self.filter["modifiedDate"] = {"from": from_date,
                                       "to": to_date}

    def set_geographics_areas(self, areas: list[dict]):
        """Set the geographics of the search filter by specifying one or more defined and
           identified geographical areas.
           Every dict must have this structure:
           {"areaType": str,
            "featureId": str}
           where "areaType" can be one of; "Municipality", "Community", "Sea", "CountryRegion",
           "NatureType", "Province", "Ramsar", "BirdValidationArea", "Parish", "Spa", "County",
           "ProtectedNature", "SwedishForestAgencyDistricts", "Sci", "WaterArea", "Atlas5x5",
           "Atlas10x10", "SfvDistricts" or "Campus" and "featureId" is an id of an instance of
           those areaType:s."""
        self.filter["geographics"] = {"areas": areas}

    def set_geographics_geometries(self,
                                   geometries: list[str],
                                   considerDisturbanceRadius: bool = False,
                                   considerObservationAccuracy: bool = False,
                                   maxDistanceFromPoint: float = None):
        """Set the geographics of the search filter by specifying point or polygon. We assume
           in WGS84 coordinates and formatted in some sensible string format.
           In the API documentation at https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=GeographicsFilterDtothey call theylist the type as being IGeoShape and
           elsewhere in the documentation they say they use ElasticSearch for the search
           features of the API, so see:
           https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/geo-shape"""
        self.filter["geographics"] = {"geometries": geometries}

    def set_geographics_bounding_box(self,
                                     bottomRight_latitude: float,
                                     bottomRight_longitude: float,
                                     topLeft_latitude: float,
                                     topLeft_longitude: float):
        """Set the geographics of the search filter by specifying a bounding box.
           We assume latitude and logitude values are WGS84.
           see: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=LatLonBoundingBoxDto"""
        bb = {"boundingBox": {"bottomRight": {"latitude": bottomRight_latitude,
                                              "longitude": bottomRight_longitude},
                              "topLeft": {"latitude": topLeft_latitude,
                                          "longitude": topLeft_longitude}}}
        self.filter["geographics"] = bb

    def set_taxon(self, ids: list[str],
                  taxonListIds: list[str] = None,
                  includeUnderlyingTaxa: bool = True,
                  redListCategories: list[str] = None,
                  taxonCategories: list[str] = None,
                  taxonListOperator: str = "Merge"):
        """Set the taxon to search for. redListCategories can be one of "DD", "EX", "RE", "CR",
           "EN", "VU", "NT", "LC", "NA" or "NE". taxonListOperator can be one of "Merge" ord
           "Filter".
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&definition=TaxonFilterDto"""
        self.filter["taxon"] = {"includeUnderlyingTaxa": includeUnderlyingTaxa,
                                "ids": ids,
                                "taxonListIds": taxonListIds,
                                "redListCategories": redListCategories,
                                "taxonCategories": taxonCategories,
                                "taxonListOperator": taxonListOperator}

    def set_verification_status(self, verificationStatus: str = "BothVerifiedAndNotVerified"):
        """Set the verification status of the search filter. It can be one of "Verified",
           "NotVerified" or "BothVerifiedAndNotVerified".
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&
           definition=StatusVerificationDto"""
        self.filter["verificationStatus"] = verificationStatus

    def set_output(self, fieldSet: str = "Minimum", fields: list[str] = []):
        """Set the output scope of the search filter.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch&definition=OutputFilterDto"""
        self.filter["output"] = {"fieldSet": fieldSet,
                                 "fields": fields}


class ObservationsAPI:
    """Handles requests to Artportalens Species Observations Service API."""

    # See the Observation object in the API for alternative attributes to sort by.
    DEFAULT_SORT_BY_ATTRIBUTE_FOR_OBSERVATIONS = 'event.startDate'

    def __init__(self, api_key: str):
        """Initialization. The client is responsible for managing secrets."""
        self.key = api_key
        self.url = API_ROOT_URL + "/species-observation-system/v1/"
        self.search_url = self.url + "Observations/Search"
        self.observation_url = self.url + "Observations/{id}"
        self.headers = auth_headers(self.key)

    def last_response(self):
        """Returns the last response (a requests response object). Use this to check any problems
           in the last API request. You can use the attributes "status_code" and "content" to find
           out more. See: https://requests.readthedocs.io/en/latest/api/#requests.Response"""
        return self.last_response

    def version(self):
        """Returns version of the API. This can be used to ping the API.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=ApiInfo_GetApiInfo"""
        url = self.url + "api/ApiInfo"
        r = requests.get(url, headers=self.headers)
        httplogs.log_request(logger,
                             r,
                             message="HTTP request to Observations API",
                             request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
        return r.json()

    def data_providers(self):
        """Returns a list of data providers that have observations in the API.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=DataProviders_GetDataProviders"""
        url = self.url + "/DataProviders"
        r = requests.get(url, headers=self.headers)
        httplogs.log_request(logger,
                             r,
                             message="HTTP request to Observations API",
                             request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
        return r.json()

    def observations_test(self):
        """Returns the observations based on a hard coded search filter."""
        url = self.search_url
        params = {"skip": 0,
                  "take": 200,
                  "sortBy": "event.Startdate",
                  "sortOrder": "Desc"}
        headers = self.headers | {"Content-Type": "application/json"}
        search_filter = EXAMPLE_SEARCH_FILTER_STR
        r = requests.post(url, params=params, headers=headers, data=search_filter)
        httplogs.log_request(logger,
                             r,
                             message="HTTP request to Observations API",
                             request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
        self.last_response = r
        if r.ok:
            return r.json()
        else:
            return None

    def observations(self, searchFilter: SearchFilter,
                     skip: int = 0,
                     take: int = 100,  # Maximum is 1000
                     sortBy: str = DEFAULT_SORT_BY_ATTRIBUTE_FOR_OBSERVATIONS,
                     sort_descending: bool = True,
                     validateSearchFilter: bool = False,    # Validation will be done.
                     translationCultureCode: str = None,    # "sv-SE" or "en-GB"
                     # If the below is true, only sensitive observations will be searched
                     sensitiveObservations: bool = False):
        """Returns `take` observations starting at `skip` + 1 according to the criteria in
           the `search_filter` and the other request parameters.
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_ObservationsBySearch"""
        if sort_descending:
            sortOrder = 'Desc'
        else:
            sortOrder = 'Asc'
        url = self.search_url
        params = {"skip": skip,
                  "take": take,
                  "sortBy": sortBy,
                  "sortOrder": sortOrder,
                  "validateSearchFilter": validateSearchFilter,
                  "translationCultureCode": translationCultureCode}
        headers = self.headers | {"Content-Type": "application/json"}
        try:
            r = requests.post(url, params=params, headers=headers, data=searchFilter.json_string())
            logger.info("Call to artportalen.observations()",
                        extra={"attributes": {"searchFilter": searchFilter.filter,
                                              "skip": skip,
                                              "take": take,
                                              "sortBy": sortBy,
                                              "sort_descending": sort_descending,
                                              "validateSearchFilter": validateSearchFilter,
                                              "translationCultureCode": translationCultureCode,
                                              "sensitiveObservations": sensitiveObservations}})
            httplogs.log_request(logger,
                                 r,
                                 message="HTTP request to Observations API",
                                 request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
            self.last_response = r
            if r.ok:
                return r.json()
            else:
                return None
        except HTTPError as e:
            logger.warning("HTTPError in artportalen.observations()",
                           extra={"exception": e})
        except Exception as e:
            logger.error("Exception caught in artportalen.observations()",
                         exc_info=True,
                         extra={"exception": e})
            return None
        else:
            return r.json()

    def observations_by_georegion(self, from_date: str, to_date: str,
                                  region_type: str, region_name: str):
        """Returns the observations in a named geographical region."""

    def observations_by_geopolygon(self, from_date: str, to_date: str, polygon: list):
        """Returns the observations within a specified geographical polygon."""

    def observation_by_id(self, id: str, outputFieldSet: str):
        """Returns the observation with the given `id`, where `outputFieldSet` specifies how many
           attributes with values to return for the observation. `
           See: https://api-portal.artdatabanken.se/api-details#
           api=sos-api-v1&operation=Observations_GetObservationById"""
        if outputFieldSet not in API_OUTPUTFIELDSET_VALUES:
            return None
        url = self.observation_url.replace("{id}", id)
        params = {"outputFieldSet": outputFieldSet,
                  "translationCultureCode": "sv-SE",
                  "sensitiveObservations": "false",
                  "resolveGeneralizedObservations": "false"}
        headers = self.headers | {"Content-Type": "application/json"}
        try:
            r = requests.get(url, params=params, headers=headers)
            r.raise_for_status()
            logger.info("Call to artportalen.observation_by_id()",
                        extra={"attributes": {"id": id,
                                              "outputFieldSet": outputFieldSet}})
            httplogs.log_request(logger,
                                 r,
                                 message="HTTP request to Observations API",
                                 request_headers_to_strip_away=[API_KEY_HTTP_HEADER])
            self.last_response = r
        except HTTPError as e:
            logger.warning("HTTPError in artportalen.observation_by_id()",
                           extra={"exception": e})
        except Exception as e:
            logger.error("Exception caught in artportalen.observation_by_id()",
                         exc_info=True,
                         extra={"exception": e})
            return None
        else:
            return r.json()
