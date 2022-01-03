import texttable
import phasezero.core as core


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
