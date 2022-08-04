import collections
import six
import requests
import retrying
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_HOST = 'https://api.phasezerotrials.com'
LOGIN_ENDPOINT = DEFAULT_HOST + '/1.0/Auth/login'


class DataDict(dict):
    def __init__(self, *args, **kw):
        super(DataDict, self).__init__(*args, **kw)
        self.__dict__ = self


def connect(email, password):
    """Creates a new Session.

    Arguments
    ---------
    email : string
        Phase Zero account email. Required for selection of saved token.

    password : string
        Password

    Returns
    -------
    session : phasezero.session.Session
        A new authenticated Session

    """

    data = {'email': email, 'password': password}

    r = requests.post(LOGIN_ENDPOINT, json=data, verify=False)
    if r.status_code != requests.codes.ok:
        messages = {401: "Email or password incorrect. Please check your account credentials and try again. "
                         "Please email hello@phasezero.co if you need assistance.",
                    500: "Unable to connect due to a server error. Our engineering team has been notified. "
                         "Please email hello@phasezero.co if you need assistance."}
        if r.status_code in messages.keys():
            print(messages[r.status_code])
            return
        else:
            r.raise_for_status()

    token = r.json()['token']
    default_tenant_id = r.json()['defaultTenantId'];
    print(f"Successfully Logged in as {email}")
    return Session(token, default_tenant_id, email, password)


def simplify_response(data, hoist_singleton=True):
    """
    Simplifies the response from an REST API for easier use in Python

    :param data: response data
    :return: Pythonified response
    """
    try:
        if len(data) == 1 and hoist_singleton:
            result = list(six.itervalues(data)).pop()
        else:
            result = data

        if isinstance(result, collections.Mapping):
            if 'type' in result and result['type'] == 'Annotation':
                return DataDict(result)

            return DataDict(((k, simplify_response(v, hoist_singleton=False)) for (k, v) in six.iteritems(result)))
        elif isinstance(result, six.string_types):
            return result
        elif isinstance(result, collections.Iterable):
            return [simplify_response(d) for d in result]
    except:
        return data


MAX_RETRY_DELAY_MS = 2000
MIN_RETRY_DELAY_MS = 250


def _retry_if_http_error(exception):
    """Return True if we should retry (in this case when it's an RequestException), False otherwise"""
    return isinstance(exception, requests.exceptions.RequestException)


class Session(object):
    """
    Represents an authenticated session.

    `Session` wraps a `requests.Session` and provides methods for convenient creation of Phase Zero API paths and URLs.
    All responses are transformed via `simplify_response` to make interactive use more convenient.
    """

    def __init__(self, token, default_tenant_id, email, password, api=DEFAULT_HOST, prefix='/1.0', retry=3):
        """
        Creates a new Session
        :param token: Phase Zero API token
        :param api: API endpoint URL (default https://api.phasezerotrials.com)
        :param prefix: API namespace prefix (default '/api/v1')
        :return: Session object
        """
        self.session = requests.Session()

        self.token = token
        self.default_tenant_id = default_tenant_id
        self.email = email
        self.password = password
        self.api_base = api
        self.prefix = prefix
        self.retry = retry if retry is not None else 0

        class BearerAuth(object):
            def __init__(self, token):
                self.token = token
                self.default_tenant_id = default_tenant_id

            def __call__(self, r):
                # modify and return the request
                r.headers['Authorization'] = 'Bearer {}'.format(self.token)
                return r

        self.session.auth = BearerAuth(token)
        self.session.headers = {'content-type': 'application/json',
                                'accept': 'application/json',
                                'X-Tenant-Id': self.default_tenant_id
                                }

    def get_tenant_id(self):
        return self.default_tenant_id;

    def make_url(self, path):
        """
        Creates a full URL by combining the API host, prefix and the provided path
        :param path: path, e.g. /projects/1
        :return: full URL, e.g. https://api.phasezerotrials.com/api/v1/projects/1
        """

        if not path.startswith(self.prefix):
            path = (self.prefix + path).replace('//', '/')

        return urljoin(self.api_base, path)

    def retry_call(self, m, *args, **kwargs):
        return retrying.Retrying(stop_max_attempt_number=self.retry + 1,
                                 wait_exponential_multiplier=MIN_RETRY_DELAY_MS,  # MS
                                 wait_exponential_max=MAX_RETRY_DELAY_MS,
                                 wait_jitter_max=MIN_RETRY_DELAY_MS,
                                 retry_on_exception=_retry_if_http_error).call(m, *args, **kwargs)

    def get_stream(self, path, **kwargs):
        r = self.retry_call(self._get, path, stream=True, **kwargs)
        return r

    def get(self, path, **kwargs):
        r = self.retry_call(self._get, path, **kwargs)

        return simplify_response(r.json())

    def _get(self, path, **kwargs):
        r = self.session.get(self.make_url(path), verify=False, **kwargs)
        r.raise_for_status()
        return r

    def put(self, path, data=None, **kwargs):
        """

        :param data:
        :param path: entity path
        :param kwargs: additional args for requests.Session.put
        :return:
        """

        if data is None:
            data = {}

        kwargs['json'] = data
        r = self.retry_call(self._put, path, **kwargs)

        return simplify_response(r.json())

    def _put(self, path, **kwargs):
        r = self.session.put(self.make_url(path), verify=False, **kwargs)
        r.raise_for_status()
        return r

    def post(self, path, data=None, **kwargs):
        if data is None:
            data = {}

        kwargs['json'] = data
        r = self.retry_call(self._post, path, **kwargs)

        return simplify_response(r.json())

    def _post(self, path, **kwargs):
        r = self.session.post(self.make_url(path), verify=False, **kwargs)
        r.raise_for_status()
        return r

    def delete(self, path, **kwargs):
        return self.retry_call(self._delete, path, **kwargs)

    def _delete(self, path, **kwargs):
        r = self.session.delete(self.make_url(path), verify=False, **kwargs)
        r.raise_for_status()
        return r

    def refresh_token(self):
        data = {'email': self.email, 'password': self.password}
        r = requests.post(LOGIN_ENDPOINT, json=data, verify=False)
        if r.status_code != requests.codes.ok:
            messages = {401: "Email or password incorrect. Please check your account credentials and try again. "
                         "Please email hello@phasezero.co if you need assistance.",
                        500: "Unable to connect due to a server error. Our engineering team has been notified. "
                         "Please email hello@phasezero.co if you need assistance."}
            if r.status_code in messages.keys():
                print(messages[r.status_code])
                return
            else:
                r.raise_for_status()

        token = r.json()['token']

        # Assign token
        self.token = token

        return self.token

