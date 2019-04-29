# -*- coding: utf-8 -*-
"""
Basic tests for the item class.
"""
from unittest import TestCase, main
from shairportmetadatareader.item import Item
from shairportmetadatareader.codetable import SSNC

class TestItem(TestCase):
    """
    Test for the item class.
    """

    def test_item_from_xml_string(self):
        """
        Check creating an item from an xml string.
        """
        # This should work
        test_str = '<item><type>73736e63</type><code>70637374</code><length>10</length>' \
                    '<data encoding="base64">MjkzNDE5NDIzMg==</data></item>'
        expected_item = Item(SSNC, "pcst", 10, "MjkzNDE5NDIzMg==", encoding="base64")
        self.assertEqual(Item.item_from_xml_string(test_str), expected_item)

        # This should fail
        self.assertIsNone(Item.item_from_xml_string(test_str[:-10]))
        self.assertRaises(ValueError, Item, SSNC, "pcst", 10, "", encoding="base64")
        self.assertRaises(ValueError, Item, SSNC, "pcst", -1, "", encoding="base64")

if __name__ == "__main__":
    main()
