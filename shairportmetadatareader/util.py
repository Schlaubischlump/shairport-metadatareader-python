"""
Common util functions used by all classes.
"""
import sys
import tempfile
from collections import defaultdict

IS_PY2 = sys.version_info.major <= 2

if IS_PY2:
    from base64 import decodestring as decodebytes, encodestring as encodebytes
    to_unicode = lambda s: s.decode("utf-8") if isinstance(s, str) else s
    to_binary = lambda s: s.encode("utf-8") if isinstance(s, unicode) else s
    to_hex = lambda x: hex(ord(x))
    hex_bytes_to_int = lambda b: int(''.join([str(ord(x)) for x in b]), 16)
    binary_ip_to_string = lambda ip: ".".join([str(ord(x)) for x in ip])
else:
    from base64 import decodebytes, encodebytes
    to_unicode = lambda s: s if isinstance(s, str) else s.decode("utf-8")
    to_binary = lambda s: s.encode("utf-8") if isinstance(s, str) else s
    to_hex = lambda x: hex(x)
    hex_bytes_to_int = lambda b: int(b.hex(), 16)
    binary_ip_to_string = lambda ip: ".".join([str(x) for x in ip])


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
    :param t:
    :return:
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
