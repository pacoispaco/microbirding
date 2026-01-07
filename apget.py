#!/usr/bin/env python3

"""This is a simple CLI program that gets stuff from the Artdatabanken Observations API and Species
API and prints it to stdout."""

import sys
import argparse
import json
import os
import os.path
from datetime import datetime
import dateutil.parser
import pprint
import artportalen

# Constants
DEFAULT_CONF_FILE_PATH = 'adb-get.conf'
DEFAULT_FROM_DATE_RFC3339 = '1900-01-01T00:00'
DEFAULT_CSV_FILE_PATH = 'artdatabanken-data.csv'
ADB_SPECIES_API_KEY_ENV_NAME = 'ARTPORTALEN_SPECIES_API_KEY'
ADB_OBSERVATIONS_API_KEY_ENV_NAME = 'ARTPORTALEN_OBSERVATIONS_API_KEY'
ADB_API_ROOT_URL = 'https://api.artdatabanken.se'
ADB_SPECIES_API_PATH = '/information/v1/speciesdataservice/v1/'
ADB_OBSERVATIONS_API_PATH = '/species-observation-system/v1/Observations/Search'
ADB_COORDINATSYSTEM_WGS_84_ID = 10
AVES_TAXON_ID = 4000104


def species_api_key():
    """Value of the Species API key environment variable if it is set, otherwise None."""
    if ADB_SPECIES_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_SPECIES_API_KEY_ENV_NAME]
    else:
        return None


def observations_api_key():
    """Value of the Species API key environment variable if it is set, otherwise None."""
    if ADB_OBSERVATIONS_API_KEY_ENV_NAME in os.environ:
        return os.environ[ADB_OBSERVATIONS_API_KEY_ENV_NAME]
    else:
        return None


def pretty_print_taxon(t, redlistinfo=False):
    """Pretty print the taxon 't' to stdout."""
    print("Taxon: %s (%s) taxon id: %s" % (t['swedishName'].capitalize(),
                                           t['scientificName'],
                                           t['taxonId']))
    swedishPresence = t['speciesData']['taxonRelatedInformation']['swedishPresence']
    immigrationHistory = t['speciesData']['taxonRelatedInformation']['immigrationHistory']
    print(" Förekomst: %s (%s)" % (swedishPresence, immigrationHistory))
    if redlistinfo:
        for item in t['speciesData']['redlistInfo']:
            print("%s:" % (item['period']['name']))
            print(" Kategori: %s" % (item['category']))
            print(" Text: %s" % (item['criterionText']))


def pretty_print_observation(o):
    """Pretty print the observation 'o' to stdout."""
    print(f" Art: {o['taxon']['vernacularName']}, {o['taxon']['scientificName']}")
    fdate = dateutil.parser.parse(o['event']['startDate'])
    edate = dateutil.parser.parse(o['event']['endDate'])
    if fdate != edate:
        if fdate.hour != 0 and fdate.minute != 0 and edate.hour != 0 and edate.minute != 0:
            print(" Datum: %s %s-%s" % ('{:%Y-%m-%d}'.format(fdate),
                  '{:%H:%M}'.format(fdate),
                  '{:%H:%M}'.format(edate)))
        else:
            print(" Datum: %s" % ('{:%Y-%m-%d}'.format(fdate)))
    else:
        if fdate.hour != 0 and fdate.minute != 0:
            print(" Datum: %s" % ('{:%Y-%m-%d %H:%M}'.format(fdate)))
        else:
            print(" Datum: %s" % ('{:%Y-%m-%d}'.format(fdate)))
    print(" Rapporterad av: %s" % (o['occurrence']['recordedBy']))
    print(" Medobservatörer: %s" % (o['occurrence']['reportedBy']))
    print(" Var: %s" % (o['location']))
    # Get WGS 84 coordinates so we can create URL:s for Google Maps and Open Street Map
    latitude = o['location']['decimalLatitude']
    longitude = o['location']['decimalLongitude']
    print(f" Latitude: {latitude}")
    print(f" Longitude: {longitude}")
    gm_url = "https://www.google.com/maps/search/?api=1&query=%s,%s" % (latitude, longitude)
    osm_url = "https://www.openstreetmap.org/?mlat=%s&mlon=%s" % (latitude, longitude)
    print(" Google Maps location: %s" % (gm_url))
    print(" Open Street Maps location: %s" % (osm_url))
#    print(" Google Maps location: %s" % ("https://www.google.com/maps/@?api=1&
# map_action=map&center=56.711061,16.3535513&zoom=12&basemap=terrain"))
#    print(" Open Street Maps location: %s" % ("https://www.openstreetmap.org/?
# mlat=-38.3653&mlon=144.9069#map=9/-38.3653/144.9069"))


def csv_print_header():
    """Print header for CSV file output."""
    csv_header = ("collectionCode#"
                  "dataProviderId#"
                  "datasetName#"
                  "ownerInstitutionCode#"
                  "basisOfRecord.id#"
                  "basisOfRecord.value#"
                  "ownerInstitutionCode#"
                  "rightsHolder#"
                  "modified#"
                  "identification.uncertainIdentification#"
                  "identification.verificationStatus.id#"
                  "identification.verificationStatus.value#"
                  "identification.verified#"
                  "event.discoveryMethod.id#"
                  "event.discoveryMethod.value#"
                  "event.startDate#"
                  "event.endDate#"
                  "event.plainStartDate#"
                  "event.plainEndTime#"
                  "event.plainEndDate#"
                  "event.plainEndTime#"
                  "occurrence.activity.id#"
                  "occurrence.activity.value#"
                  "occurrence.individualCount#"
                  "occurrence.isNaturalOccurrence#"
                  "occurrence.isNeverFoundObservation#"
                  "occurrence.isNotRediscoveredObservation#"
                  "occurrence.isPositiveObservation#"
                  "occurrence.lifeStage.id#"
                  "occurrence.lifeStage.value#"
                  "occurrence.occurrenceId#"
                  "occurrence.occurrenceStatus.id#"
                  "occurrence.occurrenceStatus.value#"
                  "occurrence.organismQuantity#"
                  "occurrence.recordedBy#"
                  "occurrence.reportedBy#"
                  "occurrence.sensitivityCategory#"
                  "occurrence.sex.id#"
                  "occurrence.sex.value#"
                  "occurrence.url#"
                  "location.coordinateUncertaintyInMeters#"
                  "location.county.featureId#"
                  "location.county.name#"
                  "location.decimalLatitude#"
                  "location.decimalLongitude#"
                  "location.geodeticDatum#"
                  "location.locality#"
                  "location.locationId#"
                  "location.municipality.featureId#"
                  "location.municipality.name#"
                  "location.parish.featureId#"
                  "location.parish.name#"
                  "location.province.featureId#"
                  "location.province.name#"
                  "location.sweref99TmX#"
                  "location.sweref99TmY#"
                  "taxon.attributes.isInvasiveAccordingToEuRegulation#"
                  "taxon.attributes.isInvasiveInSweden#"
                  "taxon.attributes.isRedlisted#"
                  "taxon.attributes.organismGroup#"
                  "taxon.attributes.protectedByLaw#"
                  "taxon.attributes.redlistCategory#"
                  "taxon.attributes.sensitivityCategory.id#"
                  "taxon.attributes.sensitivityCategory.value#"
                  "taxon.attributes.taxonCategory.id#"
                  "taxon.attributes.taxonCategory.value#"
                  "taxon.class#"
                  "taxon.family#"
                  "taxon.genus#"
                  "taxon.id#"
                  "taxon.kingdom#"
                  "taxon.order#"
                  "taxon.phylum#"
                  "taxon.scientificName#"
                  "taxon.taxonId#"
                  "taxon.vernacularName#")
    print(csv_header)


def csv_print_observation(o):
    """Print observation 'o' to stdout as a CSV row."""
    if 'ownerInstitutionCode' not in o:
        o['ownerInstitutionCode'] = ""
    if 'discoveryMethod' not in o['event'].keys():
        o['event']['discoveryMethod'] = {'id': "", 'value': ""}
    if 'plainEndTime' not in o['event'].keys():
        o['event']['plainEndTime'] = ""
    if 'activity' not in o['occurrence'].keys():
        o['occurrence']['activity'] = {'id': "", 'value': ""}
    if 'lifeStage' not in o['occurrence'].keys():
        o['occurrence']['lifeStage'] = {'id': "", 'value': ""}
    if 'sex' not in o['occurrence'].keys():
        o['occurrence']['sex'] = {'id': "", 'value': ""}
    if 'recordedBy' not in o['occurrence'].keys():
        o['occurrence']['recordedBy'] = ""
    if 'reportedBy' not in o['occurrence'].keys():
        o['occurrence']['reportedBy'] = ""
    if 'url' not in o['occurrence'].keys():
        o['occurrence']['url'] = ""
    if 'individualCount' not in o['occurrence']:
        o['occurrence']['individualCount'] = ""
    if 'organismQuantity' not in o['occurrence']:
        o['occurrence']['organismQuantity'] = ""
    if 'sensitivityCategory' not in o['taxon']['attributes'].keys():
        o['taxon']['attributes']['sensitivityCategory'] = {'id': "", 'value': ""}
    if 'vernacularName' not in o['taxon']:
        o['taxon']['vernacularName'] = ""
    if 'verificationStatus' not in o['identification']:
        o['identification']['verificationStatus'] = {'id': "", 'value': ""}
    if 'collectionCode' not in o:
        o['collectionCode'] = ""
    if 'rightsHolder' not in o:
        o['rightsHolder'] = ""
    if 'locationId' not in o['location']:
        o['location']['locationId'] = ""
    if 'locality' not in o['location']:
        o['location']['locality'] = ""
#        pprint.pprint(o)
    print((f"{o['collectionCode']}#"
           f"{o['dataProviderId']}#"
           f"{o['datasetName']}#"
           f"{o['ownerInstitutionCode']}#"
           f"{o['basisOfRecord']['id']}#"
           f"{o['basisOfRecord']['value']}#"
           f"{o['ownerInstitutionCode']}#"
           f"{o['rightsHolder']}#"
           f"{o['modified']}#"
           f"{o['identification']['uncertainIdentification']}#"
           f"{o['identification']['verificationStatus']['id']}#"
           f"{o['identification']['verificationStatus']['value']}#"
           f"{o['identification']['verified']}#"
           f"{o['event']['discoveryMethod']['id']}#"
           f"{o['event']['discoveryMethod']['value']}#"
           f"{o['event']['startDate']}#"
           f"{o['event']['endDate']}#"
           f"{o['event']['plainStartDate']}#"
           f"{o['event']['plainEndTime']}#"
           f"{o['event']['plainEndDate']}#"
           f"{o['event']['plainEndTime']}#"
           f"{o['occurrence']['activity']['id']}#"
           f"{o['occurrence']['activity']['value']}#"
           f"{o['occurrence']['individualCount']}#"
           f"{o['occurrence']['isNaturalOccurrence']}#"
           f"{o['occurrence']['isNeverFoundObservation']}#"
           f"{o['occurrence']['isNotRediscoveredObservation']}#"
           f"{o['occurrence']['isPositiveObservation']}#"
           f"{o['occurrence']['lifeStage']['id']}#"
           f"{o['occurrence']['lifeStage']['value']}#"
           f"{o['occurrence']['occurrenceId']}#"
           f"{o['occurrence']['occurrenceStatus']['id']}#"
           f"{o['occurrence']['occurrenceStatus']['value']}#"
           f"{o['occurrence']['organismQuantity']}#"
           f"{o['occurrence']['recordedBy']}#"
           f"{o['occurrence']['reportedBy']}#"
           f"{o['occurrence']['sensitivityCategory']}#"
           f"{o['occurrence']['sex']['id']}#"
           f"{o['occurrence']['sex']['value']}#"
           f"{o['occurrence']['url']}#"
           f"{o['location']['coordinateUncertaintyInMeters']}#"
           f"{o['location']['county']['featureId']}#"
           f"{o['location']['county']['name']}#"
           f"{o['location']['decimalLatitude']}#"
           f"{o['location']['decimalLongitude']}#"
           f"{o['location']['geodeticDatum']}#"
           f"{o['location']['locality']}#"
           f"{o['location']['locationId']}#"
           f"{o['location']['municipality']['featureId']}#"
           f"{o['location']['municipality']['name']}#"
           f"{o['location']['parish']['featureId']}#"
           f"{o['location']['parish']['name']}#"
           f"{o['location']['province']['featureId']}#"
           f"{o['location']['province']['name']}#"
           f"{o['location']['sweref99TmX']}#"
           f"{o['location']['sweref99TmY']}#"
           f"{o['taxon']['attributes']['isInvasiveAccordingToEuRegulation']}#"
           f"{o['taxon']['attributes']['isInvasiveInSweden']}#"
           f"{o['taxon']['attributes']['isRedlisted']}#"
           f"{o['taxon']['attributes']['organismGroup']}#"
           f"{o['taxon']['attributes']['protectedByLaw']}#"
           f"{o['taxon']['attributes']['redlistCategory']}#"
           f"{o['taxon']['attributes']['sensitivityCategory']['id']}#"
           f"{o['taxon']['attributes']['sensitivityCategory']['value']}#"
           f"{o['taxon']['attributes']['taxonCategory']['id']}#"
           f"{o['taxon']['attributes']['taxonCategory']['value']}#"
           f"{o['taxon']['class']}#"
           f"{o['taxon']['family']}#"
           f"{o['taxon']['genus']}#"
           f"{o['taxon']['id']}#"
           f"{o['taxon']['kingdom']}#"
           f"{o['taxon']['order']}#"
           f"{o['taxon']['phylum']}#"
           f"{o['taxon']['scientificName']}#"
           f"{o['taxon']['taxonId']}#"
           f"{o['taxon']['vernacularName']}#"))


def get_observations(oapi, sapi, args):
    """Return the observations."""
    taxon_ids = None
    if args.taxon_name:
        taxa = sapi.taxa_by_name(args.taxon_name,
                                 exact_match=args.exact_match)
        if not taxa:
            errmsg = (f"Error: No taxon with name '{args.taxon_name}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(3)
        else:
            taxon_ids = [taxon["taxonId"] for taxon in taxa]
    elif args.taxon_id:
        taxon = sapi.taxon_by_id(args.taxon_id,
                                 verbose=args.verbose)
        if not taxon:
            errmsg = (f"Error: No taxon with id '{args.taxon_id}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(4)
        else:
            taxon_ids = [args.taxon_id]

    sfilter = artportalen.SearchFilter()
    if args.polygon_file:
        p = polygon(args.polygon_file)
        print(p)
        if p:
            sfilter.set_geographics_geometries(geometries=[{"type": "polygon",
                                                            "coordinates": [p]}])
        else:
            sys.exit(5)
    else:
        sfilter.set_geographics_areas(areas=[{"area_type": "Municipality",
                                              "featureId": "180"}])
    sfilter.set_verification_status()
    sfilter.set_output("Extended")
    sfilter.set_date(startDate=args.from_date,
                     endDate=args.to_date,
                     dateFilterType="OverlappingStartDateAndEndDate",
                     timeRanges=[])
    sfilter.set_modified_date()
    sfilter.set_dataProvider()
    if taxon_ids:
        sfilter.set_taxon(ids=taxon_ids)
    result = oapi.observations(sfilter,
                               skip=args.offset,
                               take=args.limit,
                               sort_descending=not args.sort_reverse)
    if args.show_search_filter:
        print("==============")
        print("Search filter:")
        pprint.pprint(sfilter.filter)
    return result


def get_all_observations(oapi, sapi, args):
    """Return all observations between args.from_date and args.to_date. If they are not given
       then between 1900-01-01 and the current date."""
    p = polygon(args.polygon_file)
    if not p:
        sys.exit(5)
    taxon_ids = [AVES_TAXON_ID]
    fd = datetime.fromisoformat(args.from_date)
    td = datetime.fromisoformat(args.to_date)
    obtir = artportalen.ObservationsByTimeIntervalRequester(oapi, p, fd, td, taxon_ids)
    if args.print_csv_data_file:
        csv_print_header()
    i = 1
    for o in obtir.observations():
        if args.print_csv_data_file:
            csv_print_observation(o)
        else:
            print(o)
        i += 1


def today_RFC3339():
    """Today as an RFC 3339 / ISO 8601 date and time string, in minute resolution."""
    today = datetime.now()
    return today.isoformat(timespec='minutes')


def polygon(filename):
    """Return a list of polygon coordinates in WGS84 from the file `filename`. Return None if it
       fails."""
    result = None
    if not os.path.exists(filename):
        print(f"Error: Polygon file '{filename}' does not exist.")
    else:
        with open(filename) as f:
            try:
                result = json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Error: Polygon file '{filename}' is not a valid JSON file.")
    return result


def main():
    desc = """CLI-program for getting stuff from the Artdatabanken API:s. To actually get
observations you must use the -g flag. Note that you must set the
two API keys as environment variables. Ie:
export ADB_SPECIES_API_KEY=<API-KEY>
export ADB_OBSERVATIONS_API_KEY=<API-KEY>"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False].")
    parser.add_argument('-c', '--conf-file-path', default=DEFAULT_CONF_FILE_PATH,
                        help="Configuration file path [%s]." % (DEFAULT_CONF_FILE_PATH))
    parser.add_argument('--taxon-id',
                        help="Artdatabanken's taxon id")
    parser.add_argument('--taxon-name',
                        help="Artdatabanken's taxon name in Swedish")
    parser.add_argument('--exact-match', action='store_true', default=False,
                        help="Do exact match on taxon name [False]")
    parser.add_argument('--print-full-taxon-info', action='store_true', default=False,
                        help="Print full info on every taxon when searching on taxon name [False]")
    parser.add_argument('--pretty-print', action='store_true', default=False,
                        help="Pretty print all info.")
    parser.add_argument('--output-csv-file', default=DEFAULT_CSV_FILE_PATH,
                        help="Output CSV file [%s]." % (DEFAULT_CSV_FILE_PATH))
    parser.add_argument('-d', '--print-csv-data-file', action='store_true', default=False,
                        help="Print output as a CSV data file with '#' as separator.")
    parser.add_argument('-V', '--get-api-versions', action='store_true', default=False,
                        help="Get API versions.")
    parser.add_argument('-g', '--get-observations', action='store_true', default=False,
                        help="Get observations [False]")
    parser.add_argument('--get-all-observations', action='store_true', default=False,
                        help="Get all observations [False]")
    parser.add_argument('-s', '--show-search-filter', action='store_true', default=False,
                        help="Show the search filter used [False]. Use with '-g'")
    parser.add_argument('-r', '--sort-reverse', action='store_true', default=False,
                        help="Sort observations in reverse order [False]")
    parser.add_argument('--from-date', default=DEFAULT_FROM_DATE_RFC3339,
                        help="From date [%s]" % (DEFAULT_FROM_DATE_RFC3339))
    s = today_RFC3339()
    parser.add_argument('--to-date', default=s,
                        help="To date [%s]" % (s))
    parser.add_argument('--offset', default=0,
                        help="Offset for observations [0]")
    parser.add_argument('--limit', default=200,
                        help="Limit of observations [200]")
    parser.add_argument('--polygon-file',
                        help="Polygon file to use for getting observations. It must contain a\
                              JSON list of WGS85 coordinates and the first and last coordinates\
                              must be the same")
    args = parser.parse_args()
    if not species_api_key():
        print("Error: Environment variable ARTPORTALEN_SPECIES_API_KEY not set.")
        sys.exit(1)
    if not observations_api_key():
        print("Error: Environment variable ARTPORTALEN_OBSERVATIONS_API_KEY not set.")
        sys.exit(1)
    sapi = artportalen.SpeciesAPI(species_api_key())
    oapi = artportalen.ObservationsAPI(observations_api_key())
    if args.get_api_versions:
        v = oapi.version(args.verbose)
        print("Observations API:")
        pprint.pprint(v)
        print("Species API: No API resource for version")
        sys.exit(0)
    if args.taxon_name and args.taxon_id:
        print("Error: Flags --taxon-name and --taxon-id cannot be used at the same time.")
        sys.exit(1)
    if args.taxon_name:
        taxa = sapi.taxa_by_name(args.taxon_name,
                                 exact_match=args.exact_match)
        if not taxa:
            errmsg = (f"No taxon/taxa with name '{args.taxon_name}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(4)
        if not args.get_observations:
            # Then we print info on the named taxon/taxa
            if args.print_full_taxon_info:
                for taxon in taxa:
                    taxon_data = sapi.taxon_by_id(taxon['taxonId'],
                                                  verbose=args.verbose)
                    if args.pretty_print:
                        pretty_print_taxon(taxon_data[0])
                    else:
                        pprint.pprint(taxon_data)
            else:
                pprint.pprint(taxa)
            print(f"Number of taxa: {len(taxa)}")
    if args.taxon_id:
        taxon_data = sapi.taxon_by_id(args.taxon_id,
                                      verbose=args.verbose)
        if not taxon_data:
            errmsg = (f"No taxon with id '{args.taxon_id}' found "
                      "in Artdatabankens Species API.")
            print(errmsg)
            sys.exit(5)
        if not args.get_observations:
            # Then we print info on the taxon
            if args.pretty_print:
                [pretty_print_taxon(t) for t in taxon_data]
            else:
                pprint.pprint(taxon_data)
    if args.polygon_file and not (args.get_observations or args.get_all_observations):
        print(("Error: --polygon-file flag can only be used with "
               "-g or --get-all-observations flag."))
        sys.exit(6)
    if args.get_observations:
        result = get_observations(oapi, sapi, args)
        if args.pretty_print:
            [pretty_print_observation(r) for r in result["records"]]
        elif args.print_csv_data_file:
            csv_print_header()
            [csv_print_observation(r) for r in result["records"]]
        else:
            pprint.pprint(result)
        sys.exit(0)
    if args.get_all_observations:
        get_all_observations(oapi, sapi, args)
        sys.exit(0)


if __name__ == '__main__':
    main()
