"""
libconf_init Example
====================================================
This example demonstrates a simple method to read the shairport-sync.conf file and create an AirplayListener instance
according to the available configured backends.
"""

import time
import io, libconf

import shairportmetadatareader

DEFAULT_CONF_PATH =  "/etc/shairport-sync.conf" #"/usr/local/etc/shairport-sync/shairport-sync.conf"


class MetadataNotEnabledError(Exception):
    """
    Thrown if the metadata section inside the shairport-sync.conf is not enabled.
    """
    pass


class NoBackendAvailableError(Exception):
    """
    Thrown if neither the metadata pipe, nor the udp or mqtt backends are configured.
    """
    pass


def get_listener_for_config_file(path):
    """
    Create an AirplayListener instance according to a specific config file.
    The UDP backend is the prefered method to use. If this backend isn't available the pipe backend is used. If neither
    of those is configured this method falls back to use the MQTT backend.
    :param path: path to the shairport-sync.conf file
    :return: AirplayListener instance
    """
    config_file = io.open(DEFAULT_CONF_PATH)
    config = libconf.load(config_file)
    config_file.close()

    # Make sure that the metadata section is configure correctly
    metadata = config.metadata
    mqtt = config.mqtt

    if metadata["enabled"] != "yes":
        raise MetadataNotEnabledError("Please set the `enabled` flag inside the `metadata` section to `yes`.")

    # Make sure that at least one of the metadata provider is configured
    has_pipe = metadata.get("pipe_name", "") != ""
    has_udp = metadata.get("socket_address", "") != "" \
              and metadata.get("socket_port", 0) > 0
    has_mqtt = mqtt.get("enabled", "no") == "yes" \
               and mqtt.get("hostname", "") != "" \
               and mqtt.get("port", 0) != 0 \
               and mqtt.get("publish_raw", "no") == "yes"

    # For some reason the mqtt port is a string and not and integer
    mqtt["port"] = int(mqtt["port"])

    # Are any of the backends available
    if not has_pipe and not has_udp and not has_mqtt:
        raise NoBackendAvailableError("Please configure at least one metadata backend.")

    # Create a listener instance according to the available backend
    if has_udp:
        return shairportmetadatareader.AirplayUDPListener(**metadata)
    if has_pipe:
        return shairportmetadatareader.AirplayPipeListener(**metadata)
    if has_mqtt:
        return shairportmetadatareader.AirplayMQTTListener(**mqtt)


def on_track_info(listener, info):
    """
    Print the current track information.
    :param listener: listener instance
    :param info: track information
    """
    print("Listener: ", listener, "received information: ", info)


# Listen for metadata changes for 60 seconds
listener = get_listener_for_config_file(DEFAULT_CONF_PATH)
listener.bind(track_info=on_track_info)
listener.start_listening()
time.sleep(60)
listener.stop_listening()