# -*- coding: utf-8 -*-
from unittest import TestCase, main

from shairportmetadatareader.util import binary_ip_to_string, to_unicode

class TestUtil(TestCase):

    def test_binary_ip_to_string(self):
        self.assertEqual(binary_ip_to_string(b"\xc0\xa8\x01\x02"), "192.168.1.2")

    def test_to_unicode(self):
        self.assertEqual(to_unicode(b'Die Sch\xc3\xb6ne und das Biest'), u"Die Schöne und das Biest")

if __name__ == '__main__':
    main()