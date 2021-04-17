#!/usr/bin/env python


"""read_dir_fields.py: This script reads an SCEC ETAS forecast directory name
and extracts key fields that are then added as attributes in the SCEC Deriva
schema.

 This script is an example of how the ERD used by Deriva is extended as additional
 information or metadata is added to the asset descriptions in Deriva.

 This must be run after the create_model.py script has been run, because this modifies
 the ERD created by that script.
 
Philip Maechling
3 April 2021
"""
import os
import sys
from deriva.core import DerivaServer, ErmrestCatalog, get_credential
from deriva.chisel import Model, Schema, Table, Column, Key, ForeignKey, builtin_types, tag

if __name__ == "__main__":

    # Connect to server and catalog ------------------------------------------------------------------#

    hostname = 'forecast.derivacloud.org'  # this is a dev server for throw-away work (change to 'forecast.derivacloud.org)
    catalog_id = '5'  # this was a throw-away catalog used to test this script (change to TBD)

    model = Model.from_catalog(
        DerivaServer('https', hostname, credentials=get_credential(hostname)).connect_ermrest(catalog_id)
    )

    #
    # During testing, exit before any table modifications are done
    #


    tabname = model.schemas['ETAS'].tables["Forecast"]
    print("Before Adding Column")
    for column in tabname.column_definitions:
        print(column.name,column.type.typename,column.nullok)

    """
    Define a series of column names that reflect metadata we expect to extract from
    the ETAS directory names. These are initial names, defined by developers.
    ETAS modelers may want to rename these columns to be more meaningful to domain experts.
    For this first version, all fields are defined as free text.
    Redefinition of these values as controlled vocabularies are a future refinement.
    
    1) Sim_Start_Time: Enumeration List
    e.g: "2019_07_16"
    not null
    
    2) Catalog_Mag: Enumeration List
    e.g.: "ComCatM7p1"
    not null
    
    3) Event_ID: Enumeration List
    e.g.: "ci39457511"
    not null
    
    4) Post_Event_Date: Enumeration List
    e.g.: "7DaysAfter"
    maybe null
    
    5) Rupture_Def: Enumeration List
    e.g. "ShakeMapSurfaces"
    "ShakeMapSurfaces-noSpont-full_td-scale1.14"
    not null
    """


    tabname.create_column(Column.define('Sim_Start_Time',
                                        builtin_types.text,
                                        comment="Simulation Start Time"))

    tabname.create_column(Column.define('Catalog_Mag',
                                        builtin_types.text,
                                        comment="Catalog Name and Event Magnitude"))

    tabname.create_column(Column.define('Event_ID',
                                        builtin_types.text,
                                        comment="Earthquake Event ID"))

    tabname.create_column(Column.define('Post_Event_Date',
                                        builtin_types.text,
                                        comment="Days Forecast made after Mainshock"))

    tabname.create_column(Column.define('Rupture_Definition',
                                        builtin_types.text,
                                        comment="Type of Rupture used in ETAS forecast"))

    # retrieve catalog model again to ensure we reflect latest structural changes
    # example shows this, but I'm not sure what it returns
    print("After Adding Column")
    etas_model = model.schemas['ETAS']
    tabname = etas_model.tables["Forecast"]
    for column in tabname.column_definitions:
        print(column.name,column.type.typename,column.nullok)

    sys.exit(0)
