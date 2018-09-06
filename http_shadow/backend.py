import requests

from requests.exceptions import RequestException


class Backend(object):

    USER_AGENT = 'http-shadow/0.1 (+https://github.com/macbre/http-shadow)'

    def __init__(self, headers=None, proxy=None):
        self._http = requests.session()

        # set request headers (including user agent)
        headers = dict() if headers is None else headers
        headers['User-Agent'] = self.USER_AGENT

        # set proxy
        if proxy:
            self._http.proxies = {'http': proxy}

        self._http.headers = headers
        print(headers)

    def request(self, url):
        try:
            resp = self._http.get(url)
        except RequestException as ex:
            return {
                'exception': str(ex)
            }

        return {
            'status_code': resp.status_code,
            'location': resp.headers.get('Location'),
            'content_length': resp.headers.get('Content-Length'),
            'content_type': resp.headers.get('Content-Type'),
            'surrogate_key': resp.headers.get('Surrogate-Key'),
        }
