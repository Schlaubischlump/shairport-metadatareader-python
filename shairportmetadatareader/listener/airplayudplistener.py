"""
Module to listen to the udp backend of shairport-sync.
"""
import socket
from threading import Thread

from ..item import Item
from ..util import to_unicode, hex_bytes_to_int
from .airplaylistener import AirplayListener, logger


# import this name to use the dafault socket
DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 5555


class AirplayUDPListener(AirplayListener):
    """
    Airplay listener class to read the shairport-sync udp server backend.
    """
    def __init__(self, *args, socket_address=DEFAULT_ADDRESS, socket_port=DEFAULT_PORT, **kwargs):
        """
        :param socket_addr: tuple consisting of (socket_ip, socket_port)
        """
        super(AirplayUDPListener, self).__init__(*args, **kwargs)

        self._socket_addr = (socket_address, socket_port)

    @property
    def socket_addr(self):
        """
        :return: UPD socket address and port.
        """
        return self._socket_addr

    def start_listening(self):
        """
        Start shairport sync and continuously parse the metadata socket in a background thread.
        """
        super(AirplayUDPListener, self).start_listening()

        thread = Thread(target=self.parse_socket)
        thread.daemon = True
        thread.start()

    def parse_socket(self, buffer_size=65000):
        """
        Parse the udp socket for metadata information. This method is blocking.
        :param buffer_size: default buffer size to receive (65000 is the shairport-sync default)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet UDP socket
        sock.bind(self.socket_addr)

        self._is_listening = True

        logger.info("Start listening to socket %s:%s...", self.socket_addr[0], self.socket_addr[1])

        i = 0        # number of chunks which were already received
        chunks = []  # list with all chunks

        while self._is_listening:
            msg_data, _ = sock.recvfrom(buffer_size)
            item_type = to_unicode(msg_data[:4])
            code = to_unicode(msg_data[4:8])

            if code == "chnk":
                # accumulate data if only a chunk is send
                i += 1
                chunk_index = hex_bytes_to_int(msg_data[8:12])   # position of the chunk inside the target bytes array
                chunk_count = hex_bytes_to_int(msg_data[12:16])  # amount of chunks which need to be received
                # create an empty dummy array for all chunks
                if not chunks:
                    chunks = [b""]*chunk_count
                # insert data chunk into the array at the correct position
                # there is no guarantee that the chunks are received in the correct order
                chunks[chunk_index] = msg_data[24:]

                # all chunks were received => create the item
                if chunk_count == i:
                    item = Item(item_type=to_unicode(msg_data[16:20]),
                                code=to_unicode(msg_data[20:24]),
                                text=b"".join(chunks),
                                length=sum(len(c) for c in chunks),
                                encoding="bytes")
                    self._process_item(item)
            else:
                # reset chunk data if at least one chunk was received in the meantime
                if i > 0:
                    i = 0
                    chunks = []

                # process normal message which might include an optional argument
                item = Item(item_type, code, text=msg_data[8:] or None, length=len(msg_data)-8, encoding="bytes")
                self._process_item(item)
