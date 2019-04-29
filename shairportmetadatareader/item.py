"""
Single shaiport-sync information item.
"""
import logging
from xml.etree.ElementTree import fromstring as xml_from_string, ParseError
from datetime import datetime

from .codetable import CORE_CODE_DICT, SSNC_CODE_DICT, CORE, SSNC
# pylint: disable=W1505
from .util import ascii_integers_to_string, encoded_to_str, encodebytes, xml_to_dict, to_hex, to_unicode, to_binary

logger = logging.getLogger("AirplayListenerLogger") # pylint: disable=C0103


class Item(object): # pylint: disable=R0205
    """
    Class to represent a single item from the pipe or the udp server.
    """
    def __init__(self, item_type, code, length=0, text=None, encoding=None): # pylint: disable=R0913
        """
        :param item_type: ssnc or core
        :param code: ssnc or core codes. See codetable.py for details.
        :param text: encoded data
        :param encoding: base64 or bytes encoding of the text
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
            if encoding == "base64":
                self._data = encoded_to_str(text, encoding, as_bytes=True)
                self._data_base64 = to_unicode(text)
            elif encoding == "bytes":
                self._data = text
                self._data_base64 = encodebytes(to_binary(self._data))
        else:
            if self.length != 0:
                raise ValueError("Malformed data.")
            self._data = None
            self._data_base64 = None

    def __eq__(self, other):
        if not other:
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    # --------------------------------------------- xml parsing --------------------------------------------------------

    @classmethod
    def item_from_xml_string(cls, item_str):
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
            itype = ascii_integers_to_string(ele["item"]["type"])
            code = ascii_integers_to_string(ele["item"]["code"])
            length = int(ele["item"]["length"])

            if "data" in ele["item"]:
                data = ele["item"]["data"]
                text = data["#text"]
                encoding = data["@encoding"]
                return cls(itype, code, length, text, encoding)
            return cls(itype, code, length)
        except ParseError:
            logger.warning("Can not parse item: %s", item_str)
            return None

    # --------------------------------------------- convert data -------------------------------------------------------

    def data(self, dtype=None):
        """
        Return the _data field as the give dtype
        :param dtype: type as which the _data should be interpreted. Use None to guess the type.
        :return: _data converted as dtype
        """
        # pylint: disable=R0911, R0912
        if not self._data:
            return None

        if dtype is None:
            # try to guess the dtype
            if (self.type == SSNC) and (self.code in SSNC_CODE_DICT):
                _, dtype = SSNC_CODE_DICT[self.code]
            elif (self.type == CORE) and (self.code in CORE_CODE_DICT):
                _, dtype = CORE_CODE_DICT[self.code]

            # could not guess the dtype, just return the raw data
            if dtype is None:
                return self._data

        # sanity check
        if (dtype not in ["bytes", "str", "int", "date", "bool", "base64"]) and not callable(dtype):
            raise ValueError("Illegal dtype: {0}".format(dtype))

        if dtype == "bytes":
            return self._data
        if dtype == "str":
            return self.data_str
        if dtype == "int":
            return self.data_int
        if dtype == "date":
            return self.data_date
        if dtype == "bool":
            return self.data_bool
        if dtype == "base64":
            return self.data_base64
        if callable(dtype):
            return dtype(self)  # custom handler for data
        return self._data

    @property
    def data_bytes(self):
        """
        :return: data as bytes
        """
        if self._data:
            return self._data
        return None

    @property
    def data_str(self):
        """
        :return: data as str
        """
        if self._data:
            return to_unicode(self._data)
        return None

    @property
    def data_int(self):
        """
        :return: data as int
        """
        if self._data:
            return int("0x" + ''.join([to_hex(x)[2:] for x in self._data]), base=16)
        return None

    @property
    def data_date(self):
        """
        :return: data as date instance
        """
        if self._data:
            return datetime.fromtimestamp(self.data_int)
        return None

    @property
    def data_bool(self):
        """
        :return: data as bool
        """
        if self._data:
            return bool(self.data_int)
        return None

    @property
    def data_base64(self):
        """
        :return: data as bytes base64 encoded
        """
        if self._data:
            return self._data_base64 if self._data_base64 else encodebytes(to_binary(self._data))
        return None
