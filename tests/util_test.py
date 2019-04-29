# -*- coding: utf-8 -*-
"""
Test the util helper functions.
"""
from unittest import TestCase, main
from xml.etree.ElementTree import fromstring as xml_from_string

from shairportmetadatareader.util import binary_ip_to_string, to_unicode, hex_bytes_to_int, to_hex, to_binary, \
    ascii_integers_to_string, xml_to_dict

class TestUtil(TestCase):
    """
    Test the util functions.
    """
    # pylint: disable=C0103

    def test_binary_ip_to_string(self):
        """
        Test converting a binary ip address to a string.
        """
        self.assertEqual(binary_ip_to_string(b"\xc0\xa8\x01\x02"), "192.168.1.2")

    def test_to_unicode(self):
        """
        Test converting a string to its unicode representation.
        """
        self.assertEqual(to_unicode(b"Die Sch\xc3\xb6ne und das Biest"), u"Die Schöne und das Biest")

    def test_hex_bytes_to_int(self):
        """
        Test converting bytes in hexadecimal to its integer representation in decimal.
        """
        data_tests = [(b"\x00\x00\x00\x00", 0), (b"\x00\x00\x00\x01", 1)]
        for d, v in data_tests:
            self.assertEqual(hex_bytes_to_int(d), v)

    def test_to_hex(self):
        """
        Test converting a string to its hexadecimal representation.
        """
        str_tests = [("w", "0x77"), ("\x1d", "0x1d"), ("<", "0x3c"), ("\x84", "0x84"),
                     ("n", "0x6e"), ("X", "0x58"), ("v", "0x76"), ("\xdd", "0xdd")]
        int_tests = [(74, "0x4a"), (24, "0x18"), (126, "0x7e"), (42, "0x2a"),
                     (220, "0xdc"), (223, "0xdf"), (35, "0x23"), (191, "0xbf")]

        for (s, expected_s), (i, expected_i) in zip(str_tests, int_tests):
            self.assertEqual(to_hex(s), expected_s)
            self.assertEqual(to_hex(i), expected_i)

    def test_to_binary(self):
        """
        Test convert a utf-8 str to bytes.
        """
        str_tests = [(u"Schön", b"Sch\xc3\xb6n"), (u"Test", b"Test")]
        for (s, expected_s) in str_tests:
            self.assertEqual(to_binary(s), expected_s)

    def test_ascii_integers_to_string(self):
        """
        Convert an ascii integer to the corresponding string.
        """
        tests = [("73736e63", 16, 2, "ssnc")]
        for s, base, digits_per_char, expected in tests:
            self.assertEqual(ascii_integers_to_string(s, base, digits_per_char), expected)

    def test_xml_to_dict(self):
        """
        Convert a xml string to a dictionary.
        """
        test_str = '<item><type>73736e63</type><code>70637374</code><length>10</length><data encoding="base64"' \
                   '>MjkzNDE5NDIzMg==</data></item>'
        expected_dict = {"item": {"type": "73736e63", "length": "10", "code": "70637374", "data": \
            {"#text": "MjkzNDE5NDIzMg==", "@encoding": "base64"}}}
        self.assertEqual(xml_to_dict(xml_from_string(test_str)), expected_dict)

if __name__ == "__main__":
    main()
