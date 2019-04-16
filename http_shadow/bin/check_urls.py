from sys import stdin, argv

from http_shadow import HttpPool


def main():
    # set up workers - make HTTP requests in parallel
    k8s_sandbox = argv[1] if len(argv) >= 2 else None
    workers = HttpPool(threads=50, k8s_sandbox=k8s_sandbox)

    # read URLs from stdin
    for line in stdin:
        line = line.strip()
        # line = 'http://wikia.com/Privacy'
        # print(line)

        workers.push_item(line)

    # wait for workers to perform their tasks
    workers.wait_for_workers()
