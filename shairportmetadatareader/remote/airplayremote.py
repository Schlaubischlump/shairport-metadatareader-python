"""
Airplay remote control.
See: https://nto.github.io/AirPlay.html#audio-remotecontrol
"""
from enum import Enum
import logging
import requests
from ..util import to_unicode

# pylint: disable=C0103
logger = logging.getLogger("AirplayRemoteLogger")
logger.setLevel(logging.INFO)

AIRPLAY_ZEROCONF_SERVICE = "_dacp._tcp.local."


# ---------------------------------------- available remote commands ---------------------------------------------------

class AirplayCommand(Enum):
    """
    Available airplay commands.
    """
    BEGIN_FAST_FORWARD = "beginff"
    BEGIN_REWIND = "beginrew"
    PREVIOUS_SONG = "previtem"
    NEXT_SONG = "nextitem"
    PAUSE = "pause"
    PLAY_PAUSE = "playpause"
    PLAY = "play"
    STOP = "stop"
    PLAY_RESUME = "playresume"
    SHUFFLE_SONGS = "shuffle_songs"
    VOLUME_DOWN = "volumedown"
    VOLUME_UP = "volumeup"

    def __str__(self):
        return self.value


# ------------------------------------------ remote control client -----------------------------------------------------

class AirplayRemote(object): # pylint: disable=R0205
    """
    Remote control an airplay device.
    """
    def __init__(self, dacp_id, active_remote, host, port, hostname=None): # pylint: disable=R0913
        """
        :param dacp_id: dacp_id of the connected client
        :param active_remote: active remote token
        :param host: ip address to send the commands to
        :param port: port to send the commands to
        :param hostname: optional hostname used for logging purposes
        """
        super(AirplayRemote, self).__init__()

        self.token = active_remote
        self.dacp_id = dacp_id
        self.host = host
        self.port = port
        self.base_url = "http://{0}:{1}/ctrl-int/1/".format(host, port)
        self.hostname = hostname

    @classmethod
    def get_remote(cls, dacp_id, token, timeout):
        """
        :param dacp_id: clients dacp_id
        :param token: token of client
        :param timeout: time after which the search for the airplay remote will be terminated
        :return: instance of AirplayRemote
        """
        from zeroconf import ServiceBrowser, Zeroconf
        from .airplayservicelistener import AirplayServiceListener
        from ..util import binary_ip_to_string

        zeroconf = Zeroconf()
        listener = None
        try:
            listener = AirplayServiceListener(dacp_id)
            browser = ServiceBrowser(zeroconf, AIRPLAY_ZEROCONF_SERVICE, listener) # pylint: disable=W0612
            wait_thread = listener.start_listening()
            wait_thread.join(timeout=timeout)
            # if the thread is still alive a timeout occurred
            if wait_thread.is_alive():
                listener.stop_listening()
                return None
        except Exception as exc: # pylint: disable=W0703
            logger.warning(exc)
        finally:
            zeroconf.close()

        # connection established
        if listener and listener.info:
            host = binary_ip_to_string(listener.info.address if hasattr(listener.info, "address") else listener.info.addresses[0])
            return cls(dacp_id, token, host, listener.info.port, hostname=listener.info.server)
        return None

    def send_command(self, command):
        """
        Send a get request to the airplay client.
        :param command: command to send as string or AirplayCommand
        :return request object
        """
        command = str(command)
        headers = {"Active-Remote": self.token}
        url = self.base_url + to_unicode(command)
        return requests.get(url, headers=headers, verify=False)
