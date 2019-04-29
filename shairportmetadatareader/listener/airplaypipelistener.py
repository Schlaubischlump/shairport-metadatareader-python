"""
Module to listen to the pipe backend of shairport-sync.
"""
import os
import stat
from time import sleep
from threading import Thread

from ..item import Item
from .airplaylistener import AirplayListener, logger

# import this name to parse the dafault pipe
DEFAULT_PIPE_FILE = "/tmp/shairport-sync-metadata"


class AirplayPipeListener(AirplayListener):
    """
    Airplay listener class to read the shairport-sync pipe backend.
    """
    def __init__(self, *args, pipe_name=DEFAULT_PIPE_FILE, **kwargs):
        """
        :param pipe_name: path to shairport-sync pipe file
        """
        super(AirplayPipeListener, self).__init__(*args, **kwargs)

        # sanity checks
        if pipe_name and not isinstance(pipe_name, str):
            raise ValueError("Pipefile must be a string.")

        self._pipe_file = pipe_name

    @property
    def pipe_file(self):
        """
        :return: Readonly path to the pipe_file.
        """
        return self._pipe_file

    def start_listening(self):
        """
        Start shairport sync and continuously parse the metadata pipe in a background thread.
        :return:
        """
        super(AirplayPipeListener, self).start_listening()

        thread = Thread(target=self.parse_pipe)
        thread.daemon = True
        thread.start()


    def parse_pipe(self):
        """
        Parse the metadata pipe file and process the information. This method is blocking.
        """
        # wait till the pipe file is found
        while not os.path.exists(self.pipe_file) or not stat.S_ISFIFO(os.stat(self.pipe_file).st_mode):
            logger.warning("Could not find pipe: %s. Retrying in 5 seconds...", self.pipe_file)
            sleep(5)

        self._is_listening = True

        logger.info("Start parsing the pipe %s: ...", self.pipe_file)

        tmp = ""  # temporary string which stores one item
        while self._is_listening:
            with open(self.pipe_file) as pipe:
                for line in pipe:
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
