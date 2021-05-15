"""
Service listener instance to detect airplay services.
"""
import logging
from time import sleep
from threading import Thread

AIRPLAY_PREFIX = "iTunes_Ctrl_"

# pylint: disable=C0103
logger = logging.getLogger("AirplayServiceListenerLogger")
logger.setLevel(logging.INFO)


class AirplayServiceListener(object): # pylint: disable=R0205
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

    def remove_service(self, zeroconf, stype, name):
        """
        Called when a service is removed.
        :param zeroconf: zeroconf instance
        :param stype: type of the service
        :param name: name of the service
        """
        # pylint: disable=W0613
        if name.startswith(self._expected_name):
            logger.info("Removed airplay service: %s", name)
            self.name = None
            self.info = None
        else:
            logger.info("Service removed: %s", name)

    def add_service(self, zeroconf, stype, name):
        """
        Called when a new service is detected.
        :param zeroconf: zeroconf instance
        :param stype: type of the service
        :param name: name of the service
        """
        info = zeroconf.get_service_info(stype, name)
        if name.startswith(self._expected_name):
            self.name = name
            self.info = info
            logger.info("Added airplay service: %s %s", name, info)
        else:
            logger.info("Service added: %s %s", name, info)

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

        thread = Thread(target=wait)
        thread.daemon = True
        thread.start()
        return thread

    def stop_listening(self):
        """
        Cancel waiting for incoming connection.
        """
        self.is_listening = False
        
    def update_service(*args):
        pass
