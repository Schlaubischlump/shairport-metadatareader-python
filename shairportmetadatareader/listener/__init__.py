"""
Package containing different listener classes for various backends.
"""
from .airplaylistener import logger
from .airplaypipelistener import AirplayPipeListener, DEFAULT_PIPE_FILE
from .airplayudplistener import AirplayUDPListener, DEFAULT_PORT, DEFAULT_ADDRESS

__all__ = ["AirplayUDPListener", "AirplayPipeListener", "AirplayMQTTListener", "DEFAULT_PORT", "DEFAULT_ADDRESS",
           "DEFAULT_PIPE_FILE", "logger"]

# Import mqtt backend if the necessary frameworks are available.
try:
    import paho.mqtt
except ImportError:
    logger.warning("Can not find paho-mqtt library. AirplayMQTTListener is therefore not available. If you wish to use "
                   "this backend run: pip install paho-mqtt.")
else:
    from .airplaymqttlistener import AirplayMQTTListener, DEFAULT_BROKER, DEFAULT_MQTT_PORT
    __all__ += ["AirplayMQTTListener", "DEFAULT_BROKER", "DEFAULT_MQTT_PORT"]
