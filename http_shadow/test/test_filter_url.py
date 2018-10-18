from unittest import TestCase

from http_shadow.bin.get_urls import AccessLog


class TestGetUrls(TestCase):

    def test_filter_url(self):
        assert AccessLog.filter_out('http://paradiseislandhd.wikia.com/includes/fck/editor/filemanager/connectors/asp/connector.asp?Command=FileUpload&Type=File&CurrentFolder=%2F') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/c:pl.mitologia') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/C:marvel:Joseph_Ledger_(Earth-31916)') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/Special:Random') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/Special:RandomInCategory/Foo') is True

        assert AccessLog.filter_out('http://poznan.wikia.com/wiki/Gzik') is False
