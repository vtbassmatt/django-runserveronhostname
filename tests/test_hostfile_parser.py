"""
Tests for hostfile parser.
"""
from io import StringIO
import pytest
from runserveronhostname.hostfile_parser import Hostfile


class TestHostfileParser:
    """Test the hostfile parser."""
    
    def test_simple_hostfile(self):
        """Simple hostfile."""
        
        hosts = """##
# Host Database
#
##
127.0.0.1	localhost
255.255.255.255	broadcasthost
::1             localhost
127.0.0.1       test.localhost
"""
        hf = Hostfile(hosts)

        # ensure we see the hostnames
        assert 'localhost' in hf
        assert 'test.localhost' in hf
        # the first entry is not a hostname
        assert '127.0.0.1' not in hf
        # ensure we don't see a nonexistent hostname
        assert 'quack.localhost' not in hf

    def test_io_hostfile(self):
        hosts = """##
# Host Database
#
##
127.0.0.1	localhost
255.255.255.255	broadcasthost
::1             localhost
127.0.0.1       test.localhost
"""
        with StringIO(hosts) as f:
            hf = Hostfile(f)

        # smoketest
        assert 'localhost' in hf

    def test_mapping_behavior(self):
        """Check some mapping behaviors."""
        hosts = """##
127.0.0.1 localhost
127.0.0.1 test.localhost
"""
        hf = Hostfile(hosts)

        assert len(hf) == 2
        assert hf['localhost'] == [2,]
        all_hostnames = list(hf)
        assert len(all_hostnames) == 2
        assert 'localhost' in all_hostnames

    def test_ips_for_host(self):
        "Make sure we can get back IPs for a given host"
        hosts = """##
# Host Database
#
##
127.0.0.1	localhost
127.0.0.1       test.localhost
::1             localhost
"""
        hf = Hostfile(hosts)

        assert hf['localhost'] == [5, 7]
        assert hf.ip_on_line(5) == '127.0.0.1'
        assert hf.ip_on_line(5) == '127.0.0.1'
        # comment lines have no IPs
        assert hf.ip_on_line(1) == None

        with pytest.raises(ValueError):
            hf.ip_on_line(0)
        with pytest.raises(ValueError):
            hf.ip_on_line(20)

    def test_formatting(self):
        """Check formatters."""
        raw_hosts = """## A comment
\t
127.0.0.1\tlocalhost
127.0.0.1   test.localhost
"""
        clean_hosts = """## A comment
127.0.0.1\tlocalhost
127.0.0.1\ttest.localhost"""
        simple_hosts = "127.0.0.1\tlocalhost test.localhost"

        hf = Hostfile(raw_hosts)

        assert format(hf, 'raw') == raw_hosts
        assert format(hf, 'clean') == clean_hosts
        assert format(hf, '') == clean_hosts
        # we don't want to test the comment string that `simple` prints
        assert format(hf, 'simple').endswith(simple_hosts)

        with pytest.raises(ValueError):
            format(hf, 'foobar')
