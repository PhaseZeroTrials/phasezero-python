import urllib
from pathlib import Path
import mimetypes
import threading
import requests
import os
import math

import phasezero.core as core

from tqdm import tqdm

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ProgressPercentage(object):
    def __init__(self, filename, progress=tqdm):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._size = float(os.path.getsize(filename))
        self._progress = progress(unit='B',
                                  unit_scale=True,
                                  total=self._size,
                                  desc=os.path.basename(filename))

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self._progress.update(self._seen_so_far)
            if self._seen_so_far >= self._size:
                self._progress.close()


def upload_folder(session, project_id, project_path, directory_path, failed_files, progress=tqdm):
    """
    Recursively uploads a folder to Phase Zero

    :param project_path:
    :param project_id:
    :param session: Session
    :param directory_path: local path to directory
    :param failed_files: list of files failed to be uploaded
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    """

    for root, dirs, files in os.walk(directory_path):
        root_name = os.path.basename(root)
        if len(root_name) == 0:
            root_name = os.path.basename(os.path.dirname(root))

        relative_path = f"{project_path}/{root_name}"
        for f in files:
            path = os.path.join(root, f)
            try:
                file = core.create_file(session, project_id, relative_path, f)
            except:
                document = core.get_file(session, project_id, project_path, f)
                file = core.initiate_multipart_upload(session, document['id'])

            try:
                upload_revision(session, file, path, progress=progress)
            except:
                failed_files << relative_path




def upload_file(session, project_id, project_path, file_path, progress=tqdm):
    """
    Upload a file to Phase Zero

    :param project_path:
    :param project_id:
    :param session: Session
    :param file_path: local path to file
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: created File entity dictionary
    """
    name = os.path.basename(file_path)
    try:
        file = core.create_file(session, project_id, project_path, name)
    except:
        document = core.get_file(session, project_id, project_path, name)
        file = core.initiate_multipart_upload(session, document['id'])

    return upload_revision(session, file, file_path, progress=progress)


def guess_content_type(file_name):
    content_type = mimetypes.guess_type(file_name)[0]
    if content_type is None:
        content_type = 'application/octet-stream'

    return content_type


def upload_revision(session, parent_file, local_path, progress=tqdm):
    """
    Upload a new `Revision` to `parent_file`. File is uploaded from `local_path` to
    the Phase Zero cloud, and the newly created `Revision` version is set.
    :param chunk_size:
    :param session: phasezero.connection.Session
    :param parent_file: file entity dictionary or file ID string
    :param local_path: local path
    :param progress: if not None, wrap in a progress (i.e. tqdm). Default: tqdm
    :return: new `Revision` entity dicitonary
    """
    file_name = os.path.basename(local_path)
    content_type = guess_content_type(file_name)
    multipart_upload_to_aws(session, parent_file, content_type, local_path, progress)


def multipart_upload_to_aws(session, document, content_type, local_path, progress):
    target_file = Path(local_path)
    file_size = target_file.stat().st_size
    print(file_size)
    max_size = 5 * 1024 * 1024
    num_chunks = math.floor(file_size / max_size) + 1
    create_presigned_url_endpoint = f"/Documents/{document['id']}/UploadUrl"
    mark_as_complete_endpoint = f"/Documents/{document['id']}/Revision"

    urls = []
    for part in range(1, num_chunks + 1):
        params = {'uploadId': document['uploadId'], 'partNumber': part}
        encoded_params = urllib.parse.urlencode(params)
        signed_url = session.get(f"{create_presigned_url_endpoint}?{encoded_params}")
        urls.append(signed_url)

    parts = []
    with target_file.open('rb') as fin:
        for num, url in enumerate(progress(urls)):
            part = num + 1
            file_data = fin.read(max_size)
            print(f"upload {document['name']} part {part} size={len(file_data)}")
            res = requests.put(url, data=file_data, verify=False)
            print(res)
            if res.status_code != 200:
                return
            etag = res.headers['ETag']
            parts.append({'ETag': etag, 'PartNumber': part})

    params = {'uploadId': document['uploadId']}
    encoded_params = urllib.parse.urlencode(params)

    # Mark upload as complete
    # Refresh in case of time out
    session.refresh_token()
    session.put(f"{mark_as_complete_endpoint}?{encoded_params}", parts)


def upload_paths(args):
    session = args.session
    project_id = args.project_id
    project_path = args.project_path
    paths = args.paths
    failed_files = []
    if type(args.paths) != list:
        paths = [args.paths]

    if paths is None:
        return

    for p in paths:
        print('Uploading {}'.format(p))
        if os.path.isdir(p):
            upload_folder(session, project_id, project_path, p, failed_files)
        else:
            upload_file(session, project_id, project_path, p)

    if len(failed_files) > 0:
        print('Failed to upload the following files:')
        for file in failed_files:
            print(file)