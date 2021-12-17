import argparse
from getpass import getpass
import phasezero.session as session
import phasezero.upload as upload
import phasezero.prompts as prompts


def main():
    parser = argparse.ArgumentParser(prog='python3 -m phasezero.cli')
    parser.add_argument('-u', '--user', help='Phase Zero user email')
    parser.add_argument('-p', '--password', help='Phase Zero password')

    subparsers = parser.add_subparsers(title='Available subcommands',
                                       description='Use `python -m ovation.cli <subcommand> -h` for additional help')

    # UPLOAD
    parser_upload = subparsers.add_parser('upload', description='Upload files to Ovation')
    parser_upload.add_argument('project_id', help='Project or Folder UUID')
    parser_upload.add_argument('project_path', help='Path to destination folder in Phase Zero')
    parser_upload.add_argument('paths', nargs='+', help='Paths to local files or directories')
    parser_upload.set_defaults(func=upload.upload_paths)

    args = parser.parse_args()


    if args.user is None:
        args.user = input('Email: ')

    if args.password is None:
        args.password = getpass('Password: ')

    if 'func' not in args is None:
        parser.print_help()
        return

    args.session = session.connect(args.user, args.password)
    args.func(args)

    if len(vars(args)) == 3 and args.user and args.password and args.session:
        prompt_user(args)


def prompt_user(args):
    print("No subcommands were provided. Either provide a subcommand or continue")
    print("Available subcommands\n1:Upload\n2:Download")
    value = int(input("Please enter a subcommand (e.g. enter 1 for Upload):"))
    if value == 1:
        print("\n==========Upload Selected==========\n")
        prompts.handle_upload_prompt(args)
        upload.upload_paths(args)
    else:
        print("Unknown command")
        return


if __name__ == "__main__":
    main()
