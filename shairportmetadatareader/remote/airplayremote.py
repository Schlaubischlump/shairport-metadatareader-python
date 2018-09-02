"""
Airplay remote control.
See: https://nto.github.io/AirPlay.html
"""

import sys
import logging
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("AirplayListenerLogger")


import requests
from enum import Enum
from time import sleep
from threading import Thread

from zeroconf import ServiceBrowser, Zeroconf

IS_PY2 = sys.version_info.major <= 2

if IS_PY2:
    binary_ip_to_string = lambda ip: ".".join([str(ord(x)) for x in ip])
    to_unicode = lambda s: s.decode("utf-8") if isinstance(s, str) else s
else:
    binary_ip_to_string = lambda ip: ".".join([str(x) for x in ip])
    to_unicode = lambda s: s if isinstance(s, str) else s.decode("utf-8")


AIRPLAY_PREFIX = "iTunes_Ctrl_"
AIRPLAY_ZEROCONF_SERVICE = "_dacp._tcp.local."


class AirplayServiceListener(object):
    """
    Listener for incoming airplay connections.
    """
    def __init__(self, dacp_id, conf):
        """
        :param dacp_id: expected name of the connected airplay service
        :param conf: zeroconf instance
        """
        self.name = None
        self._expected_name = AIRPLAY_PREFIX + dacp_id
        self.info = None
        self.is_listening = False

    def remove_service(self, zeroconf, type, name):
        if name.startswith(self._expected_name):
            logger.info("Removed airplay service: {0}".format(name))
            self.name = None
            self.info = None
        else:
            logger.info("Service removed: {0}".format(name))

    def add_service(self, zeroconf, type, name):
        """
        Called when a new service is detected
        :param zeroconf:
        :param type:
        :param name: name of the service
        """
        info = zeroconf.get_service_info(type, name)
        if name.startswith(self._expected_name):
            self.name = name
            self.info = info
            logger.info("Added airplay service: {0} {1}".format(name, info))
        else:
            logger.info("Service added: {0} {1}".format(name, info))

    def start_listening(self):
        """
        Wait for an incoming connection.
        :return waiting thread instance
        """
        def wait():
            while True:
                # found a connection
                if (self.name and self.info) or not self.is_listening:
                    self.stop_listening()
                    break
                sleep(1)

        self.is_listening = True

        t = Thread(target=wait)
        t.daemon=True
        t.start()
        return t

    def stop_listening(self):
        """
        Cancel waiting for incoming connection.
        """
        self.is_listening = False


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


class AirplayRemote(object):
    """
    Remote control an airplay device.
    """
    def __init__(self, dacp_id, active_remote, host, port, hostname=None):
        """
        :param dacp_id: dacp_id of the connected client
        :param token:
        """
        super(AirplayRemote, self).__init__()

        self.token = active_remote
        self.dacp_id = dacp_id
        self.host = host
        self.port = port
        self.base_url = "{0}:{1}/ctrl-int/1/".format(host, port)
        # optional hostname
        self.hostname = hostname

    @classmethod
    def get_remote(cls, dacp_id, token):
        """
        :param dacp_id: dacp_id of the client
        :param token: token of client
        :return: instance of AirplayRemote
        """
        zeroconf = Zeroconf()
        listener = None
        try:
            listener = AirplayServiceListener(dacp_id, zeroconf)
            browser = ServiceBrowser(zeroconf, AIRPLAY_ZEROCONF_SERVICE, listener)
            wait_thread = listener.start_listening()
            wait_thread.join()
        except Exception as e:
            print(e)
        finally:
            zeroconf.close()

        # connection established
        if listener and listener.info:
            host = "http://" + binary_ip_to_string(listener.info.address)
            port = listener.info.port
            return cls(dacp_id, token, host, port, hostname=listener.info.server)
        return None

    def send_command(self, command):
        """
        Send a get request to the airplay client.
        :param command: command as string or AirplayCommand to send
        :return request object
        """
        command = command.value if isinstance(command, AirplayCommand) else command
        headers = {"Active-Remote": self.token}
        url = self.base_url + to_unicode(command)
        return requests.get(url, headers=headers, verify=False)
