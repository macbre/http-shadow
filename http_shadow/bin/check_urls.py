import json
import syslog

from sys import stdin

from http_shadow import Backend

PROXY = 'border.service.sjc.consul:80'


def compare(url, resp_a, resp_b):
    is_ok = resp_a == resp_b

    if is_ok:
        print('OK <{}>'.format(url))
    else:
        print('ERROR: <{}> {} {}'.format(url, resp_a, resp_b))
        # print(resp_b['content_length'] - resp_a['content_length'])

    # log to syslog for further processing in elasticsearch / Kibana
    syslog.openlog(ident='http-shadow', logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
    syslog.syslog(json.dumps({
        'is_ok': is_ok,
        'url': url,
        'response_prod': resp_a,
        'response_kube': resp_b,
    }))
    syslog.closelog()


def main():
    # set up backends
    prod = Backend(proxy=PROXY)
    kube = Backend(headers={'X-Mw-Kubernetes': '1'}, proxy=PROXY)

    # read URLs from stdin
    for url in stdin:
        url = url.strip()
        # url = 'http://wikia.com/Privacy'
        # print(url)

        resp_prod = prod.request(url)
        resp_kube = kube.request(url)

        compare(url, resp_prod, resp_kube)
