def handle_upload_prompt(args):
    print("Please enter the destination Phase Zero Project Id\n")
    args.project_id = input("Project Id: ")
    print("Please enter the studyID followed by the relative path of the folder\n"
          "Example for a directory /phaseZero/destinationFolder\n")
    args.project_path = input("Destination Folder: ")
    print("Please enter the relative paths to local files or directories\n"
          "Example for a directory /path/to/Files\n"
          "Example for a single file /path/to/Files/file.txt\n")
    args.paths = input("Local File/Directory Path: ")


def handle_list_prompt(args):
    print("[Optional] Enter a Project Id To list, leave blank to see all available projects\n")
    args.project_id = input("Project Id: ")
    if args.project_id:
        print("[Optional] Enter the relative path to list files in S3 directory\n"
              "Example for a directory /path/to/Files\n")
        args.path = input("S3 RelativePath: ")
    else:
        args.path = ''


def handle_download_prompt(args):
    print("Enter a Project Id to download\n")
    args.project_id = input("Project Id: ")
    if args.project_id:
        print("[Optional] Enter the relative path to list files in S3 directory\n"
              "Example for a directory /path/to/Files\n"
              "If left blank, the entire project will be downloaded")

        args.path = input("S3 RelativePath: ")
    else:
        args.path = ''
    args.output = input("Output Directory: ")
