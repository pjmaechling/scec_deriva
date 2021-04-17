"""Minimal example of a possible rendering of the ETAS starter model.
Developer: Robert Schuler
Modifications: Philip Maechling
"""
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

# ETAS_Forecast
model.schemas['ETAS'].create_table(Table.define(  # <--- 'Table.define(...)' defines a general-purpose table
    'ETAS_Forecast',                                                        # table name
    column_defs=[                                                           # column definitions
        Column.define('Forecast_Name', builtin_types.text, nullok=False),   # column for the name of the forecast
        Column.define('Forecast_Config_JSON', builtin_types.text, annotations={  # this is for DERIVA "schema annoations" to configure DERIVA features
            tag.asset: {                                                    # the "asset" annotation for enabling web upload/download
                'url_pattern': '/hatrac/ETAS/ETAS_Forecast/WebUpload_{{{_Forecast_Config_JSON.md5_hex}}}/{{{_Forecast_Config_JSON.filename}}}',
                'filename_ext_filter': ['.json']
            }
        })
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
        Column.define('ETAS_Forecast', builtin_types.ermrest_rid),          # foreign key column
        Column.define('README_md', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/ETAS_Forecast/WebUpload_{{{_README_md.md5_hex}}}/{{{_README_md.filename}}}',
              'filename_ext_filter': ['.md']
            }
        }),
        Column.define('Config_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/ETAS_Forecast/WebUpload_{{{_Config_JSON.md5_hex}}}/{{{_Config_JSON.filename}}}',
              'filename_ext_filter': ['.json']
            }
        }),
        Column.define('Meta_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
              'url_pattern': '/hatrac/ETAS/ETAS_Forecast/WebUpload_{{{_Meta_JSON.md5_hex}}}/{{{_Meta_JSON.filename}}}',
              'filename_ext_filter': ['.json']
            }
        }),
        Column.define('Evaluation_Catalog_JSON', builtin_types.text, annotations={
            tag.asset: {                                                    # asset annotation
                'url_pattern': '/hatrac/ETAS/ETAS_Forecast/WebUpload_{{{_Evaluation_Catalog_JSON.md5_hex}}}/{{{_Evaluation_Catalog_JSON.filename}}}',
                'filename_ext_filter': ['.json']
            }
        })
    ],
    fkey_defs=[
        ForeignKey.define(  # this FKey will reference the ETAS_Forecast table
            ['ETAS_Forecast'],                                              # foreign key column (list allows 1+)
            'ETAS', 'ETAS_Forecast', ['RID']                                # referenced schema, table, columns
        )
    ]
))


# # ETAS_Evaluation_File
# #  This is to store the readme.md, meta.json, config.json, evaluation_catalog.json files (one file reference per row)
# model.schemas['ETAS'].create_table(Table.define_asset(
#     'ETAS', 'ETAS_Evaluation_File',
#     column_defs=[
#         Column.define('ETAS_Evaluation', builtin_types.ermrest_rid)         # foreign key column
#     ],
#     fkey_defs=[
#         ForeignKey.define(  # This FKey will reference the ETAS_Evaluation table
#             ['ETAS_Evaluation'],
#             'ETAS', 'ETAS_Evaluation', ['RID']
#         )
#     ]
# ))


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


# Bulk Upload Annotation --------------------------------------------------------------------------#

# NOTE: this is not really intended for you to absorb right not. This is one of the most complicated
#       annotations to set on the catalog. But I'm including it here for completeness of the catalog
#       setup.

model.annotations[tag.bulk_upload] = {
    "asset_mappings": [
        {
            "column_map": {
                "Forecast_Name": "{forecast_name}",
                "Forecast_Config_JSON": "{URI}"
            },
            "file_pattern": "^.*/(?P<forecast_name>[^/]+)/config.json$",
            "target_table": [
                "ETAS",
                "ETAS_Forecast"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/ETAS_Forecast/{forecast_name}/{file_name}"
            },
            "record_query_template": "/entity/{target_table}/Forecast_Name={forecast_name_urlencoded}/Forecast_Config_JSON={URI_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "ETAS_Forecast": "{etas_forecast_rid}",
                "URL": "{URI}",
                "MD5": "{md5}",
                "Filename": "{file_name}",
                "Length": "{file_size}",
            },
            "file_pattern": "^.*/(?P<forecast_name>[^/]+)/[^/]+[.](?P<ext>bin|slurm|slurm[.]e.*|slurm[.]o.*)$",
            "target_table": [
                "ETAS",
                "ETAS_Forecast_File"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/ETAS_Forecast/{forecast_name}/{file_name}"
            },
            "record_query_template": "/entity/{target_table}/URL={URI_urlencoded}",
            "metadata_query_templates": [
                "/attribute/ETAS:ETAS_Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "create_record_before_upload": "False"
        }
    ],
    "mime_overrides": {
        "mime/type/goes/here": [
            "file_ext_goes_here"
        ]
    },
    "version_update_url": "https://github.com/informatics-isi-edu/deriva-client",
    "version_compatibility": [
        [
            ">=1.0.0",
            "<2.0.0"
        ]
    ]
}

model.apply()  # this applies the annotation change(s)

# -----------------------------------------------------------------------------------------------#

print('Congratulations! You have created a DERIVA catalog model.')
print('https://{hostname}/chaise/recordset/#{catalog_id}/ETAS:ETAS_Forecast'.format(hostname=hostname, catalog_id=catalog_id))
"""
"""
