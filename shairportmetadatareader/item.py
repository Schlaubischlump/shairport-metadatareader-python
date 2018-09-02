import logging
logger = logging.getLogger("AirplayListenerLogger")
from xml.etree.ElementTree import fromstring as xml_from_string, ParseError
from datetime import datetime

from .util import ascii_integers_to_string, encoded_to_str, encodebytes, xml_to_dict, to_hex, to_unicode, to_binary


class Item(object):
    """
    Class to represent a single pipe item.
    """
    def __init__(self, item_type, code, length=0, text=None, encoding=None):
        """
        :param item_type: ssnc or core
        :param code: ssnc or core codes. See AirplayListener for details.
        :param text: data text
        :param encoding: data encoding
        :param length: length of the data
        """
        super(Item, self).__init__()

        if not item_type:
            raise ValueError("item_type must not be None.")

        if not code:
            raise ValueError("code must not be None.")

        self.type = item_type
        self.code = code
        self.length = length

        if text:
            if self.length <= 0:
                raise ValueError("Malformed data.")
            self.data = encoded_to_str(text, encoding, as_bytes=True)
            self._data_base64 = to_unicode(text) if encoding == "base64" else None
        else:
            if self.length != 0:
                raise ValueError("Malformed data.")
            self.data = to_binary("")
            self._data_base64 = None

    @classmethod
    def item_from_string(cls, item_str):
        """
        Parse the xml string and create an item instance from it.
        :param item_str: xml string from pipe
        :return: item on success or None
        """
        try:
            ele = xml_from_string(item_str)
            ele = xml_to_dict(ele)

            # make sure that the data is not malformed
            if not "type" in ele["item"]:
                return None

            # parse attributes of item
            type = ascii_integers_to_string(ele["item"]["type"])
            code = ascii_integers_to_string(ele["item"]["code"])
            length = int(ele["item"]["length"])

            if "data" in ele["item"]:
                data = ele["item"]["data"]
                text = data["#text"]
                encoding = data["@encoding"]
                return cls(type, code, length, text, encoding)
            return cls(type, code, length)
        except ParseError:
            logger.warning("Can not parse item: {0}".format(item_str))
            return None

    @property
    def data_str(self):
        if self.data:
            return to_unicode(self.data)

    @property
    def data_int(self):
        if self.data:
            return int("0x" + ''.join([to_hex(x)[2:] for x in self.data]), base=16)

    @property
    def data_date(self):
        if self.data:
            return datetime.fromtimestamp(self.data_int)

    @property
    def data_bool(self):
        if self.data:
            return self.data_int

    @property
    def data_base64(self):
        if self.data:
            return self._data_base64 if self._data_base64 else encodebytes(to_binary(self.data))
