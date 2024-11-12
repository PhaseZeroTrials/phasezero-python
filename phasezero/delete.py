import phasezero.core as core

def delete_file_main(args):
    session = args.session
    project_id = args.project_id
    relative_path = args.relative_path

    try:
        result = core.delete_file(session, project_id, relative_path)
        print(f"File '{relative_path}' has been successfully deleted.")
        print(result)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")