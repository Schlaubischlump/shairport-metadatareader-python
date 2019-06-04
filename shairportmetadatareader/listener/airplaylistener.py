"""
See: https://github.com/mikebrady/shairport-sync-metadata-reader

We use two 4-character codes to identify each piece of data, the type and the code.
The first 4-character code, called the type, is either:
- core for all the regular metadata coming from iTunes, etc., or
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
from __future__ import division

import os
import logging


from ..remote import AirplayRemote
from ..codetable import CORE, SSNC, CORE_CODE_DICT, SSNC_CODE_DICT
from ..util import write_data_to_image
from ..shairport import stop_shairport_daemon, start_shairport_daemon


# pylint: disable=C0103
logger = logging.getLogger("AirplayListenerLogger")
logger.setLevel(logging.INFO)

def load_kivy():
    """
    Load all required Properties from kivy.
    """
    # pylint: disable=W0602, W0601
    global EventDispatcher, StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
    from kivy.event import EventDispatcher
    # pylint: disable=W0621, E0611
    from kivy.properties import StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty,\
        ListProperty, ObjectProperty
    logger.info("Using kivy as backend.")


def load_eventdispatcher():
    """
    Load all required Properties from eventdispatcher.
    """
    # pylint: disable=W0602, W0601
    global EventDispatcher, StringProperty, OptionProperty, DictProperty, BooleanProperty, BoundedNumericProperty, \
        ListProperty, ObjectProperty
    # pylint: disable=W0621, E0611
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


# core codes which should be included in the track information field
CORE_CODE_WHITELIST = {'mikd', 'minm', 'mper', 'miid', 'asal', 'asar', 'ascm', 'asco', 'asbr', 'ascp', 'asda', 'aspl',
                       'asdm', 'asdc', 'asdn', 'aseq', 'asgn', 'asdt', 'asrv', 'assr', 'assz', 'asst', 'assp', 'astm',
                       'astc', 'astn', 'asur', 'asyr', 'asfm', 'asdb', 'asdk', 'asbt', 'agrp', 'ascd', 'ascs', 'asct',
                       'ascn', 'ascr', 'asri', 'asai', 'askd', 'assn', 'assu', 'aeNV', 'aePC', 'aeHV', 'aeMK', 'aeSN',
                       'aeEN'}


# pylint: disable=R0902, E0602
class AirplayListener(EventDispatcher):
    """
    Abstract class to listen to shairport metadata events and receive a remote control instance to control playback.
    You should NOT use this class directly but instead subclass it. Subclasses should override at least the
    `start_listening` method.
    """

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

    def __init__(self, sample_rate=44100, **kwargs):
        """
        :param sample_rate: sample_rate used by shairport-sync. Needed to calculate the playback progress.
        """
        # pylint: disable=W0613
        super(AirplayListener, self).__init__()
        self._sample_rate = sample_rate  # sample rate used by shairport-sync
        self._is_listening = False  # is listening for metadata updates
        self._tmp_track_info = {}   # temporary storage for track metadata

        self.playback_progress = []  # playback progress send by ssnc

        self.track_info = {}  # track info send by ssnc
        self._artwork = ""
        self._has_remote_data = [False, False]  # [has dacp_id, has active_remote]

        # There is a "bug" inside shairport where sometimes after pause is pressed another play command is send,
        # although play was not pressed by the user.
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

    # -------------------------------------------- start / stop listening ----------------------------------------------

    def start_listening(self): # pylint: disable=R0201
        """
        Start shairport-sync and continuously parse the metadata in a background thread.
        Each subclass should override this method.
        """
        # try to start shairport-sync daemon
        start_shairport_daemon()

    def stop_listening(self):
        """
        Stop parsing the metadata and stop the shairport-sync daemon started inside the start_listening method.
        """
        # stop metadata reading
        self._is_listening = False

        # try to stop shairport-sync
        stop_shairport_daemon()

    # ------------------------------------------------ data processing -------------------------------------------------

    # pylint: disable=R0912, R0915
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
                # workaround for a "bug" inside shairport (see __init__ for details)
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
                # workaround for a "bug" inside shairport (see __init__ for details)
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
            elif item.code in SSNC_CODE_DICT:
                # unused tag recognized => just ignore it
                pass
            else:
                logger.warning("Unknown shairport-sync core (ssnc) code \"%s\", with base64 data %s.", item.code,
                               item.data_base64)

        elif item.type == CORE:
            if item.code in CORE_CODE_WHITELIST:
                # save metadata info
                dmap_key, data_type = CORE_CODE_DICT[item.code]
                self._tmp_track_info[dmap_key] = item.data(dtype=data_type)
            elif item.code in CORE_CODE_DICT:
                # just ignore these and don't add them to the track info
                # you can still listen to the item property to respond to these keys
                pass
            else:
                logger.warning("Unknown DMAP-core code: %s, with data %s.", item.code, item.data_base64)

        # send a callback if dacp_id and active_remote token are received
        if all(self._has_remote_data):
            self.has_remote_data = True
            self._has_remote_data = [False, False]

        self.item = item
