"""
Module to listen to the MQTT backend of shairport-sync.
"""
from socket import gethostname
from paho.mqtt.client import Client

from ..item import Item
from .airplaylistener import AirplayListener, logger

DEFAULT_BROKER = "127.0.0.1" #"iot.eclipse.org""
DEFAULT_MQTT_PORT = 1883

class AirplayMQTTListener(AirplayListener):
    """
    You should make sure that you configured shairport-sync correctly before using this backend class.
    This listener class only works if you already started your MQTT Broker instance and initialized this class with
    the correct broker hostname. At this time the user login or TLS protection are not supported (this might change in
    the future). Make sure that that you configured shairport-sync to send the raw data (`publish_raw`).
    The `enable_remote` option is not required for the `AirplayRemote` instance to work.
    """
    def __init__(self, *args, hostname=DEFAULT_BROKER, port=DEFAULT_MQTT_PORT, topic=gethostname(), **kwargs):
        """
        :param hostname: name of the mqtt broker
        :param port: port of the mqtt broker as int
        :param topic: name of the mqtt broker (Use None to use the default hostname)
        """
        super(AirplayMQTTListener, self).__init__(*args, **kwargs)

        if hostname and not isinstance(hostname, str):
            raise ValueError("Broker should be the broker hostname as string.")

        self._client = None
        self._broker = hostname
        self._port = port
        self._topic = topic

    @property
    def broker(self):
        """
        :return: MQTT broker as string.
        """
        return self._broker

    @property
    def port(self):
        """
        :return: MQTT broker port as int.
        """
        return self._port

    @property
    def topic(self):
        """
        :return: MQTT topic as string.
        """
        return self._topic

    def receive_message(self, client, userdata, message): # pylint: disable=W0613
        """
        Callback when the MQTT client receives a message.
        :param client: MQTT client instance
        :param userdata:
        :param message: received message
        """
        _, msg_type, msg_code = message.topic.rsplit("/", 2)
        msg_data = message.payload
        item = Item(item_type=msg_type,
                    code=msg_code,
                    text=msg_data,
                    length=len(msg_data),
                    encoding="bytes")
        self._process_item(item)

    def start_listening(self):
        """
        Start shairport sync and continuously parse the metadata mqtt socket in a background thread.
        """
        super(AirplayMQTTListener, self).start_listening()

        self._client = Client("ShairportListener")
        self._client.on_message = self.receive_message
        try:
            self._client.connect(self.broker, port=self.port)
            self._client.loop_start()
            self._client.subscribe("/{0}/#".format(self.topic))
            logger.info("Subscribe to %s: ...", "/{0}/#".format(self.topic))
        except ConnectionRefusedError:
            logger.warning("Connection refused. Make sure that mosquitto is running in the background.")
        else:
            logger.info("Start listening to mqtt broker %s: ...", self.broker)

    def stop_listening(self):
        """
        Stop shairport sync and parsing the mqtt messages.
        :return:
        """
        self._client.disconnect()
        self._client.loop_stop()

        super(AirplayMQTTListener, self).stop_listening()
