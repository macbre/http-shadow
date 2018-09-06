from sys import stdin

from http_shadow import Backend

PROXY = 'border.service.sjc.consul:80'


def compare(url, resp_a, resp_b):
    if resp_a == resp_b:
        print('OK <{}>'.format(url))
    else:
        print('ERROR: <{}> {} {}'.format(url, resp_a, resp_b))


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
