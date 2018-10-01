import json
import logging
import syslog
import re

from threading import Thread
from queue import Queue

from http_shadow import Backend

HTTP_PROXY = 'border.service.sjc.consul:80'
# used for comparing redirect locations on different sandboxes
GENERIC_SANDBOX = 'sandbox'


class HttpPool(object):
    def __init__(self, threads=5, apache_host='', k8s_host=''):
        self._queue = Queue(maxsize=0)
        self._workers = []

        for _ in range(threads):
            worker = Worker(self._queue, apache_host, k8s_host)

            worker.daemon = True
            worker.start()

            self._workers.append(worker)

    def push_item(self, item):
        self._queue.put(item, block=False)

    def wait_for_workers(self):
        for worker in self._workers:
            worker.join()


class Worker(Thread):
    def __init__(self, queue, apache_host, k8s_host):
        """
        :type queue Queue
        """
        super(Worker, self).__init__()
        self._queue = queue
        self._apache_host = apache_host
        self._k8s_host = k8s_host
        self._logger = logging.getLogger(self.name)
        self._is_sandbox = len(apache_host) > 0 and len(k8s_host) > 0

        # set up backends
        k8s_headers = {'X-Mw-Kubernetes': '1'} if self._is_sandbox else {}
        self._prod = Backend(proxy=HTTP_PROXY)
        self._kube = Backend(headers=k8s_headers, proxy=HTTP_PROXY)

    def do_request(self, url):
        self._logger.info(url)

        resp_apache = self._prod.request(self.add_subdomain(url, self._apache_host) if self._is_sandbox else url)
        resp_kube = self._kube.request(self.add_subdomain(url, self._k8s_host) if self._is_sandbox else url)

        if self._is_sandbox:
            # these are always different
            if 'surrogate_key' in resp_apache['response']: del resp_apache['response']['surrogate_key']
            if 'surrogate_key' in resp_kube['response']: del resp_kube['response']['surrogate_key']

            if 'location' in resp_apache['response'] and resp_apache['response']['location'] is not None:
                resp_apache['response']['location'] = resp_apache['response']['location'].replace(self._apache_host, GENERIC_SANDBOX)
            if 'location' in resp_kube['response'] and resp_kube['response']['location'] is not None:
                resp_kube['response']['location'] = resp_kube['response']['location'].replace(self._k8s_host, GENERIC_SANDBOX)

        compare(url, resp_apache, resp_kube)

    def run(self):
        while True:
            self.do_request(self._queue.get())
            self._queue.task_done()

    def add_subdomain(self, url, subdomain):
        # prepend wikia.com with <subdomain>.
        return re.sub(r'((wikia|fandom).com)', subdomain + r'.\1', url)


def compare(url, resp_apache, resp_kube):
    is_ok = resp_apache['response'] == resp_kube['response']

    if is_ok:
        print('OK <{}>'.format(url))
    else:
        print('ERROR: <{}> {} {}'.format(url, resp_apache, resp_kube))
        # print(resp_kube['content_length'] - resp_apache['content_length'])

    # log to syslog for further processing in elasticsearch / Kibana
    syslog.openlog(ident='backend', logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
    syslog.syslog(json.dumps({
        'appname': 'http-shadow',  # this will create a separate elasticsearch index
        'is_ok': is_ok,
        'url': url,
        'apache': resp_apache,
        'kube': resp_kube,
    }))
    syslog.closelog()
