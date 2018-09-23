import logging
from time import sleep
from threading import Thread

AIRPLAY_PREFIX = "iTunes_Ctrl_"

logger = logging.getLogger("AirplayServiceListenerLogger")


class AirplayServiceListener(object):
    """
    Listener for incoming airplay connections.
    """
    def __init__(self, dacp_id):
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