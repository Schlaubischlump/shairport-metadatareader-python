from __future__ import print_function, division
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
from .item import Item
from .util import write_data_to_image
from .remote import AirplayRemote

import atexit
import logging
import subprocess
from threading import Thread

try:
    # prefer kivy if its available
    from kivy.event import EventDispatcher
    from kivy.properties import StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
except ImportError:`
    # fallback to eventdispatcher
    from eventdispatcher import EventDispatcher, StringProperty, OptionProperty, ListProperty, DictProperty, \
        LimitProperty as BoundedNumericProperty, Property as ObjectProperty
    BooleanProperty = lambda p: OptionProperty(False, options=[True, False])

logger = logging.getLogger("AirplayListenerLogger")

SHAIRPORT_RUNNING = False


def start_shairport_daemon(exec_path="shairport-sync"):
    """
    Start the shairport daemon if it is not already running.
    :param exec_path: path to the executable
    """
    ret = subprocess.Popen([exec_path, "-d"], stderr=subprocess.PIPE)
    ret.wait()

    if ret.returncode != 0:
        _, err = ret.communicate()
        logger.warning("Can not launch shairport-sync: {0}".format(err.decode("utf-8")))
    else:
        logger.info("Starting shairport-sync daemon.")
        global SHAIRPORT_RUNNING
        SHAIRPORT_RUNNING = True


def stop_shairport_daemon(exce_path="shairport-sync"):
    """
    Stop the shairport daemon if it is running.
    :param exec_path: path to the executable
    """
    global SHAIRPORT_RUNNING
    if not SHAIRPORT_RUNNING:
        return

    ret = subprocess.Popen([exce_path, "-k"], stderr=subprocess.PIPE)
    ret.wait()

    if ret.returncode != 0:
        _, err = ret.communicate()
        logger.warning("Can not stop shairport-sync: {0}".format(err.decode("utf-8")))
    else:
        logger.info("Stopping shairport-sync daemon.")
        SHAIRPORT_RUNNING = False


# if __del__ is not called, we should try to kill shairport when the program terminates
# if this fails, shairport should still be killed when it was started as daemon, but the cleanup of the pid file
# does not happen in this case
atexit.register(stop_shairport_daemon)

# code: dmap.readable_code, data_type
# https://github.com/jkiddo/jolivia/blob/46e53969d4b4bfb4a538511591b9ad2a8f3fca80/jolivia.protocol/src/main/java/org/dyndns/jkiddo/dmp/IDmapProtocolDefinition.java#L154
core_metadata_dict = {"mikd": ("itemkind", "int"),
                      "minm": ("itemname", "str"),
                      "mper": ("persistentid", "int"),
                      "miid": ("itemid", "int"),
                      "asal": ("songalbum", "str"),
                      "asar": ("songartist", "str"),
                      "ascm": ("songcomment", "str"),
                      "asco": ("songcompilation", "bool"),
                      "asbr": ("songbitrate", "int"),
                      "ascp": ("songcomposer", "str"),
                      "asda": ("songdateadded", "date"),
                      "aspl": ("songdateplayed", "date"),
                      "asdm": ("songdatemodified", "date"),
                      "asdc": ("songdisccount", "int"),
                      "asdn": ("songdiscnumber", "int"),
                      "aseq": ("songeqpreset", "str"),
                      "asgn": ("songgenre", "str"),
                      "asdt": ("songdescription", "str"),
                      "asrv": ("songrelativevolume", "int"),
                      "assr": ("songsamplerate", "int"),
                      "assz": ("songsize", "int"),
                      "asst": ("songstarttime", "int"),
                      "assp": ("songstoptime", "int"),
                      "astm": ("songtime", "int"),
                      "astc": ("songtrackcount", "int"),
                      "astn": ("songtracknumber", "int"),
                      "asur": ("songuserrating", "int"),
                      "asyr": ("songyear", "int"),
                      "asfm": ("songformat", "str"),
                      "asdb": ("songdisabled", "bool"),
                      "asdk": ("songdatakind", "int"),
                      "asbt": ("songsbeatsperminute", "int"),
                      "agrp": ("songgrouping", "str"),
                      "ascd": ("songcodectype", "str"),
                      "ascs": ("songcodecsubtype", "int"),
                      "asct": ("songcategory", "str"),
                      "ascn": ("songcontentdescription", "str"),
                      "ascr": ("songcontentrating", "int"),
                      "asri": ("songartistid", "int"),
                      "asai": ("songalbumid", "int"),
                      "askd": ("songlastskipdate", "date"),
                      "assn": ("sortname", "str"),
                      "assu": ("sortalbum", "str"),
                      #"caps": ("playerstate", "int"),         # 1 playing, 2 paused, 3 stopped ?
                      #"cmsr": ("serverrevision", "int"),      # revision number
                      "aeNV": ("itunesnormvolume", "int"),    # com.apple.itunes.norm-volume
                      "aePC": ("itunesispodcast", "bool"),    # com.apple.itunes.is-podcast
                      "aeHV": ("ituneshasvideo", "bool"),     # com.apple.itunes.has-video
                      "aeMK": ("itunesmediakind", "int"),     # com.apple.itunes.mediakind
                      "aeSN": ("itunesseriesname", "str"),    # com.apple.itunes.series-name
                      "aeEN": ("itunesepisodenumstr", "str")  # com.apple.itunes.norm-volume
                      }


class AirplayListener(EventDispatcher):
    connected = BooleanProperty(False)
    '''True if a device is connected, otherwise false.'''

    dacp_id = StringProperty("")
    '''Current DACP-ID of connected device.'''

    active_remote = StringProperty("")
    '''Active remote token used to remote control the airplay device.'''

    host = ListProperty([])
    '''ip-Adress and port number of client.'''

    playback_state = OptionProperty("stop", options=["play", "pause", "stop"])
    '''Playback state.'''

    track_info = DictProperty({})
    '''Information about the currently playing track.'''

    playbackprogress = BoundedNumericProperty(0, min=0.0, max=1.0)
    '''Current playback position as progress from 0 to 1.'''

    artwork = StringProperty("")
    '''Path to artwork file.'''

    user_agent = StringProperty("")
    '''Airplay user agent. e.g. iTunes/12.2 (Macintosh; OS X 10.9.5)'''

    item = ObjectProperty("")
    '''Last received item from the pipe. Use this if you need to react to a specific code.'''

    airplay_volume = BoundedNumericProperty(0, min=0.0, max=1.0)
    '''Volume send by the source e.g. Value ranges from 0 to 1. iTunes. Where -1 means mute.'''

    volume = BoundedNumericProperty(0, min=0.0, max=1.0)
    '''Playback volume. Value ranges from 0 to 1.'''

    mute = BooleanProperty(False)
    '''Is the ariplay device currently muted.'''

    def __init__(self):
        super(AirplayListener, self).__init__()
        self._is_listening = False # is listening for metadata updates
        self._tmp_track_info = {}  # temporary storage for track metadata

        self.track_info = {} # track info send by ssnc

    def __del__(self):
        # try to stop shairport if the instance of this class is destroyed
        stop_shairport_daemon()

    def get_remote(self):
        """
        Get an airplay remote to control the client.
        :return: AirplayRemote Instance.
        """
        # Todo: Check if the clip and dapo fields work ...
        if not self.connected:
            logger.warning("No connected airplay device found.")
            return None
        # add this point the dacp-id and active-remote is already send
        # this might take some time
        return AirplayRemote.get_remote(self.dacp_id, self.active_remote)

    #------------------------------------------------- listening logic -------------------------------------------------

    def start_listening(self, pipe_file="/tmp/shairport-sync-metadata"):
        '''
        Start shairport and continuously read the metadata pipe in a background thread.
        :param pipe_file: path to shairports pipe file
        '''
        def parse_pipe():
            tmp = "" # temporary string which stores one item
            while self._is_listening:
                with open(pipe_file) as f:
                    for line in f:
                        # service was stopped
                        if not self._is_listening:
                            break

                        strip_line = line.strip()
                        if not strip_line.endswith("</item>"):
                            # if this line belongs to the same item
                            tmp += strip_line
                        else:
                            # last line which belongs to the item was reached
                            strip_line = tmp + strip_line
                            tmp = ""
                            self._process_item(strip_line)

        # try to start shairport-sync daemon
        start_shairport_daemon()

        # read the pipe in a background thread
        self._is_listening = True

        t = Thread(target=parse_pipe)
        t.daemon = True
        t.start()

    def stop_listening(self):
        # stop metadata reading
        self._is_listening = False

        # try to stop shairport-sync
        stop_shairport_daemon()

    #------------------------------------------------- data processing -------------------------------------------------

    def _process_item(self, item_str):
        """
        Process a single item from the pipe.
        :param item_str: single string from the pipe representing an item
        :return:
        """
        item = Item.item_from_string(item_str)
        if not item:
            return

        if item.type == "ssnc":
            if item.code == "PICT": # artwork received
                if item.data_base64: # check if picture data is found
                    self.artwork = write_data_to_image(item.data) # Path to artwork image
                self.artwork = None
            elif item.code == "mden": # metadata end
                # only send updates if required
                if not (self._tmp_track_info.items() <= self.track_info.items()):
                    self.track_info = self._tmp_track_info
                    self._tmp_track_info = {}
            elif item.code == "pbeg":  # play stream begin
                # see https://github.com/mikebrady/shairport-sync-metadata-reader/issues/5
                self.connected = True
            elif item.code == "pfls":  # pause stream
                self.playback_state = "pause"
            elif item.code == "prsm":  # play stream start/resume
                self.playback_state = "play"
            elif item.code == "pend":  # play stream end
                self.playback_state = "stop"
                self._tmp_track_info = {}
            elif item.code == "prgr":
                # current track progress as RTP timestamp
                start, cur, end = [float(i) for i in item.data_str.split("/")]
                # playbackposition_in_seconds = max(0, (cur-start)/SAMPLE_RATE)
                # this calculation is just an approximation => limit value to positiv numbers
                self.playbackprogress = min(max(0, (cur-start)/(end-start)), 1.0)
            elif item.code == "pvol": # playback volume
                # "airplay_volume,volume,lowest_volume,highest_volume"
                # where "volume", "lowest_volume" and "highest_volume" are given in dB.
                # The "airplay_volume" is send by the source (e.g. iTunes) to the player
                # and its range starts from 0.00 down to -30.00, whereby -144.00 means "mute".
                airplay_volume, volume, l, h = (float(i) for i in item.data_str.split(','))
                # normalize volume
                self.mute = (airplay_volume == -144)
                self.volume = (volume-l) / (h-l)
                self.airplay_volume = (airplay_volume + 30) / 30
            elif item.code == "daid":  # DACP-ID
                self.dacp_id = item.data_str
            elif item.code == "acre":  # Active-Remote token
                self.active_remote = item.data_str
            elif item.code == "snua":  # Useragent string
                self.user_agent = item.data_str
            elif item.code in ["mdst", "pcen", "pcst", "flsr", "pffr", "dapo", "clip", "svip"]:
                # unused tags:
                #   mdst: metadata is about to be sent
                #   pcst: picture is about to be sent; has rtptime associated with the picture, if available
                #   pcen: picture has been sent; has the rtptime associated with the metadata, if available
                #   flsr: flush requested
                #   pffr: send when the first frame is received
                #   dapo: client port number (not working for me)
                #   clip: source ip-address
                #   svip: server ip-address
                pass
            else:
                logger.warning("Unknown shairport-sync core (ssnc) code \"{0}\", with base64 data {1}.".format(
                    item.code, item.data_base64))

        elif item.type == "core": # dmap.itemkind
            if item.code in core_metadata_dict:
                dmap_key, data_type = core_metadata_dict[item.code]
                # convert data to required type
                if data_type == "int":
                    data = item.data_int
                elif data_type == "str":
                    data = item.data_str
                elif data_type == "date":
                    data = item.data_date
                elif data_type == "bool":
                    data = item.data_bool
                elif data_type == "base64":
                    data = item.data_base64
                # save metadata info
                self._tmp_track_info[dmap_key] = data
            else:
                logger.warning("Unknown DMAP-core code: {0}, with data {1}.".format(item.code, item.data_base64))

        self.item = item
