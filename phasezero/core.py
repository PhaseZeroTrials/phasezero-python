from phasezero.session import simplify_response
import urllib
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

CREATE_FILE_ENDPOINT = '/1.0/Documents/Study/{studyId}/Path/{relativePath}'


def create_file(session, project_id, project_path, name):
    """
    Create a new `File` entity under parent.

    :param project_path:
    :param project_id:
    :param session: phasezero.session.Session
    :param name: File name
    :return: created file
    """

    return _create_contents(session, project_id, project_path, name)


def _create_contents(session, project_id, project_path, name):
    relative_path = urllib.parse.quote(project_path + "/" + name, safe='')
    url_endpoint = f"/Documents/Study/{project_id}/Path/{relative_path}"

    result = session.post(url_endpoint)
    
    return simplify_response(result)


def get_file(session, project_id, project_path, name):
    """
    Gets specific file specified by the project_id and the project_path
    :param name:
    :param project_path:
    :param project_id:
    :param session: phasezero.session.Session
    :return: list of Projects
    """
    relative_path = urllib.parse.quote(project_path + "/" + name, safe='')
    url_endpoint = f"/Documents/Study/{project_id}/Path/{relative_path}"

    result = session.get(url_endpoint)
    return simplify_response(result)


def get_projects(session):
    url_endpoint = "/Studies"
    return simplify_response(session.get(url_endpoint))


def list_files(session, project_id, path=''):
    url_endpoint = f"/Documents/Study/{project_id}"
    if path != '' and path != '/':
        relative_path = urllib.parse.quote(path, safe='')
        url_endpoint += f"?path={relative_path}"

    result = session.get(url_endpoint)
    return simplify_response(result)

def get_presigned_url(session, project_id, key):
    relative_path = urllib.parse.quote(key, safe='')
    url_endpoint = f"/Documents/Study/{project_id}/Path/{relative_path}/Url"

    result = session.get(url_endpoint)
    return simplify_response(result)

def download_file_from_url(url):
    result = requests.get(url, stream=True)
    result.raise_for_status()
    return result


def initiate_multipart_upload(session, document_id):
    """
    Gets all Projects visible to the authenticated user
    :param document_id:
    :param session: phasezero.session.Session
    :return: list of Projects
    """

    url_endpoint = f"/Documents/{document_id}/MultipartUpload"

    result = session.post(url_endpoint)
    return simplify_response(result)


def delete_file(session, project_id, relative_path):
    """
    Delete a file from Phase Zero

    :param session: phasezero.session.Session
    :param project_id: Project or Study ID
    :param relative_path: Relative path of the file to delete
    :return: Response from the server
    """
    url_endpoint = f"/Documents/Study/{project_id}/Path/{urllib.parse.quote(relative_path, safe='')}/Delete"
    result = session.delete(url_endpoint)
    return simplify_response(result)
