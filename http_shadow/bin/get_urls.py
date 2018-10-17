import logging
import re
import time

from wikia_common_kibana import Kibana


class AccessLog(object):

    # how often to query elasticsearch for new access log entries
    INTERVAL = 5

    # elasticsearch index with access log
    ES_INDEX = 'logstash-apache-access-log'

    # query to use when taking URLs from access log
    QUERY = 'verb: "GET"'

    # which fields to fetch
    FIELDS = ['hostname', 'request']

    # how many URLs to fetch
    BATCH = 2500

    @staticmethod
    def format_log_entry(entry):
        return 'http://{hostname}{request}'.format(**entry)

    @staticmethod
    def filter_out(url):
        """
        :type url str
        :rtype: bool
        """
        # filter out all URLs that are not allowed to be accessed by web-server configuration configuration
        if re.match(
            r'#/(lib|serialized|tests|mw-config|includes|cache|maintenance|languages|config)/#', url
        ) is not None:
            return True

        # SUS-6050 | filter out /load.php requests with varying cache control
        if '/load.php' in url and 'version=' in url:
            return True

        # Special:Random will give us different redirects by design
        if '/Special:Random' in url:
            return True

        # Special:UserLogin and Special:UserSignup make redirects with a random cb value added
        if '/Special:UserLogin' in url or '/Special:UserSignup' in url:
            return True

        # SUS-5885 | ignore c: cross-wiki links // e.g. http://community.wikia.com/wiki/c:pl.mitologia
        if url.startswith('/c:'):
            return True

        return False

    # yields URLs found in access log
    def fetch(self):
        logger = logging.getLogger(__name__)

        while True:
            es = Kibana(
                period=self.INTERVAL,
                index_prefix=self.ES_INDEX
            )

            res = es.query_by_string(self.QUERY, fields=self.FIELDS, limit=self.BATCH)
            urls = map(self.format_log_entry, res)

            for url in urls:
                if self.filter_out(url):
                    logger.info('Filtered out <%s>', url)
                    continue

                yield url

            time.sleep(self.INTERVAL)


def main():
    access_log = AccessLog()

    for url in access_log.fetch():
        print(url)
