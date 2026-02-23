"""
Provides the class ArtportalenProvider which encapsulates the code for calling the Artportalen
API:s and also provides features for accessing Artportalen data, both via API calls and calls to
the local Artportalen cache database.
"""

from enum import StrEnum
from requests.exceptions import HTTPError
from app.mapping import MappingService
from . import client


class Vocabulary(StrEnum):
    SEX = "sex"


class Language(StrEnum):
    SV = "sv"
    EN = "en"


class ArtportalenProvider():
    """The high level interface to Artportalen for the web app."""
    def __init__(self, *, settings, logger):
        self.settings = settings
        self.logger = logger

        # Set up the API objects
        v = self.settings.ARTPORTALEN_SPECIES_API_KEY.get_secret_value()
        self.sapi = client.SpeciesAPI(v)
        v = self.settings.ARTPORTALEN_OBSERVATIONS_API_KEY.get_secret_value()
        self.oapi = client.ObservationsAPI(v)

    def get_observations(self,
                         mapping: MappingService,
                         area_name: str,
                         from_date: str,
                         to_date: str,
                         taxon_name: str = None,
                         observer_name: str = None):
        """Get observations from Artportalen API."""
        # Get the taxa ids that match the given `taxon_name`.
        taxon_ids = [self.settings.DEFAULT_TAXON_SEARCH_ID]
        if taxon_name:
            taxa = self.sapi.taxa_by_name(taxon_name,
                                          exact_match=True)
            if not taxa:
                self.settings.debug((f"No taxa matching {taxon_name}"),
                                    ("found in Artportalen Species API"))
            else:
                taxon_ids = [t["taxonId"] for t in taxa]

        # Set up the search filter for the Artportalen Observations API
        sfilter = client.SearchFilter()
        sfilter.set_taxon(ids=taxon_ids)

        area = mapping.area_by_name(area_name)
        polygon = area.geopolygons[0].serialize_as_list()
        sfilter.set_geographics_geometries(geometries=[{"type": "polygon",
                                                        "coordinates": [polygon]}])
        sfilter.set_verification_status()
        sfilter.set_output(fieldSet="Extended")
        sfilter.set_date(startDate=from_date,
                         endDate=to_date,
                         dateFilterType="OverlappingStartDateAndEndDate",
                         timeRanges=[])
        sfilter.set_modified_date()
        sfilter.set_dataProvider()
        try:
            observations = self.oapi.observations(sfilter,
                                                  skip=0,
                                                  take=1000,
                                                  sort_descending=True)
        except HTTPError as e:
            self.logger.warning("HTTPError in artportalen.observations()",
                                extra={"exception": e})
            return None

        return observations

    def vocabulary_term(self,
                        code: int,
                        vocabulary: Vocabulary = Vocabulary.SEX,
                        language: Language = Language.SV) -> str:
        """The term in the given `vocabulary` associated with the given `code` and `language`."""
        if vocabulary == Vocabulary.SEX:
            if language in [Language.EN, Language.SV]:
                return client.vocabulary_sex[code][language]
            else:
                msg = f"Unrecognized language '{language}' in vocabulary '{vocabulary}'"
                self.logger.warning(msg)
        else:
            msg = f"Unrecognized vocabulary '{vocabulary}'"
            self.logger.warning(msg)
