from sys import stdin

from http_shadow import HttpPool


def main():
    # set up workers - make HTTP requests in parallel
    workers = HttpPool(threads=10)

    # read URLs from stdin
    for line in stdin:
        line = line.strip()
        # line = 'http://wikia.com/Privacy'
        # print(line)

        workers.push_item(line)

    # wait for workers to perform their tasks
    workers.wait_for_workers()
