# -*- coding: utf-8 -*-
"""
Test the basic AirplayListener functionality.
"""
import socket
from unittest import TestCase, main
from zeroconf import ServiceInfo, Zeroconf

from shairportmetadatareader.listener.airplaylistener import AirplayListener
from shairportmetadatareader.item import Item
from shairportmetadatareader.codetable import CORE_CODE_DICT
from shairportmetadatareader.remote.airplayservicelistener import AIRPLAY_PREFIX


LOCALHOST = "127.0.0.1"
AIRPLAY_PORT = 63309


class TestAirplayListener(TestCase):
    """
    Class to test the AirplayListener base class.
    """

    def test_process_item(self):
        """
        :return:
        """
        # nonlocal is not available in python2, therefore use a list instead
        binding_was_called = [False]

        # check if the metadata is written to track_info and the callback is executed
        def on_track_info(_, info):
            self.assertTrue(len(info) > 0)
            binding_was_called[0] = True

        listener = AirplayListener()
        # check if the bindings are working
        listener.bind(track_info=on_track_info)

        def execute_step(item_str):
            item = Item.item_from_xml_string(item_str)
            listener._process_item(item) # pylint: disable=W0212
            return item

        # snua -- User Agent
        execute_step('<item><type>73736e63</type><code>736e7561</code><length>15</length><data encoding="base64">'
                     'QWlyUGxheS8zNzEuNC43</data></item>')
        self.assertTrue(listener.connected)
        self.assertEqual(listener.user_agent, "AirPlay/371.4.7")

        # acre -- Active Remote
        item = execute_step('<item><type>73736e63</type><code>61637265</code><length>10</length><data encoding='
                            '"base64">NDEzNzc5MjkxOA==</data></item>')
        self.assertEqual(listener.active_remote, item.data())

        # daid -- DACP ID
        item = execute_step('<item><type>73736e63</type><code>64616964</code><length>16</length><data encoding='
                            '"base64">OEFBQTEyQzY2RDRBNzkwQQ==</data></item>')
        self.assertEqual(listener.dacp_id, item.data())

        # artwork -- Begin artwork
        item = execute_step('<item><type>73736e63</type><code>70637374</code><length>10</length><data encoding='
                            '"base64">MjcyMTk4ODg1MQ==</data></item>')
        self.assertEqual(listener.artwork, "")

        # metadata -- Send a test metadata which should be included in the track_info dict
        item = execute_step('<item><type>636f7265</type><code>6d706572</code><length>8</length><data encoding='
                            '"base64">dx08hG5Yf8g=</data></item>')

        # end sending metadata -- Check if the track_info was written to the dictionary
        execute_step('<item><type>73736e63</type><code>6d64656e</code><length>10</length><data encoding="base64">'
                     'MjcyMjAxODYwMA==</data></item>')
        dmap_key, data_type = CORE_CODE_DICT[item.code]
        self.assertTrue(listener.track_info[dmap_key] == item.data(data_type))

        # the track_info must be changed at this point => the binding function must already been called if everything
        # is working correctly
        self.assertTrue(binding_was_called[0])

    def test_get_remote(self):
        """
        :return:
        """
        listener = AirplayListener()

        def execute_step(item_str):
            # Send user agent
            item = Item.item_from_xml_string(item_str)
            listener._process_item(item) # pylint: disable=W0212
            return item

        # snua -- User Agent
        execute_step('<item><type>73736e63</type><code>736e7561</code><length>15</length><data encoding="base64">'
                     'QWlyUGxheS8zNzEuNC43</data></item>')

        # acre -- Active Remote
        execute_step('<item><type>73736e63</type><code>61637265</code><length>10</length><data encoding="base64">'
                     'NDEzNzc5MjkxOA==</data></item>')

        # daid -- DACP ID
        execute_step('<item><type>73736e63</type><code>64616964</code><length>16</length><data encoding="base64">'
                     'OEFBQTEyQzY2RDRBNzkwQQ==</data></item>')

        # register a fake airplay client service to receive events
        zero_conf = Zeroconf()
        service_id = AIRPLAY_PREFIX + listener.dacp_id + "._dacp._tcp.local."
        info = ServiceInfo("_dacp._tcp.local.", service_id, socket.inet_aton(LOCALHOST), AIRPLAY_PORT, 0, 0, {})
        zero_conf.register_service(info)

        # get a reference to the remote
        remote = listener.get_remote(timeout=2)

        # remove the fake service
        zero_conf.unregister_service(info)

        # check if we were able to create a remote
        self.assertTrue(remote is not None)


if __name__ == "__main__":
    main()
