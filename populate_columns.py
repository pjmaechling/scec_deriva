#!/usr/bin/env python


"""populate_columns.py: This script reads the entries in a SCEC ETAS forecast directory,
extracts key fields that are then added as attributes in the SCEC Deriva schema.

This script has methods for decomposing ETAS directory names into metadata fields

Philip Maechling
17 April 2021
"""
import os
import sys
import json
from dataclasses import dataclass
from deriva.core import DerivaServer, ErmrestCatalog, get_credential
from deriva.chisel import Model, Schema, Table, Column, Key, ForeignKey, builtin_types, tag

"""
Define information collected from Filenames:
Assume format:
First string is SimStateDate: ends with -
After thatseparate individual fields

Simulation_Start_Time: Enumeration List
e.g: "2019_07_16"
not null

Catalog_Mag: Enumeration List
e.g.: "ComCatM7p1"
not null

Event_ID: Enumeration List
e.g.: "ci39457511"
not null

Post_Event_Date: Enumeration List
e.g.: "7DaysAfter"
null

Rupture_Def: Enumeration List
e.g. "ShakeMapSurfaces"
"ShakeMapSurfaces-noSpont-full_td-scale1.14"

"""

#
# These are the ETAS directory names we expect. However, this script reads these names from
# the entries in the Deriva db, rather than from this list.
# TODO : mark the deriva Forecast Filename as unique.
u3etas_files = [
    "2019_07_16-ComCatM7p1_ci38457511_7DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_07_27-ComCatM7p1_ci38457511_21DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_03-ComCatM7p1_ci38457511_28DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_19-ComCatM7p1_ci38457511_14DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_19-ComCatM7p1_ci38457511_35DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_19-ComCatM7p1_ci38457511_42DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_24-ComCatM7p1_ci38457511_49DaysAfter_ShakeMapSurfaces-noSpont-full_td-scale1.14",
    "2019_08_31-ComCatM7p1_ci38457511_56DaysAfter_ShakeMapSurfaces",
    "2019_09_04-ComCatM7p1_ci38457511_ShakeMapSurfaces",
    "2019_09_09-ComCatM7p1_ci38457511_63DaysAfter_ShakeMapSurfaces",
    "2019_09_16-ComCatM7p1_ci38457511_70DaysAfter_ShakeMapSurfaces"
]

def extract_sim_start_time(dir_name):
    """
    This assumes a convention that the first string is the sim start time,
    and this string ends with a -.
    It also assumes that worst case is this is the only - in the directory name
    so the number of split elements is always 2 or greater
    :param dir_name:
    :return: string which is first date the simulation started
    """
    elems = dir_name.split("-")
    if len(elems) < 2:
        print("Error parsing date from forecast dir name:{0}".format(dir_name))
    else:
        return elems[0]

def extract_cat_mag(dir_name):
    """
    This assumes that the catalog and mag are the first string that follow the
    sim start time. It must deal with two cases:
    ComCatM7p1_ci38457511_56DaysAfter_ShakeMapSurfaces
    ComCatM7p1_ci38457511_ShakeMapSurfaces
    ComCatM7p1_ci38457511_7DaysAfter_ShakeMapSurfaces
    It first splits off the sim_start_time using -
    This may split into two or three elements, depending on whether the name includes
    a rutpure definition, but we only need
    :param dir_name:
    :return: string
    """
    elems = dir_name.split("-")
    if len(elems) < 2:
        print("Error parsing Catalog+Mag info from forecast dir name:{0}".format(dir_name))
    else:
        forecast_info = elems[1].split("_")
        if len(forecast_info) < 3:
            print("Error parsing Catalog+mag info from forecast string:{0}".format(elems[1]))
        else:
            return forecast_info[0]

def extract_event_id(dir_name):
    """
    This uses the second element of the _ split to get a event ID
    :param dir_name:
    :return:
    """
    elems = dir_name.split("-")
    if len(elems) < 2:
        print("Error parsing event id from forecast dir name:{0}".format(dir_name))
    else:
        forecast_info = elems[1].split("_")
        if len(forecast_info) == 3 or len(forecast_info) == 4:
            return forecast_info[1]
        else:
            print("Error parsing event id from forecast string:{0}".format(elems[1]))

def extract_post_event_date(dir_name):
    """
    This tests how many elements are found when a split using _ is done.
    If this split returns only 3 elements, then the directory name does not include a post_event_date
    so this returns a null
    :param dir_name:
    :return:
    """
    elems = dir_name.split("-")
    if len(elems) < 2:
        print("Error parsing post event date info from forecast dir name:{0}".format(dir_name))
    else:
        forecast_info = elems[1].split("_")
        if len(forecast_info) == 3:
            return ""
        elif len(forecast_info) == 4:
            return forecast_info[2]
        else:
            print("Error parsing post event date info from forecast string:{0}".format(elems[1]))
            return None

def extract_rupture_def(dir_name):
    """
    This method uses two different splits, first split on -
    Then split on _
    :param dir_name:
    :return:
    """
    elems = dir_name.split("-")
    """
    This first split will catch cases that have only two - in the file name
    In this case, we split the second element using underscores and
    get the last elements, which we expect to be "ShakeMapSurfaces"
    """
    if len(elems) == 2:
        nelems = elems[1].split("_")
        if len(nelems) == 3:
            return nelems[2]
        elif len(nelems) == 4:
            return nelems[3]
        else:
            print("Error parsing rupture definition from {0}".format(dir_name))
            print(nelems)
    elif len(elems) == 5:
        """
        This second split finds cases which end with several dashes.
        In this case we need to split the second element and extract the last entry, which should
        be "ShakeMap, then we need to add that to the other elements found
        """
        nelems = elems[1].split("_")
        # this syntax is supposed to be the last entry in the list
        p1_rup_string = "{0}".format(nelems[-1])
        ret_string = "{0}-{1}-{2}-{3}".format(p1_rup_string,elems[2],elems[3],elems[4])
        return ret_string
    else:
        print("Error parsing rupture_def from string:{0}".format(dir_name))

@dataclass
class ETAS_metadata:
    sim_start_time: str
    catalog_mag: str
    event_id: str
    post_event_date: str
    rupture_def: str
    RID: str

if __name__ == "__main__":
    """
    Script that creates a dictionary with key of forecast_name, and a dataclass
    with entries for the metadata we extracted from it.
    """

    column_metadata = {}

    #
    # This first example tests the metadata extraction code, and creates a dictionary
    # This test code and isn't needed when running against Deriva instance
    #
    files =  u3etas_files
    for name in files:
        if name.startswith("."):
            continue
        else:
            sim_start_time = extract_sim_start_time(name)
            catalog_mag = extract_cat_mag(name)
            event_id = extract_event_id(name)
            post_event_date = extract_post_event_date(name)
            rupture_def = extract_rupture_def(name)
            rid = "" # Define the RID as an empty string for now

            mdata = ETAS_metadata(sim_start_time,
                                  catalog_mag,
                                  event_id,
                                  post_event_date,
                                  rupture_def,
                                  rid)

            column_metadata[name] = mdata


    # print("Results:")
    # for x in column_metadata:
    #    print("Key: {0} Values: {1}".format(x,column_metadata[x]))
    #
    # End test code for extracting metadata from directory names

    # Connect to server and catalog ------------------------------------------------------------------#

    hostname = 'forecast.derivacloud.org'  # this is a dev server for throw-away work (change to 'forecast.derivacloud.org)
    catalog_id = '5'  # this was a throw-away catalog used to test this script (change to TBD)

    model = Model.from_catalog(
        DerivaServer('https', hostname, credentials=get_credential(hostname)).connect_ermrest(catalog_id)
    )

    catalog = ErmrestCatalog('https', hostname, catalog_id, credentials=get_credential((hostname)))

    # Use the pathbuilder approach
    pb = catalog.getPathBuilder()
    etas = pb.schemas["ETAS"]
    #
    # print("Schema: ETAS - table keys:",etas.tables.keys())
    #
    # Query the ETAS Forecast Table to get column names
    # The dataset object is used for updates
    # The dataset path object is used to run the query and get the resultset
    dataset = pb.schemas["ETAS"].tables["Forecast"]
    # print("Dataset columns:",dataset.column_definitions.keys())
    fcast = dataset.path
    results = fcast.entities()
    entities = results.fetch()

    #
    # Results from retrieved entities
    print("Result set len - forecast table entities",len(entities))
    print("List entities before Update:",list(entities))

    # This first resultset should contain contain empty strings for the metadata fields we plan to add
    # Iterate through the result set, extract the forecast name, and extract the metadata fiels
    #
    # Declare updated entiries object here for visibility
    updated_entities = None

    for idx in range(len(entities)):
        print(entities[idx],entities[idx]["RID"],entities[idx]["Forecast_Name"])
        fname = entities[idx]["Forecast_Name"]

        sim_start_time = extract_sim_start_time(fname)
        catalog_mag = extract_cat_mag(fname)
        event_id = extract_event_id(fname)
        post_event_date = extract_post_event_date(fname)
        rupture_def = extract_rupture_def(fname)
        rid = entities[idx]["RID"]

        #
        # Now prepare update to current entities with metadata extracted
        # from directory name. create a json row values
        # newvals = {}
        # newvals["Sim_Start_Time"] = sim_start_time
        # newvals["Catalog_Mag"] = catalog_mag
        # newvals["Event_ID"] = event_id
        # newvals["Post_Event_Date"] = post_event_date
        # newvals["Rupture_Definition"] = rupture_def
        # newvals["RID"] = rid
        # json_update = json.dumps(newvals)
        # print(json_update)
        #
        # Alternative update method for comparison
        # TODO : ask for preferred update method
        entities[idx]["Sim_Start_Time"] = sim_start_time
        entities[idx]["Catalog_Mag"] = catalog_mag
        entities[idx]["Event_ID"] = event_id
        entities[idx]["Post_Event_Date"] = post_event_date
        entities[idx]["Rupture_Definition"] = rupture_def
        entities[idx]["RID"] = rid
        updated_entities = dataset.update(entities)

    #
    # Now we have a dictionary with key of the forecast directory name, and an RID number.
    # We update the columns with the extracted metadata
    # Results from retrieved entities
    print("Result set len - forecast table entities",len(updated_entities))
    print("List entities before Update:",list(updated_entities))

    sys.exit(0)

"""
These are notes that define the metadata fields that will be extracted from the
ETAS directory names.

Sim_Start_Time: Enumeration List
e.g: "2019_07_16"
not null

Catalog_Mag: Enumeration List
e.g.: "ComCatM7p1"
not null

Event_ID: Enumeration List
e.g.: "ci39457511"
not null

Post_Event_Date: Enumeration List
e.g.: "7DaysAfter"
null

Rupture_Definition: Enumeration List
e.g. "ShakeMapSurfaces"
"ShakeMapSurfaces-noSpont-full_td-scale1.14"

Here is an example of update: http://docs.derivacloud.org/deriva-py/derivapy-datapath-update.html
"""
