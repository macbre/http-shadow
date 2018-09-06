from time import sleep

from wikia_common_kibana import Kibana


class AccessLog(object):

    # how often to query elasticsearch for new access log entries
    INTERVAL = 5

    # query to use when taking URLs from access log
    QUERY = 'verb: "GET"'

    # which fields to fetch
    FIELDS = ['hostname', 'request']

    # how many URLs to fetch
    BATCH = 150

    def __init__(self):
        self.kibana = Kibana(
            period=self.INTERVAL,
            index_prefix='logstash-apache-access-log'
        )

    @staticmethod
    def format_log_entry(entry):
        return 'http://{hostname}{request}'.format(**entry)

    # yields URLs found in access log
    def fetch(self):
        while True:
            res = self.kibana.query_by_string(self.QUERY, fields=self.FIELDS, limit=self.BATCH)
            urls = map(self.format_log_entry, res)

            for url in urls:
                yield url

            sleep(self.INTERVAL)


def main():
    access_log = AccessLog()

    for url in access_log.fetch():
        print(url)
