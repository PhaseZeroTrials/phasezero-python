# Phase Zero Python CLI

Phase Zero is a no-code platform designed for any healthcare organization to safely collect, store, and share any type of health related data.

This Python CLI wraps the Phase Zero REST API for document management including:

1. File Upload
2. File Download
3. List Files

## Requirements

* Python 3.4+

## Getting Started

Clone the following repository

```
git clone https://github.com/PhaseZeroTrials/phasezero-python.git
```

It is recommended to use a virtualenv when running the code

Install the requirements by running

```
pip3 install -r requirements.txt
```

## Usage


### Uploading files from the terminal

Use the `phasezero.cli` module's `upload` command to upload files from your local file system to Phase Zero.


The `upload` command takes the following positional arguments:

```
positional arguments:
  project_id    Project or Folder UUID
  project_path  Path to destination folder in Phase Zero
  paths         Paths to local files or directories
```

Example usage from the terminal

```
python3 -m phasezero.cli -u user@email.com -p yourPhaseZeroPassword upload 1 documents/ ./path/to/files/
```

### Downloading files from the terminal

Use the `phasezero.cli` modules' `download` command to download files from Phase Zero into your local file system
The `download` command takes the following positional arguments:

```
positional arguments:
  project_id    Project Id
  path          Path to desired directory for file to download
  
named arguments:  
  -o            Output local file directory
```
Example usage from the terminal
```
​python3 -m phasezero.cli -u user@email.com -p yourPhaseZeroPassword download 1 cloud_directory/ -o my_local_computer
```

### Deleting files from the terminal

Use the `phasezero.cli` module's `delete` command to delete files from Phase Zero.

The `delete` command takes the following positional arguments:

```
positional arguments:
  project_id    Project Id
  relative_path Relative path of the file to delete
```

Example usage from the terminal:

```
python3 -m phasezero.cli -u user@email.com -p yourPhaseZeroPassword delete 1 /path/to/file.txt
```

This will delete the file located at `/path/to/file.txt` in the project with ID 1.

## Recommendations

If you do not want to run the command in the root of your folder, it is recommended to set add the phaszero module to your  `PYTHONPATH`

[Stack Overflow Example](https://stackoverflow.com/a/53311583)

```aidl
export PYTHONPATH="${PYTHONPATH}:/path/to/my/modules/"
```

This allows the command `python3 -m phasezero.cli` to be run from anywhere

### Setting an Alias

Here is a recommended alias that can be used to easily access the CLI:

```aidl
alias pz_cli="source ~/Documents/pz/python3-venv/pz-python/bin/activate; python3 -m phasezero.cli"
```

