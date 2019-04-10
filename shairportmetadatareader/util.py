"""
Common util functions used by all classes.
"""
import sys
import tempfile
from collections import defaultdict

IS_PY2 = sys.version_info.major <= 2

if IS_PY2:
    from base64 import decodestring as decodebytes, encodestring as encodebytes
else:
    from base64 import decodebytes, encodebytes


def to_unicode(s):
    if IS_PY2:
        return s.decode("utf-8") if isinstance(s, str) else s
    return s if isinstance(s, str) else s.decode("utf-8")


def to_binary(s):
    if IS_PY2:
        return s.encode("utf-8") if isinstance(s, unicode) else s
    return s.encode("utf-8") if isinstance(s, str) else s


def to_hex(x):
    """
    Convert a str or an int to its hexadecimal representation.
    :param x: str or int
    """
    if isinstance(x, int):
        return hex(x)
    return hex(ord(x))


def hex_bytes_to_int(b):
    if IS_PY2:
        return int(''.join([str(ord(x)) for x in b]), 16)
    return int(b.hex(), 16)


def binary_ip_to_string(ip):
    """
    Get the ip-address as readable string from its binary representation.
    :param ip: ip-address in binary format
    :return: ip-address as string
    """
    if IS_PY2:
        return ".".join([str(ord(x)) for x in ip])
    return ".".join([str(x) for x in ip])


def ascii_integers_to_string(string, base=16, digits_per_char=2):
    """
    :param string: ascii encoded string consisting of the corresponding ord numbers
    :param base: base of the string
    :param digits_per_char: number of digits for each char
    :return: readable string
    """
    return "".join([chr(int(string[i:i + digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])


def encoded_to_str(data, encoding, as_bytes=True):
    if encoding == "base64":
        bytes = decodebytes(data.encode('ascii'))
        return bytes if as_bytes else to_unicode(bytes)
    raise AttributeError("Unknown encoding format: {0}".format(encoding))


def xml_to_dict(ele):
    """
    Convert an xml object to a dictionary structure.
    See: http://stackoverflow.com/a/10077069
    :param ele: xml string
    :return: dictionary from xml
    """
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
