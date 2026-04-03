-- Create the table for observations. This is mapped from the JSON object structure and attributes
-- returned by the Artportalen API. Underscore characters '_' indicate JSON dictionary attributes.

CREATE TABLE IF NOT EXISTS observations (
  -- basisOfRecord
  basisOfRecord_id INTEGER,
  basisOfRecord_value VARCHAR,

  -- top-level
  collectionCode VARCHAR,
  dataProviderId INTEGER,
  datasetName VARCHAR,

  -- event
  event_discoveryMethod_id INTEGER,
  event_discoveryMethod_value VARCHAR,
  event_endDate TIMESTAMPTZ,
  event_plainEndDate DATE,
  event_plainStartDate DATE,
  event_startDate TIMESTAMPTZ,

  -- identification
  identification_uncertainIdentification BOOLEAN,
  identification_verificationStatus_id INTEGER,
  identification_verificationStatus_value VARCHAR,
  identification_verified BOOLEAN,

  -- location
  location_coordinateUncertaintyInMeters INTEGER,
  location_county_featureId VARCHAR,
  location_county_name VARCHAR,
  location_decimalLatitude DOUBLE,
  location_decimalLongitude DOUBLE,
  location_geodeticDatum VARCHAR,
  location_locality VARCHAR,
  location_locationId VARCHAR,
  location_municipality_featureId VARCHAR,
  location_municipality_name VARCHAR,
  location_parish_featureId VARCHAR,
  location_parish_name VARCHAR,
  location_province_featureId VARCHAR,
  location_province_name VARCHAR,
  location_sweref99TmX DOUBLE,
  location_sweref99TmY DOUBLE,

  -- modified
  modified TIMESTAMPTZ,

  -- occurrence
  occurrence_activity_id INTEGER,
  occurrence_activity_value VARCHAR,
  occurrence_individualCount VARCHAR,
  occurrence_isNaturalOccurrence BOOLEAN,
  occurrence_isNeverFoundObservation BOOLEAN,
  occurrence_isNotRediscoveredObservation BOOLEAN,
  occurrence_isPositiveObservation BOOLEAN,
  occurrence_lifeStage_id INTEGER,
  occurrence_lifeStage_value VARCHAR,

  occurrence_occurrenceId VARCHAR PRIMARY KEY,  -- unique key
  occurrence_occurrenceStatus_id INTEGER,
  occurrence_occurrenceStatus_value VARCHAR,
  occurrence_organismQuantity VARCHAR,
  occurrence_organismQuantityInt INTEGER,
  occurrence_recordedBy VARCHAR,
  occurrence_reportedBy VARCHAR,
  occurrence_sensitivityCategory INTEGER,
  occurrence_sex_id INTEGER,
  occurrence_sex_value VARCHAR,
  occurrence_url VARCHAR,

  -- other top-level
  ownerInstitutionCode VARCHAR,
  rightsHolder VARCHAR,

  -- taxon (top-level)
  taxon_class VARCHAR,
  taxon_family VARCHAR,
  taxon_genus VARCHAR,
  taxon_id INTEGER,
  taxon_kingdom VARCHAR,
  taxon_order VARCHAR,
  taxon_phylum VARCHAR,
  taxon_scientificName VARCHAR,
  taxon_taxonId VARCHAR,
  taxon_vernacularName VARCHAR,

  -- taxon.attributes
  taxon_attributes_isInvasiveAccordingToEuRegulation BOOLEAN,
  taxon_attributes_isInvasiveInSweden BOOLEAN,
  taxon_attributes_isRedlisted BOOLEAN,
  taxon_attributes_organismGroup VARCHAR,
  taxon_attributes_protectedByLaw BOOLEAN,
  taxon_attributes_redlistCategory VARCHAR,

  taxon_attributes_sensitivityCategory_id INTEGER,
  taxon_attributes_sensitivityCategory_value VARCHAR,

  taxon_attributes_taxonCategory_id INTEGER,
  taxon_attributes_taxonCategory_value VARCHAR
);

-- Create table for observations_recorded_by. This contains rows for all the persons listed as observers 
-- in the 'occurrence_recordedBy' column above.

CREATE TABLE IF NOT EXISTS observation_recorded_by (
  occurrence_occurrenceId VARCHAR,
  person_name VARCHAR,
  PRIMARY KEY (occurrence_occurrenceId, person_name)
);
