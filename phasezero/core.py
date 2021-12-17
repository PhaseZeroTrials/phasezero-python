import six
from phasezero.session import simplify_response
import urllib

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
    Gets all Projects visible to the authenticated user
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
