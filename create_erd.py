1 contributor
63 lines (48 sloc) 2.23 KB
#
# Test the deriva-client library
# Based on a pip install into a anaconda python3 installation
#
from deriva.core import DerivaServer, ErmrestCatalog, HatracStore, AttrDict, get_credential
from deriva.core.ermrest_model import builtin_types, Table, Column, Key, ForeignKey
import sys

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:

        scheme = "https"
        catalog_id = "2"
        servername = "forecast.derivacloud.org"

        credentials = get_credential(servername)
        print(type(credentials))

        catalog = ErmrestCatalog(scheme, servername, catalog_id, credentials=credentials)
        print(type(catalog))
        print(str(catalog))

        model = catalog.getCatalogModel()
        client_table = model.schemas["public"].tables["ermrest_client"]

        # you can access the column definitions in their defined order in the table
        for column in client_table.column_definitions:
            print((column.name, column.type.typename, column.nullok))

        # you can also look up columns by name or by position
        column = client_table.column_definitions[0]
        assert column == client_table.column_definitions[column.name]



        # replace these with your real group IDs
        grps = AttrDict({
            "admin": "https://app.globus.org/groups/50b309c9-4223-11eb-8a64-0ece49b2bd8d",
            "curator": "https://app.globus.org/groups/e5e0880b-4222-11eb-8c49-0eb9d45bd5fd",
            "writer": "https://app.globus.org/groups/a060fd0b-3f13-11eb-85ca-0aecec13621f",
            "reader": "https://app.globus.org/groups/ebfd0f5d-4221-11eb-8826-0aecec13621f",
        })

        object_store = HatracStore('https', servername, credentials)
        namespace = '/hatrac/project_data'
        object_store.create_namespace(namespace)
        object_store.set_acl(namespace, 'owner', [grps.admin])
        object_store.set_acl(namespace, 'subtree-create', [grps.curator, grps.writer])
        object_store.set_acl(namespace, 'subtree-update', [grps.curator])
        object_store.set_acl(namespace, 'subtree-read', [grps.reader])


    except Exception as e:
        print(e)
        print("Caught Exception")
    else:
        print("Success!")

    sys.exit(0)
    """
    """
