import argparse
from getpass import getpass
import phasezero.session as session
import phasezero.upload as upload
import phasezero.download as download
import phasezero.contents as contents
import phasezero.prompts as prompts
import phasezero.delete as delete
import phasezero.core as core
import urllib.parse


def main():
    parser = argparse.ArgumentParser(prog='python3 -m phasezero.cli')
    parser.add_argument('-u', '--user', help='Phase Zero user email')
    parser.add_argument('-p', '--password', help='Phase Zero password')

    subparsers = parser.add_subparsers(title='Available subcommands',
                                       description='Use `python -m phasezero.cli <subcommand> -h` for additional help')

    # UPLOAD
    parser_upload = subparsers.add_parser('upload', description='Upload files to Phase Zero')
    parser_upload.add_argument('project_id', help='Project or Folder UUID')
    parser_upload.add_argument('project_path', help='Path to destination folder in Phase Zero')
    parser_upload.add_argument('paths', nargs='+', help='Paths to local files or directories')
    parser_upload.set_defaults(func=upload.upload_paths)

    # DOWNLOAD
    parser_download = subparsers.add_parser('download', description='Download files from Phase Zero')
    parser_download.add_argument('project_id', help='Project Id', default='')
    parser_download.add_argument('path', nargs='?', help='(Optional) S3 Relative Path to download', default='')
    parser_download.add_argument('-o', '--output', help='Output directory')
    parser_download.set_defaults(func=download.download_main)

    # LIST
    parser_ls = subparsers.add_parser('list',
                                      aliases=['ls'],
                                      description='List Projects or Contents')

    parser_ls.add_argument('project_id', nargs='?', help='(Optional) Project or Folder ID', default='')
    parser_ls.add_argument('path', nargs='?', help='(Optional) S3 Relative Path', default='')

    parser_ls.set_defaults(func=contents.list_contents_main)

    # DELETE
    parser_delete = subparsers.add_parser('delete', description='Delete a file from Phase Zero')
    parser_delete.add_argument('project_id', help='Project Id')
    parser_delete.add_argument('relative_path', help='Relative path of the file to delete')
    parser_delete.set_defaults(func=delete.delete_file_main)

    args = parser.parse_args()

    if args.user is None:
        args.user = input('Email: ')

    if args.password is None:
        args.password = getpass('Password: ')

    if 'func' not in args is None:
        parser.print_help()
        return

    args.session = session.connect(args.user, args.password)

    if 'func' in args:
        args.func(args)

    if len(vars(args)) == 3 and args.user and args.password and args.session:
        prompt_user(args)


def prompt_user(args):
    print("No subcommands were provided. Either provide a subcommand or continue")
    print("Available subcommands\n1:Upload\n2:Download\n3:List Project or Files\n4:Delete File")
    value = int(input("Please enter a subcommand (e.g. enter 1 for Upload):"))
    if value == 1:
        print("\n==========Upload Selected==========\n")
        prompts.handle_upload_prompt(args)
        upload.upload_paths(args)
    elif value == 2:
        print("\n==========Download Selected==========\n")
        prompts.handle_download_prompt(args)
        download.download_main(args)
    elif value == 3:
        print("\n==========List Selected==========\n")
        prompts.handle_list_prompt(args)
        contents.list_contents_main(args)
    elif value == 4:
        print("\n==========Delete Selected==========\n")
        prompts.handle_delete_prompt(args)
        delete.delete_file_main(args)
    else:
        print("Unknown command")
        return





if __name__ == "__main__":
    main()
