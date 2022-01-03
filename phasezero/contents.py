import texttable
import phasezero.core as core


def _format_s3_objects(rootPrefix, prefix, folder_name):
    return { 'name': folder_name.replace(prefix, ''), 'path': folder_name.replace(rootPrefix, '') }

def list_contents_main(args):
    session = args.session
    project_id = args.project_id
    path = args.path

    # List Projects
    if project_id is None or project_id == '':
        table = texttable.Texttable(max_width=0)
        table.set_cols_align(["l", "l"])
        table.add_rows([['Name', 'ID']])
        for p in core.get_projects(session):
            table.add_row([p.name, p.id])

        print(table.draw())
    else:
        result = core.list_files(session, project_id, path)
        table = texttable.Texttable(max_width=0)
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_align(['l', 'l'])
        table.add_rows([['Name', 'Path']])

        tenant_id = session.get_tenant_id()
        root_prefix = f"{tenant_id}/{project_id}/"

        # Add Folders
        folders = [_format_s3_objects(root_prefix, result.prefix, folder) for folder in result.commonPrefixes]
        s3_objects = [_format_s3_objects(root_prefix, result.prefix, obj.key) for obj in result.s3Objects]
        for folder in folders:
            table.add_row([folder['name'], folder['path']])

        for obj in s3_objects:
            table.add_row([obj['name'], obj['path']])

        print(table.draw())
