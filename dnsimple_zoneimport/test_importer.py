# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import tempfile

import pytest

from dnsimple_zoneimport import importer


class TestFindDomain(object):

    def test_filename(self):
        testfiles = [
            ('example.com.db', 'example.com'),
            ('foo.example.com.db', 'foo.example.com'),
            ('example.museum.db', 'example.museum'),
            ('/tmp/example.com.db', 'example.com'),
        ]
        for name, real_domain in testfiles:
            returned_domain = importer.find_domain(name)
            assert returned_domain == real_domain

    def test_origin_domain(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('$ORIGIN example.com.')
        f.close()
        assert importer.find_domain(f.name) == 'example.com'

    def test_origin_padded_domain(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(';My Zone file\n   	$ORIGIN example.com. ; This is the origin entry.\n\n')
        f.close()
        assert importer.find_domain(f.name) == 'example.com'

    def test_origin_subdomain(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('$ORIGIN foo.example.com.')
        f.close()
        assert importer.find_domain(f.name) == 'foo.example.com'

    def test_fail(self):
        with tempfile.NamedTemporaryFile(delete=True) as f:
            with pytest.raises(LookupError):
                importer.find_domain(f.name)
