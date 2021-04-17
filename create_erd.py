"""Minimal example of a possible rendering of the ETAS starter model.
Developer: Robert Schuler
Modifications: Philip Maechling
"""
from deriva.core import DerivaServer, get_credential
from deriva.chisel import Model, Schema, Table, Column, Key, ForeignKey, builtin_types, tag
import sys

# Press the green button in the gutter to run the script.

# Connect to server and catalog ------------------------------------------------------------------#

hostname = 'forecast.derivacloud.org'   # this is a dev server for throw-away work (change to 'forecast.derivacloud.org)
catalog_id = '5'            # this was a throw-away catalog used to test this script (change to TBD)

model = Model.from_catalog(
    DerivaServer('https', hostname, credentials=get_credential(hostname)).connect_ermrest(catalog_id)
)

# Cleanup ----------------------------------------------------------------------------------------#

if 'ETAS' in model.schemas:
    # Purge anything so we can "do over" repeatedly at this point
    model.schemas['ETAS'].drop(cascade=True)


# ETAS schema ------------------------------------------------------------------------------------#

# Create the "schema" to organize tables in the catalog "model"
model.create_schema(Schema.define('ETAS'))

# ETAS Forecast ----------------------------------------------------------------------------------#

# Create the tables at the "Forecast" level of the table hierarchy

# ETAS_Forecast
model.schemas['ETAS'].create_table(Table.define(  # <--- 'Table.define(...)' defines a general-purpose table
    'ETAS_Forecast',                                                        # table name
    column_defs=[                                                           # column definitions
        Column.define('Forecast_Name', builtin_types.text, nullok=False),   # column for the name of the forecast
    ],
    key_defs=[                                                              # key definitions
        Key.define(['Forecast_Name'])                                       # each key specifies its list of columns of 1+ columns
    ]
))


# ETAS_Forecast_File
#  This is for storing the 'forecast_config.json', 'slurm_log', 'slurm_stdout', and 'slurm_stderr'
model.schemas['ETAS'].create_table(Table.define_asset(  # <--- 'Table.define_asset(...)' defines a table for storing files
    'ETAS', 'ETAS_Forecast_File',                                           # schema_name, table_name
    column_defs=[                                                           # column definitions
        Column.define('ETAS_Forecast', builtin_types.ermrest_rid)           # a key we will use as fkey column
    ],
    fkey_defs=[                                                             # foreign key definitions
        ForeignKey.define(                                                  # this FKey will reference ETAS_Forecast row
            ['ETAS_Forecast'],                                              # fkey columns: list of 1+ column(s) from this table
            'ETAS', 'ETAS_Forecast', ['RID']                                # referenced key: schema name, table name, and list of 1+ key columns
        )
    ]
))


# ETAS Evaluation --------------------------------------------------------------------------------#

# Create the tables at the "Evaluation" level of the table hierarchy

# ETAS_Evaluation
model.schemas['ETAS'].create_table(Table.define(
    'ETAS_Evaluation',
    column_defs=[
        Column.define('Evaluation_Description', builtin_types.text),        # free-text description
        Column.define('ETAS_Forecast', builtin_types.ermrest_rid)           # foreign key column
    ],
    fkey_defs=[
        ForeignKey.define(  # this FKey will reference the ETAS_Forecast table
            ['ETAS_Forecast'],                                              # foreign key column (list allows 1+)
            'ETAS', 'ETAS_Forecast', ['RID']                                # referenced schema, table, columns
        )
    ]
))


# ETAS_Evaluation_File
#  This is to store the readme.md, meta.json, config.json, evaluation_catalog.json files (one file reference per row)
model.schemas['ETAS'].create_table(Table.define_asset(
    'ETAS', 'ETAS_Evaluation_File',
    column_defs=[
        Column.define('ETAS_Evaluation', builtin_types.ermrest_rid)         # foreign key column
    ],
    fkey_defs=[
        ForeignKey.define(  # This FKey will reference the ETAS_Evaluation table
            ['ETAS_Evaluation'],
            'ETAS', 'ETAS_Evaluation', ['RID']
        )
    ]
))


# ETAS_Evaluation_Result
#  This is for storing the result files (one file reference per row)
model.schemas['ETAS'].create_table(Table.define_asset(
    'ETAS', 'ETAS_Evaluation_Result',
    column_defs=[
        Column.define('ETAS_Evaluation', builtin_types.ermrest_rid),        # foreign key columns
        Column.define('Evaluation_Type', builtin_types.text)                # type of the evaluation
    ],
    fkey_defs=[
        ForeignKey.define(  # This FKey will reference the ETAS_Evaluation table
            ['ETAS_Evaluation'],
            'ETAS', 'ETAS_Evaluation', ['RID']
        )
    ]
))


# ETAS_Evaluation_Plot
#  This is for storing the plot files (one file reference per row)
model.schemas['ETAS'].create_table(Table.define_asset(
    'ETAS', 'ETAS_Evaluation_Plot',
    column_defs=[
        Column.define('ETAS_Evaluation_Result', builtin_types.ermrest_rid), # foreign key column
    ],
    fkey_defs=[
        ForeignKey.define(  # This FKey will reference the ETAS_Evaluation_Result table
            ['ETAS_Evaluation_Result'],
            'ETAS', 'ETAS_Evaluation_Result', ['RID']
        )
    ]
))

print('Congratulations! You have created a DERIVA catalog model.')
print('https://{hostname}/chaise/recordset/#{catalog_id}/ETAS:ETAS_Forecast'.format(hostname=hostname, catalog_id=catalog_id))
"""
"""
