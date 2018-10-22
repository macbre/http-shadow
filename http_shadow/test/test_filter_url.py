from unittest import TestCase

from http_shadow.bin.get_urls import AccessLog


class TestGetUrls(TestCase):

    def test_filter_url(self):
        assert AccessLog.filter_out('http://paradiseislandhd.wikia.com/includes/fck/editor/'
                                    'filemanager/connectors/asp/connector.asp?Command=FileUpload&'
                                    'Type=File&CurrentFolder=%2F') is True

        assert AccessLog.filter_out('http://community.wikia.com/wiki/c:pl.mitologia') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/C:marvel:Joseph_Ledger_(Earth-31916)') is True
        assert AccessLog.filter_out('http://community.wikia.com/wiki/Special:Random') is True

        assert AccessLog.filter_out('http://poznan.wikia.com/wiki/Gzik') is False
        assert AccessLog.filter_out('http://community.wikia.com/wiki/Special:RandomInCategory/Foo') is True

        # SUS-6067
        assert AccessLog.filter_out('http://community.wikia.com/index.php/?action=ajax&rs=ChatAjax'
                                    '&method=blockOrBanChat&roomId=313003&userToBan=Mr.Mangled10&'
                                    'time=86400&reason=Automatically+banned+for+matching+anti-spam+'
                                    'rules+-+if+you+believe+this+is+an+error%2C+please+contact+a+%5B%5B'
                                    'Community_Central%3AAdmins_and_mods%7Cmoderator%5D%5D+ASAP.&'
                                    'mode=global&key=Chat::cookies::XXX&token=XXX&&cb=36488') is True
