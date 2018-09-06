import time

from wikia_common_kibana import Kibana


class AccessLog(object):

    # how often to query elasticsearch for new access log entries
    INTERVAL = 10

    # query to use when taking URLs from access log
    QUERY = 'verb: "GET"'

    # which fields to fetch
    FIELDS = ['hostname', 'request']

    # how many URLs to fetch
    BATCH = 250

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
            now = int(time.time())
            self.kibana._since = now - self.INTERVAL + 1
            self.kibana._to = now

            res = self.kibana.query_by_string(self.QUERY, fields=self.FIELDS, limit=self.BATCH)
            urls = map(self.format_log_entry, res)

            for url in urls:
                yield url

            time.sleep(self.INTERVAL)


def main():
    access_log = AccessLog()

    for url in access_log.fetch():
        print(url)
