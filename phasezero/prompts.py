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
