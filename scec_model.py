"""Minimal example of a possible rendering of the ETAS starter model.
"""
from deriva.core import DerivaServer, get_credential
from deriva.chisel import Model, Schema, Table, Column, Key, ForeignKey, builtin_types, tag

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

# Forecast
model.schemas['ETAS'].create_table(Table.define(  # <--- 'Table.define(...)' defines a general-purpose table
    'Forecast',                                                             # table name
    column_defs=[                                                           # column definitions
        Column.define('Forecast_Name', builtin_types.text, nullok=False),   # column for the name of the forecast
        Column.define('Forecast_Config_JSON', builtin_types.text, annotations={  # this is for DERIVA "schema annoations" to configure DERIVA features
            tag.asset: {                                                    # the "asset" annotation for enabling web upload/download
                'url_pattern': '/hatrac/ETAS/Forecast/WebUpload_{{{_Forecast_Config_JSON.md5_hex}}}/{{{_Forecast_Config_JSON.filename}}}',
                'filename_ext_filter': ['.json']
            }
        })
    ],
    key_defs=[                                                              # key definitions
        Key.define(['Forecast_Name'])                                       # each key specifies its list of columns of 1+ columns
    ]
))


# Forecast_File
#  This is for storing the 'forecast_config.json', 'slurm_log', 'slurm_stdout', and 'slurm_stderr'
model.schemas['ETAS'].create_table(Table.define_asset(  # <--- 'Table.define_asset(...)' defines a table for storing files
    'ETAS', 'Forecast_File',                                            # schema_name, table_name
    column_defs=[                                                       # column definitions
        Column.define('Forecast', builtin_types.ermrest_rid)            # a key we will use as fkey column
    ],
    fkey_defs=[                                                         # foreign key definitions
        ForeignKey.define(                                              # this FKey will reference Forecast row
            ['Forecast'],                                               # fkey columns: list of 1+ column(s) from this table
            'ETAS', 'Forecast', ['RID']                                 # referenced key: schema name, table name, and list of 1+ key columns
        )
    ]
))


# ETAS Evaluation --------------------------------------------------------------------------------#

# Create the tables at the "Evaluation" level of the table hierarchy

# Evaluation_Group
model.schemas['ETAS'].create_table(Table.define(
    'Evaluation_Group',
    column_defs=[
        Column.define('Evaluation_Group_Name', builtin_types.text, nullok=False),   # evaluation group name
        Column.define('Forecast', builtin_types.ermrest_rid),               # foreign key column
        Column.define('README_md', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/Evaluation_Group/WebUpload_{{{_README_md.md5_hex}}}/{{{_README_md.filename}}}',
              'filename_ext_filter': ['.md']
            }
        }),
        Column.define('Config_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/Evaluation_Group/WebUpload_{{{_Config_JSON.md5_hex}}}/{{{_Config_JSON.filename}}}',
              'filename_ext_filter': ['.json']
            }
        }),
        Column.define('Meta_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/Evaluation_Group/WebUpload_{{{_Meta_JSON.md5_hex}}}/{{{_Meta_JSON.filename}}}',
              'filename_ext_filter': ['.json']
            }
        }),
        Column.define('Evaluation_Catalog_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
                'url_pattern': '/hatrac/ETAS/Evaluation_Group/WebUpload_{{{_Evaluation_Catalog_JSON.md5_hex}}}/{{{_Evaluation_Catalog_JSON.filename}}}',
                'filename_ext_filter': ['.json']
            }
        })
    ],
    key_defs=[
        Key.define(
            ['Evaluation_Group_Name']
        )
    ],
    fkey_defs=[
        ForeignKey.define(  # this FKey will reference the Forecast table
            ['Forecast'],                                              # foreign key column (list allows 1+)
            'ETAS', 'Forecast', ['RID']                                # referenced schema, table, columns
        )
    ]
))


# Evaluation
#  This is for storing the result files (one file reference per row)
model.schemas['ETAS'].create_table(Table.define_asset(
    'ETAS', 'Evaluation',
    column_defs=[
        Column.define('Evaluation_Group', builtin_types.ermrest_rid),        # foreign key columns
        Column.define('Evaluation_Type', builtin_types.text)                # type of the evaluation
    ],
    fkey_defs=[
        ForeignKey.define(  # This FKey will reference the Evaluation table
            ['Evaluation_Group'],
            'ETAS', 'Evaluation_Group', ['RID']
        )
    ]
))


# Evaluation_Plot
#  This is for storing the plot files (one file reference per row)
model.schemas['ETAS'].create_table(Table.define_asset(
    'ETAS', 'Evaluation_Plot',
    column_defs=[
        Column.define('Evaluation', builtin_types.ermrest_rid), # foreign key column
    ],
    fkey_defs=[
        ForeignKey.define(  # This FKey will reference the Evaluation table
            ['Evaluation'],
            'ETAS', 'Evaluation', ['RID']
        )
    ]
))

# -----------------------------------------------------------------------------------------------#

print('Congratulations! You have created a DERIVA catalog model.')
print('Run the scec_annotations.py to apply annotations to the catalog.')
print('https://{hostname}/chaise/recordset/#{catalog_id}/ETAS:Forecast'.format(hostname=hostname, catalog_id=catalog_id))
