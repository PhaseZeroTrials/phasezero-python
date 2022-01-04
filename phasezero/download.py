import os.path
import phasezero.core as core
from tqdm import tqdm
import functools
from multiprocessing.pool import ThreadPool as Pool

DEFAULT_CHUNK_SIZE = 1024 * 1024


def download_folder(session, folders, files, project_id, root_prefix, prefix, output=None, progress=tqdm):
    # First Level of Folder
    # Download Files
    files = [file.replace(root_prefix, '') for file in files]
    with Pool() as p:
        for f in progress(p.imap_unordered(functools.partial(download_file,
                                                             session,
                                                             project_id,
                                                             output=output,
                                                             progress=progress),
                                           files),
                          desc='Downloading files',
                          unit='file',
                          total=len(files)):
            pass

    # Download rest of folders recursively
    file_dict = []
    for folder in folders:
        _traverse_folder(session, folder, project_id, root_prefix, prefix, file_dict, output=output, progress=progress)
    with Pool() as p:
        for f in progress(p.imap_unordered(functools.partial(_download_file_implicit_path,
                                                             session,
                                                             project_id,
                                                             progress=progress),
                                           file_dict),
                          desc='Downloading files',
                          unit='file',
                          total=len(file_dict)):
            pass


def _traverse_folder(session, folder, project_id, root_prefix, prefix, files, output=None, progress=tqdm):
    if folder is None:
        return

    folder_name = str(folder).replace(str(prefix), "")
    if output is None:
        path = folder_name
    else:
        path = os.path.join(output, folder_name)

    if not os.path.isdir(path):
        os.mkdir(path)

    # Get Files and Folders
    key = folder.replace(str(root_prefix), "")

    result = get_files_and_folders(session, project_id, key)
    prefix = result['prefix']

    folders = result['folders']
    for file in result['files']:
        s3_key = file.replace(root_prefix, '')
        files += [{'s3_key': s3_key, 'output_path': path}]
    for f in folders:
        _traverse_folder(session, f, project_id, root_prefix, prefix, files, output=path, progress=progress)


def _download_file_implicit_path(session, project_id, file_dict, progress=tqdm):
    return download_file(session, project_id, file_dict['s3_key'], output=file_dict['output_path'], progress=progress)


def download_file(session, project_id, path, output=None, progress=tqdm):
    response = core.download_file(session, project_id, path)
    name = os.path.basename(path)
    if output:
        dest = os.path.join(output, name)
    else:
        dest = name
    with open(dest, "wb") as f:
        if progress:
            for data in progress(response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE),
                                 unit='MB',
                                 unit_scale=True,
                                 miniters=1):
                f.write(data)
        else:
            for data in response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                f.write(data)


def get_files_and_folders(session, project_id, path):
    results = core.list_files(session, project_id, path)
    folders = results.commonPrefixes
    files = [obj.key for obj in results.s3Objects]
    return {"files": files, "folders": folders, "prefix": results.prefix}


def download_main(args):
    session = args.session
    project_id = args.project_id
    path = args.path
    output = args.output

    result = get_files_and_folders(session, project_id, path)
    folders = result['folders']
    files = result['files']
    prefix = result['prefix']

    tenant_id = session.get_tenant_id()
    file_path = f"{tenant_id}/{project_id}/{path}".replace("//", "/")

    tenant_id = session.get_tenant_id()
    root_prefix = f"{tenant_id}/{project_id}/".replace("//", "/")

    if file_path in folders:
        download_folder(session, folders, files, project_id, root_prefix, prefix, output=output)
    elif file_path in files:
        download_file(session, project_id, path, output=output)
    elif path is None or path == '':
        print("Downloading entire project")
        download_folder(session, folders, files, project_id, root_prefix, prefix, output=output)
    else:
        print("Unable to find file")
