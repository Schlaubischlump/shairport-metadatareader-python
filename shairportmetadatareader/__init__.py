import os
import logging

logging.basicConfig()

from .shairport import start_shairport_daemon, stop_shairport_daemon
from .listener import AirplayPipeListener, AirplayUDPListener, DEFAULT_PIPE_FILE, DEFAULT_SOCKET
from .remote import AirplayRemote, AirplayCommand


__all__ = ["AirplayPipeListener", "AirplayUDPListener", "DEFAULT_PIPE_FILE", "DEFAULT_SOCKET",
           "start_shairport_daemon", "stop_shairport_daemon",  "AirplayRemote", "AirplayCommand"]

# Import mqtt backend if the necessary frameworks are available.
try:
    from .listener import AirplayMQTTListener, DEFAULT_BROKER
    __all__ += ["AirplayMQTTListener", DEFAULT_BROKER]
except:
    pass


def which(program):
    """
    # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    Determine the path of an executable.
    :param program: name of the executable
    :return: path to the executable
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


if not which("shairport-sync"):
    import logging
    logger = logging.getLogger("ShairportLogger")
    logger.warning("Can not find executable shairport-sync in your PATH. Make sure that shairport-sync is installed "
                   "and configured to support writing the metadata to the pipe or the UDP server.")
