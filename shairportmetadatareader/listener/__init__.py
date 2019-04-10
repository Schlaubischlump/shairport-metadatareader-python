from .airplaylistener import logger
from .airplaypipelistener import AirplayPipeListener, DEFAULT_PIPE_FILE
from .airplayudplistener import AirplayUDPListener, DEFAULT_SOCKET

__all__ = ["AirplayUDPListener", "AirplayPipeListener", "AirplayMQTTListener", "DEFAULT_SOCKET", "DEFAULT_PIPE_FILE",
           "logger"]

# Import mqtt backend if the necessary frameworks are available.
try:
    import paho.mqtt
except ImportError:
    logger.warning("Can not find paho-mqtt library. AirplayMQTTListener is therefore not available.")
else:
    from .airplaymqttlistener import AirplayMQTTListener, DEFAULT_BROKER
    __all__ += ["AirplayMQTTListener", "DEFAULT_BROKER"]


