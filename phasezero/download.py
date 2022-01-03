import os.path
import phasezero.core as core
from tqdm import tqdm

DEFAULT_CHUNK_SIZE = 1024 * 1024


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


def download_main(args):
    session = args.session
    project_id = args.project_id
    path = args.path
    output = args.output

    results = core.list_files(session, project_id, path)
    print(results)

    folders = results.commonPrefixes
    files = [obj.key for obj in results.s3Objects]

    tenant_id = session.get_tenant_id()
    file_path = f"{tenant_id}/{project_id}/{path}".replace("//", "/")

    if file_path in folders:
        print("i'm a folder")
    elif file_path in files:
        download_file(session, project_id, path, output=output)
    else:
        print("Unable to find file")
