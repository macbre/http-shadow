import json
import logging
import syslog

from threading import Thread
from queue import Queue

from http_shadow import Backend

HTTP_PROXY = 'border.service.sjc.consul:80'


class HttpPool(object):

    def __init__(self, threads=5):
        self._queue = Queue(maxsize=0)
        self._workers = []

        for _ in range(threads):
            worker = Worker(self._queue)

            worker.daemon = True
            worker.start()

            self._workers.append(worker)

    def push_item(self, item):
        self._queue.put(item, block=False)

    def wait_for_workers(self):
        for worker in self._workers:
            worker.join()


class Worker(Thread):

    def __init__(self, queue):
        """
        :type queue Queue
        """
        super(Worker, self).__init__()
        self._queue = queue
        self._logger = logging.getLogger(self.name)

        # set up backends
        self._prod = Backend(proxy=HTTP_PROXY)
        self._kube = Backend(headers={'X-Mw-Kubernetes': '1'}, proxy=HTTP_PROXY)

    def do_request(self, url):
        self._logger.info(url)

        resp_prod = self._prod.request(url)
        resp_kube = self._kube.request(url)

        # self._logger.info(resp_prod)
        # self._logger.info(resp_kube)

        compare(url, resp_prod, resp_kube)

    def run(self):
        while True:
            self.do_request(self._queue.get())
            self._queue.task_done()


def compare(url, resp_a, resp_b):
    is_ok = resp_a == resp_b

    if is_ok:
        print('OK <{}>'.format(url))
    else:
        print('ERROR: <{}> {} {}'.format(url, resp_a, resp_b))
        # print(resp_b['content_length'] - resp_a['content_length'])

    # log to syslog for further processing in elasticsearch / Kibana
    syslog.openlog(ident='backend', logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
    syslog.syslog(json.dumps({
        'appname': 'http-shadow',  # this will create a separate elasticsearch index
        'is_ok': is_ok,
        'url': url,
        'response_prod': resp_a,
        'response_kube': resp_b,
    }))
    syslog.closelog()
