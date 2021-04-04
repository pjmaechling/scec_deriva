"""Minimal example of a possible rendering of the ETAS starter model.
"""
from deriva.core import DerivaServer, get_credential
from deriva.chisel import Model, tag

# Connect to server and catalog ------------------------------------------------------------------#

hostname = 'forecast.derivacloud.org'   # this is a dev server for throw-away work (change to 'forecast.derivacloud.org)
catalog_id = '5'            # this was a throw-away catalog used to test this script (change to TBD)

model = Model.from_catalog(
    DerivaServer('https', hostname, credentials=get_credential(hostname)).connect_ermrest(catalog_id)
)

# ACLs --------------------------------------------------------------------------------------------#

# Note: This just adds the "isrd-systems" group as an "owner" of this catalog so that the DERIVA
#       team can access the catalog while it is in development (or beyond)

__isrd_systems__ = "https://auth.globus.org/3938e0d0-ed35-11e5-8641-22000ab4b42b"   # DERIVA sys admins
__isrd_staff__ = "https://auth.globus.org/176baec4-ed26-11e5-8e88-22000ab4b42b"     # DERIVA staff
__scec_readers__ = "https://auth.globus.org/a060fd0b-3f13-11eb-85ca-0aecec13621f"   # SCEC reader-only group

# add isrd-systems to
owners = model.acls['owner']
if __isrd_systems__ not in owners:
    owners.append(__isrd_systems__)

# add a couple groups to read-only acls
for acl_name in ['enumerate', 'select']:
    for group in [__scec_readers__, __isrd_staff__]:
        if group not in model.acls[acl_name]:
            model.acls[acl_name].append(group)


# Chaise-Config Annotation ------------------------------------------------------------------------#

model.annotations[tag.chaise_config] = {
    "navbarBrandText": "SCEC Forecast",
    "navbarBrand": f"/chaise/recordset/#{catalog_id}/ETAS:Forecast",
    "systemColumnsDisplayCompact": ["RID"],
    "systemColumnsDisplayDetailed": ["RID"],
    "systemColumnsDisplayEntry": ["RID"],
    "signUpURL": "https://app.globus.org/groups/a060fd0b-3f13-11eb-85ca-0aecec13621f/about",
    "logoutURL": f"/chaise/recordset/#{catalog_id}/ETAS:Forecast",
    "navbarMenu": {
        "newTab": False,
        "children": [
            {
                "name": "Search",
                "children": [
                    { "name": "Forecasts", "url": "/chaise/recordset/#{{$catalog.id}}/ETAS:Forecast" },
                    { "name": "Evaluation Groups", "url": "/chaise/recordset/#{{$catalog.id}}/ETAS:Evaluation_Group" },
                    { "name": "Evaluations", "url": "/chaise/recordset/#{{$catalog.id}}/ETAS:Evaluation" }
                ]
            }
        ]
    }
}


# Schema Display Annotation ------------------------------------------------------------------------#

model.schemas['ETAS'].annotations[tag.display] = {
    "name_style": {"underline_space": True},
    "show_key_link": {"*": False},
    "show_foreign_key_link": {"*": False},
}


# Visible Columns Annotations ---------------------------------------------------------------------#

# Note: These annotations will modify the default display of columns for the annotated tables below

model.schemas['ETAS'].tables['Forecast_File'].annotations[tag.visible_columns] = {
    'compact': [
        'RID',
        'URL'
    ]
}

model.schemas['ETAS'].tables['Evaluation'].annotations[tag.visible_columns] = {
    'compact': [
        'RID',
        'Evaluation_Type',
        'URL',
        {
            "source": [
                {
                    "inbound": [
                        "ETAS",
                        "Evaluation_Plot_Evaluation_fkey"
                    ]
                },
                "RID"
            ],
            "markdown_name": "Plot",
            "entity": True,
            "aggregate": "array_d",
            "display": {
                "markdown_pattern": "{{#each $self}}[![{{{this.values.Filename}}}]({{{this.values.URL}}}){width=120}]({{{this.values.URL}}}){{/each}}",
                "template_engine": "handlebars"
            }
        }
    ]
}

model.schemas['ETAS'].tables['Evaluation_Plot'].annotations[tag.visible_columns] = {
    "compact": [
        "RID",
        "URL",
        {
            "display": {
                "markdown_pattern": "[![{{{Filename}}}]({{{URL}}}){width=120}]({{{URL}}})"
            },
            "markdown_name": "Preview"
        }
    ],
    "detailed": [
        "RID",
        "URL",
        "Filename",
        "Description",
        "Length",
        "MD5",
        "Evaluation",
        {
            "markdown_name": "Preview",
            "display": {
                "markdown_pattern": "[![{{{Filename}}}]({{{URL}}}){width=120}]({{{URL}}})"
            }
        }
    ]
}


# Visible FKeys Annotations ---------------------------------------------------------------------#

# Note: These annotations will modify the default ordering of related entities

model.schemas['ETAS'].tables['Forecast'].annotations[tag.visible_foreign_keys] = {
    "detailed": [
        [
            "ETAS",
            "Forecast_File_Forecast_fkey"
        ],
        [
            "ETAS",
            "Evaluation_Group_Forecast_fkey"
        ]
    ]
}


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
            "file_pattern": "^(?P<forecast_name>[^/]+)/config.json$",
            "target_table": [
                "ETAS",
                "Forecast"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{file_name}"
            },
            "record_query_template": "/entity/{target_table}/Forecast_Name={forecast_name_urlencoded}/Forecast_Config_JSON={URI_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Forecast": "{etas_forecast_rid}",
                "URL": "{URI}",
                "MD5": "{md5}",
                "Filename": "{file_name}",
                "Length": "{file_size}",
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/[^/]+[.](?P<ext>bin|slurm|slurm[.]e.*|slurm[.]o.*)$",
            "target_table": [
                "ETAS",
                "Forecast_File"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/URL={URI_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Forecast": "{etas_forecast_rid}",
                "Evaluation_Group_Name": "{evaluation_group_name}",
                "README_md": "{URI}"
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/README.md$",
            "target_table": [
                "ETAS",
                "Evaluation_Group"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/Evaluation_Group_Name={evaluation_group_name_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Forecast": "{etas_forecast_rid}",
                "Evaluation_Group_Name": "{evaluation_group_name}",
                "Config_JSON": "{URI}"
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/config.json$",
            "target_table": [
                "ETAS",
                "Evaluation_Group"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/Evaluation_Group_Name={evaluation_group_name_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Forecast": "{etas_forecast_rid}",
                "Evaluation_Group_Name": "{evaluation_group_name}",
                "Meta_JSON": "{URI}"
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/meta.json$",
            "target_table": [
                "ETAS",
                "Evaluation_Group"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/Evaluation_Group_Name={evaluation_group_name_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Forecast": "{etas_forecast_rid}",
                "Evaluation_Group_Name": "{evaluation_group_name}",
                "Evaluation_Catalog_JSON": "{URI}"
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/evaluation_catalog.json$",
            "target_table": [
                "ETAS",
                "Evaluation_Group"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Forecast/Forecast_Name={forecast_name_urlencoded}/etas_forecast_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/Evaluation_Group_Name={evaluation_group_name_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Evaluation_Group": "{etas_evaluation_group_rid}",
                "Evaluation_Type": "{evaluation_type}",
                "URL": "{URI}",
                "MD5": "{md5}",
                "Filename": "{file_name}",
                "Length": "{file_size}",
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/results/(?P<evaluation_type>.+-test).*[.]json$",
            "target_table": [
                "ETAS",
                "Evaluation"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/results/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Evaluation_Group/Evaluation_Group_Name={evaluation_group_name_urlencoded}/etas_evaluation_group_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/URL={URI_urlencoded}",
            "create_record_before_upload": "False"
        },
        {
            "column_map": {
                "Evaluation": "{etas_evaluation_rid}",
                "URL": "{URI}",
                "MD5": "{md5}",
                "Filename": "{file_name}",
                "Length": "{file_size}",
            },
            "file_pattern": "^(?P<forecast_name>[^/]+)/(?P<evaluation_group_name>[^/]+)/plots/(?P<basename>.+)[.]png",
            "target_table": [
                "ETAS",
                "Evaluation_Plot"
            ],
            "checksum_types": [
                "md5"
            ],
            "hatrac_options": {
                "versioned_uris": "True"
            },
            "hatrac_templates": {
                "hatrac_uri": "/hatrac/ETAS/Forecast/{forecast_name}/{evaluation_group_name}/plots/{file_name}"
            },
            "metadata_query_templates": [
                "/attribute/ETAS:Evaluation/Filename={basename_urlencoded}.json/etas_evaluation_rid:=RID?limit=1"
            ],
            "record_query_template": "/entity/{target_table}/URL={URI_urlencoded}",
            "create_record_before_upload": "False"
        },
    ],
    "mime_overrides": {
        "mime/type/goes/here": [
            "file_ext_goes_here"
        ]
    },
    "relative_path_validation": True,
    "version_update_url": "https://github.com/informatics-isi-edu/deriva-client",
    "version_compatibility": [
        [
            ">=1.0.0",
            "<2.0.0"
        ]
    ]
}


# Apply Changes ---------------------------------------------------------------------------------#

model.apply()  # <-- after any acl or annotations changes, we have to 'apply()' to update the server

# -----------------------------------------------------------------------------------------------#

print(f'Annotations updated on {hostname} catalog {catalog_id}')
