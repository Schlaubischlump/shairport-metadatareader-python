from socket import gethostname
from paho.mqtt.client import Client

from ..item import Item
from .airplaylistener import AirplayListener, logger

DEFAULT_BROKER = "127.0.0.1" #"iot.eclipse.org""

class AirplayMQTTListener(AirplayListener):
    """
    You should make sure that you configured shairport-sync correctly before using this backend class.
    This listener class only works if you already started your MQTT Broker instance and initialized this class with
    the correct broker hostname. At this time the user login or TLS protection are not supported (this might change in the
    future). Make sure that that you configured shairport-sync to send the raw data (`publish_raw`). The `enable_remote` option
    is not required for the `AirplayRemote` instance to work.
    """
    def __init__(self, broker=DEFAULT_BROKER, topic=gethostname(), *args, **kwargs):
        """
        :param broker: name of the mqtt broker
        :param topic: name of the mqtt broker (Use None to use the default hostname)
        """
        super(AirplayMQTTListener, self).__init__(*args, **kwargs)

        if broker and not isinstance(broker, str):
            raise ValueError("Broker should be the broker hostname as string.")

        self._broker = broker
        self._topic = topic

    @property
    def broker(self):
        """
        :return: MQTT broker as string.
        """
        return self._broker

    def topic(self):
        """
        :return: MQTT topic as string.
        """
        return self._topic

    def receive_message(self, client, userdata, message):
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
            self._client.connect(self.broker)
            self._client.loop_start()
            self._client.subscribe("/{0}/#".format(self._topic))
            logger.info("Subscribe to %s: ...", "/{0}/#".format(self._topic))
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
