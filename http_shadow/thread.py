import json
import logging
import syslog
import re

from threading import Thread
from queue import Queue

from http_shadow import Backend

HTTP_PROXY = 'border.service.sjc.consul:80'


class HttpPool(object):
    def __init__(self, threads: int = 5, k8s_sandbox: str = None):
        """
        :type threads int
        :type k8s_sandbox str
        """
        self._queue = Queue(maxsize=0)
        self._workers = []

        for _ in range(threads):
            worker = Worker(self._queue, k8s_sandbox=k8s_sandbox)

            worker.daemon = True
            worker.start()

            self._workers.append(worker)

    def push_item(self, item):
        self._queue.put(item, block=False)

    def wait_for_workers(self):
        for worker in self._workers:
            worker.join()


class Worker(Thread):
    def __init__(self, queue, k8s_sandbox=None):
        """
        :type queue Queue
        :type k8s_sandbox str
        """
        super(Worker, self).__init__()
        self._queue = queue
        self._k8s_sandbox = k8s_sandbox
        self._logger = logging.getLogger(self.name)
        self._is_sandbox = k8s_sandbox is not None

        if self._is_sandbox:
            self._logger.info('Using %s k8s-powered sandbox', self._k8s_sandbox)

        # set up backends
        k8s_headers = {'X-Mw-Kubernetes': '1'}
        self._prod = Backend(proxy=HTTP_PROXY)
        self._kube = Backend(headers=k8s_headers, proxy=HTTP_PROXY)

    def do_request(self, url):
        self._logger.info(url)

        resp_apache = self._prod.request(url)
        resp_kube = self._kube.request(self.add_subdomain(url, self._k8s_sandbox) if self._is_sandbox else url)

        if self._is_sandbox:
            # these are always different
            if 'surrogate_key' in resp_apache['response']:
                del resp_apache['response']['surrogate_key']
            if 'surrogate_key' in resp_kube['response']:
                del resp_kube['response']['surrogate_key']

            if 'location' in resp_apache['response'] and resp_apache['response']['location'] is not None:
                resp_apache['response']['location'] = resp_apache['response']['location']
            if 'location' in resp_kube['response'] and resp_kube['response']['location'] is not None:
                resp_kube['response']['location'] = resp_kube['response']['location']

        compare(url, resp_apache, resp_kube)

    def run(self):
        while True:
            self.do_request(self._queue.get())
            self._queue.task_done()

    @staticmethod
    def add_subdomain(url, subdomain):
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

    # log kubernetes times for 200 responses
    if resp_kube['response']['status_code'] == 200:
        syslog.openlog(ident='k8s-response', logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
        syslog.syslog(str(resp_kube['info']['x_response_time']))
        syslog.closelog()
