"""
Common util functions used by all classes.
"""
import sys
import tempfile
from collections import defaultdict

IS_PY2 = sys.version_info.major <= 2

if IS_PY2:
    from base64 import decodestring as decodebytes, encodestring as encodebytes # pylint: disable=W0611
else:
    from base64 import decodebytes, encodebytes # pylint: disable=W0611


def to_unicode(string_or_bytes):
    """
    :param string_or_bytes:
    :return: string_or_bytes converted to unicode
    """
    if IS_PY2:
        return string_or_bytes.decode("utf-8") if isinstance(string_or_bytes, str) else string_or_bytes
    return string_or_bytes if isinstance(string_or_bytes, str) else string_or_bytes.decode("utf-8")


def to_binary(string_or_unicode):
    """
    :param string_or_unicode:
    :return: string_or_unicode converted to utf-8 as bytes
    """
    if IS_PY2:
        # pylint: disable=E0602
        return string_or_unicode.encode("utf-8") if isinstance(string_or_unicode, unicode) else string_or_unicode
    return string_or_unicode.encode("utf-8") if isinstance(string_or_unicode, str) else string_or_unicode


def to_hex(str_or_int):
    """
    Convert a str or an int to its hexadecimal representation.
    :param str_or_int: str or int
    :return: str_or_int converted to hexadecimal system
    """
    if isinstance(str_or_int, int):
        return hex(str_or_int)
    return hex(ord(str_or_int))


def hex_bytes_to_int(hex_bytes):
    """
    Convert hexadecimal bytes to an integer.
    :param hex_bytes: bytes which represent an integer
    :return: integer representation of hex_bytes
    """
    if IS_PY2:
        return int(''.join([str(ord(x)) for x in hex_bytes]), 16)
    return int(hex_bytes.hex(), 16)


def binary_ip_to_string(ip_address):
    """
    Get the ip-address as readable string from its binary representation.
    :param ip_address: ip-address in binary format
    :return: ip-address as string
    """
    if IS_PY2:
        return ".".join([str(ord(x)) for x in ip_address])
    return ".".join([str(x) for x in ip_address])


def ascii_integers_to_string(string, base=16, digits_per_char=2):
    """
    :param string: ascii encoded string consisting of the corresponding ord numbers
    :param base: base of the string
    :param digits_per_char: number of digits for each char
    :return: readable string
    """
    return "".join([chr(int(string[i:i + digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])


def encoded_to_str(data, encoding, as_bytes=True):
    """
    Encode bytes to a base64 string or bytes object. Further encoding might be added in the future.
    :param data: data as bytes
    :param encoding: encoding as str (currently only: base64)
    :param as_bytes: True to return bytes, False to return a str
    :return:
    """
    if encoding == "base64":
        bytes_decoded = decodebytes(data.encode('ascii')) # pylint: disable=W1505
        return bytes_decoded if as_bytes else to_unicode(bytes_decoded)
    raise AttributeError("Unknown encoding format: {0}".format(encoding))


def xml_to_dict(ele):
    """
    Convert an xml object to a dictionary structure.
    See: http://stackoverflow.com/a/10077069
    :param ele: xml string
    :return: dictionary from xml
    """
    # pylint: disable=C0103
    d = {ele.tag: {} if ele.attrib else None}
    children = list(ele)
    if children:
        dd = defaultdict(list)
        for dc in map(xml_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {ele.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if ele.attrib:
        d[ele.tag].update(('@' + k, v) for k, v in ele.attrib.items())
    if ele.text:
        text = ele.text.strip()
        if children or ele.attrib:
            if text:
                d[ele.tag]['#text'] = text
        else:
            d[ele.tag] = text
    return d


def write_data_to_image(data, extension=".png"):
    """
    Write image data encoded as binary or raw string to a file.
    :param data: image data as binary
    :param extension: file extension to use
    :return path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(prefix="image_", suffix=extension, delete=False)
    with temp_file as file:
        file.write(data)
    return temp_file.name
