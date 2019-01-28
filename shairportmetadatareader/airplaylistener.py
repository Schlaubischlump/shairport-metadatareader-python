from __future__ import division

"""
# See: https://github.com/mikebrady/shairport-sync-metadata-reader
We use two 4-character codes to identify each piece of data, the type and the code.
The first 4-character code, called the type, is either:
- core for all the regular metadadata coming from iTunes, etc., or
- ssnc (for 'shairport-sync') for all metadata coming from Shairport Sync itself, such as start/end delimiters, etc.

For core metadata, the second 4-character code is the 4-character metadata code that comes from iTunes etc. See, 
for example, https://code.google.com/p/ytrack/wiki/DMAP for information about the significance of the codes. 
The original data supplied by the source, if any, follows, and is encoded in base64 format. The length of the data is 
also provided.

For ssnc metadata, the second 4-character code is used to distinguish the messages. Cover art, coming from the source, 
is not tagged in the same way as other metadata, it seems, so is sent as an ssnc type metadata message with the code 
PICT. Progress information, similarly, is not tagged like other source-originated metadata, so it is sent as an ssnc 
type with the code prgr.
"""
import os
import stat
import socket
import logging
from time import sleep
from threading import Thread

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AirplayListenerLogger")

def load_kivy():
    global EventDispatcher, StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
    from kivy.event import EventDispatcher
    from kivy.properties import StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
    logger.info("Using kivy as backend.")

def load_eventdispatcher():
    global EventDispatcher, StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
    from eventdispatcher import EventDispatcher, StringProperty, OptionProperty, ListProperty, DictProperty, \
            LimitProperty as BoundedNumericProperty, Property as ObjectProperty
    BooleanProperty = lambda p: OptionProperty(False, options=[True, False])
    logger.info("Using eventdispatcher as backend.")


# Setting the "PREFER_KIVY" environment flag allows overriding the default behaviour of using kivy as backend.
# Set this flag to "0" to try to load eventdispatcher and fallback to kivy. Using "1" reverses this behavior and tries
# to load kivy before trying to load eventdispatcher (this is the default).
if os.environ.get("PREFER_KIVY", "1") == "0":
    try:
        load_eventdispatcher()
    except ImportError:
        load_kivy()
else:
    try:
        load_kivy()
    except ImportError:
        load_eventdispatcher()


from .item import Item
from .remote import AirplayRemote
from .codetable import CORE, SSNC, core_code_dict, ssnc_code_dict
from .util import write_data_to_image, to_unicode, hex_bytes_to_int
from .shairport import stop_shairport_daemon, start_shairport_daemon


# import this name to parse the dafault pipe
DEFAULT_PIPE_FILE = "/tmp/shairport-sync-metadata"
# import this name to use the dafault socket
DEFAULT_SOCKET = ("127.0.0.1", 5555)

# core codes which should be included in the track information field
CORE_CODE_WHITELIST = {'mikd', 'minm', 'mper', 'miid', 'asal', 'asar', 'ascm', 'asco', 'asbr', 'ascp', 'asda', 'aspl',
                       'asdm', 'asdc', 'asdn', 'aseq', 'asgn', 'asdt', 'asrv', 'assr', 'assz', 'asst', 'assp', 'astm',
                       'astc', 'astn', 'asur', 'asyr', 'asfm', 'asdb', 'asdk', 'asbt', 'agrp', 'ascd', 'ascs', 'asct',
                       'ascn', 'ascr', 'asri', 'asai', 'askd', 'assn', 'assu', 'aeNV', 'aePC', 'aeHV', 'aeMK', 'aeSN',
                       'aeEN'}


class AirplayListener(EventDispatcher):

    connected = BooleanProperty(False)
    '''True if a device is connected, otherwise false.'''

    has_remote_data = BooleanProperty(False)
    '''
    True if the dacp_id and active_remote token are available. An event might be better suited for this case. 
    Todo: Find a way to make the event dispatching work with kivy and event dispatcher.
    '''

    dacp_id = StringProperty("")
    '''Current DACP-ID of connected device.'''

    active_remote = StringProperty("")
    '''Active remote token used to remote control the airplay device.'''

    client_name = StringProperty("")
    '''Name of the airplay client e.g John's iPhone.'''

    playback_state = OptionProperty("stop", options=["play", "pause", "stop"])
    '''Playback state.'''

    track_info = DictProperty({})
    '''Information about the currently playing track.'''

    playback_progress = ListProperty([])
    '''(current playback position, duration) of the track'''

    artwork = StringProperty("")
    '''Path to artwork file.'''

    user_agent = StringProperty("")
    '''Airplay user agent. e.g. iTunes/12.2 (Macintosh; OS X 10.9.5)'''

    item = ObjectProperty(None)
    '''Last received item from the pipe. Use this if you need to react to a specific code.'''

    airplay_volume = BoundedNumericProperty(0, min=0.0, max=1.0)
    '''Volume send by the source e.g. Value ranges from 0 to 1. iTunes. Where -1 means mute.'''

    volume = BoundedNumericProperty(0, min=0.0, max=1.0)
    '''Playback volume. Value ranges from 0 to 1.'''

    mute = BooleanProperty(False)
    '''Is the ariplay device currently muted.'''

    # ------------------------------------------ constructor/destructor ------------------------------------------------

    def __init__(self, sample_rate=44100):
        """
        :param sample_rate: sample_rate used by shairport-sync. Needed to calculate the playback progress.
        """
        super(AirplayListener, self).__init__()
        self._sample_rate = sample_rate  # sample rate used by shairport-sync
        self._is_listening = False  # is listening for metadata updates
        self._tmp_track_info = {}   # temporary storage for track metadata

        self.playback_progress = []  # playback progress send by ssnc

        self.track_info = {}  # track info send by ssnc
        self._artwork = ""
        self._has_remote_data = [False, False]  # [has dacp_id, has active_remote]

        # There is a bug (?) inside shairport where sometimes after pause if pressed another play command is send,
        # although play was not pressed.
        # Normally a progress message is send before or directly after a play message is send.
        # Check if progress is send before play or if play was send before progress. If so then change the playback
        # state to "play".
        self._did_receive_progress_msg = False
        self._did_receive_play_msg = False

    def __del__(self):
        # try to stop shairport if the instance of this class is destroyed
        stop_shairport_daemon()

    # ---------------------------------------------- airplay remote ----------------------------------------------------

    def get_remote(self, timeout=5):
        """
        Get an airplay remote to control the client.
        :return: AirplayRemote Instance.
        """

        # use zeroconf to find the remote
        if not self.has_remote_data:
            logger.warning("No connected airplay device found.")
            return None
        # at this point the dacp-id and active-remote is already send
        # this might take some time
        return AirplayRemote.get_remote(self.dacp_id, self.active_remote, timeout=timeout)

    # ------------------------------------------------ listening logic -------------------------------------------------

    def start_listening(self, pipe_file=None, socket_addr=None):
        """
        Start shairport-sync and continuously parse the metadata pipe or the UDP server in a background thread.
        If pipe_file and socket_addr are both None, this method will fall back to parsing the DEFAULT_PIPE_FILE.
        You should only specify the pipe_file or the socket_addr at a time. If you set both arguments, the pipe_file
        will be used and the socket_addr is ignored.
        :param pipe_file: path to shairport-sync pipe file
        :param socket_addr: tuple consisting of (socket_ip, socket_port)
        """
        if pipe_file and socket_addr:
            logger.warning("Ambiguous parameter configuration. Falling back to pipe_file.")

        # use the default pipe if no pipe and no socket is specified
        if not pipe_file and not socket_addr:
            pipe_file = DEFAULT_PIPE_FILE

        # sanity checks
        if pipe_file and not isinstance(pipe_file, str):
            raise ValueError("Pipefile must be a string.")

        if socket_addr and not (isinstance(socket_addr, list) or isinstance(socket_addr, tuple)):
            raise ValueError("Socket_addr must be a tuple consisting of the ip address and the port number.")

        # try to start shairport-sync daemon
        start_shairport_daemon()

        # read the pipe or the socket in a background thread
        if pipe_file:
            t = Thread(target=self.parse_pipe, args=(pipe_file,))
        else:
            t = Thread(target=self.parse_socket, args=(socket_addr,))
        t.daemon = True
        t.start()

    def stop_listening(self):
        """
        Stop parsing the metadata pipe or the UDP server and stop the shairport-sync daemon if it was started inside the
        start_listening method.
        """
        # stop metadata reading
        self._is_listening = False

        # try to stop shairport-sync
        stop_shairport_daemon()

    def parse_socket(self, socket_addr=DEFAULT_SOCKET, buffer_size=65000):
        """
        Parse the udp socket for metadata information. This method is blocking.
        :param socket_addr: tuple consisting of (ip_str, port_number)
        :param buffer_size: default buffer size to receive (65000 is the shairport-sync default)
        """
        sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)  # Internet UDP socket
        sock.bind(socket_addr)

        self._is_listening = True

        i = 0        # number of chunks which were already received
        chunks = []  # list with all chunks

        while self._is_listening:
            msg_data, addr = sock.recvfrom(buffer_size)
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

    def parse_pipe(self, pipe_file=DEFAULT_PIPE_FILE):
        """
        Parse the metadata pipe file and process the information. This method is blocking.
        :param pipe_file: path to the pipe file
        """
        # wait till the pipe file is found
        while not os.path.exists(pipe_file) or not stat.S_ISFIFO(os.stat(pipe_file).st_mode):
            logger.warning("Could not find pipe: {0}. Retrying in 5 seconds...".format(pipe_file))
            sleep(5)

        self._is_listening = True

        tmp = ""  # temporary string which stores one item
        while self._is_listening:
            with open(pipe_file) as f:
                for line in f:
                    # service was stopped
                    if not self._is_listening:
                        break

                    strip_line = line.strip()
                    if strip_line.endswith("</item>"):
                        item = Item.item_from_xml_string(tmp + strip_line)
                        if item:
                            self._process_item(item)
                        tmp = ""
                    elif strip_line.startswith("<item>"):
                        # if only a closing tag is missing we try to close the tag and try to parse the data
                        if tmp != "":
                            item = Item.item_from_xml_string(tmp + "</item>")
                            if item:
                                self._process_item(item)
                        tmp = strip_line
                    else:
                        tmp += strip_line

    # ------------------------------------------------ data processing -------------------------------------------------

    def _process_item(self, item):
        """
        Process a single item from the pipe.
        :param item: metadata item
        """
        if item.type == SSNC:
            # snua or snam are the 'ANNOUNCE' packet to reserve the player
            if item.code == "snua":
                # receive new device information
                self.user_agent = item.data()

                self.connected = True
                if all(self._has_remote_data):
                    self._has_remote_data = [False, False]
            elif item.code == "snam":
                self.client_name = item.data()

                # the device name can be the ANNOUNCE package as well
                self.connected = True
                if all(self._has_remote_data):
                    self._has_remote_data = [False, False]
            elif item.code == "pcst":
                # reset artwork
                self.artwork = ""
            elif item.code == "PICT":
                if item.data_base64:  # check if picture data is found
                    self._artwork = write_data_to_image(item.data())  # Path to artwork image
                else:
                    self._artwork = ""
            elif item.code == "pcen":
                # send artwork when all data is received
                self.artwork = self._artwork
            elif item.code == "mdst":
                # reset track information when new metadata starts
                # self.track_info = {}
                pass
            elif item.code == "mden":
                # only send updates if required
                #if not (self._tmp_track_info.items() <= self.track_info.items()):
                self.track_info = self._tmp_track_info
                self._tmp_track_info = {}
            elif item.code == "pfls":
                self.playback_state = "pause"
                self._did_receive_progress_msg = False
                self._did_receive_play_msg = False
            elif item.code == "prsm":
                self._did_receive_play_msg = True
                # workaround for a bug inside shairport (see __init__ for details)
                if self._did_receive_progress_msg:
                    self.playback_state = "play"
                    self._did_receive_progress_msg = False
                    self._did_receive_play_msg = False
            # to inaccurate
            elif item.code == "pend":
                self.playback_state = "stop"
                #self.track_info = {}
                self._did_receive_progress_msg = False
                self._did_receive_play_msg = False
                self.connected = False
            elif item.code == "prgr":
                self._did_receive_progress_msg = True
                # workaround for a bug inside shairport (see __init__ for details)
                if self._did_receive_play_msg:
                    self.playback_state = "play"
                    self._did_receive_progress_msg = False
                    self._did_receive_play_msg = False

                # this calculation seems inaccurate => limit the values to positive numbers
                start, cur, end = item.data()
                self.playback_progress = [max(0, (cur-start)/self._sample_rate), max(0, (end-start)/self._sample_rate)]
                #start, cur, end = item.data() # (start, current track progress, end) as RTP timestamp
                #self.playback_progress = min(max(0, (cur-start)/(end-start)), 1.0)
            elif item.code == "pvol":
                # normalize volume
                airplay_volume, volume, l, h = item.data()
                self.mute = (airplay_volume == -144)
                self.volume = max(0, (volume-l) / (h-l))
                self.airplay_volume = max(0, (airplay_volume + 30) / 30)
            elif item.code == "daid":
                self.dacp_id = item.data()
                self._has_remote_data[0] = True
            elif item.code == "acre":
                self.active_remote = item.data()
                self._has_remote_data[1] = True
            elif item.code in ssnc_code_dict:
                # unused tag recognized => just ignore it
                pass
            else:
                logger.warning("Unknown shairport-sync core (ssnc) code \"{0}\", with base64 data {1}.".format(
                    item.code, item.data_base64))

        elif item.type == CORE:
            if item.code in CORE_CODE_WHITELIST:
                # save metadata info
                dmap_key, data_type = core_code_dict[item.code]
                self._tmp_track_info[dmap_key] = item.data(dtype=data_type)
            elif item.code in core_code_dict:
                # just ignore these and don't add them to the track info
                # you can still listen to the item property to respond to these keys
                pass
            else:
                logger.warning("Unknown DMAP-core code: {0}, with data {1}.".format(item.code, item.data_base64))

        # send a callback if dacp_id and active_remote token are received
        if all(self._has_remote_data):
            self.has_remote_data = True
            self._has_remote_data = [False, False]

        self.item = item
