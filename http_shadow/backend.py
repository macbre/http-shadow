import logging
import requests

from requests.exceptions import RequestException


class Backend(object):

    USER_AGENT = 'http-shadow/0.1 (+https://github.com/macbre/http-shadow)'

    def __init__(self, headers=None, proxy=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._http = requests.session()

        # set request headers (including user agent)
        headers = dict() if headers is None else headers
        headers['User-Agent'] = self.USER_AGENT

        # set proxy
        if proxy:
            self._http.proxies = {'http': proxy}

        self._http.headers = headers

        self._logger.info('HTTP client: proxy %s, headers: %s', proxy, headers)

    def request(self, url):
        try:
            resp = self._http.get(url, allow_redirects=False)
        except RequestException as ex:
            return {
                'exception': str(ex)
            }

        return {
            'response': {
                'status_code': resp.status_code,
                'location': resp.headers.get('Location'),
                'cache_control': resp.headers.get('Cache-Control'),
                'content_type': resp.headers.get('Content-Type', '').lower(),
                'surrogate_key': resp.headers.get('Surrogate-Key'),
            },
            'info': {
                'x_served_by': resp.headers.get('X-Served-By'),
            }
        }
