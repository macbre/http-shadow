from sys import stdin, argv

from http_shadow import HttpPool


def main():
    # set up workers - make HTTP requests in parallel
    apache_host = argv[1] if len(argv) >= 2 else ''
    k8s_host = argv[2] if len(argv) >= 3 else ''
    workers = HttpPool(threads=10, apache_host=apache_host, k8s_host=k8s_host)

    # read URLs from stdin
    for line in stdin:
        line = line.strip()
        # line = 'http://wikia.com/Privacy'
        # print(line)

        workers.push_item(line)

    # wait for workers to perform their tasks
    workers.wait_for_workers()
