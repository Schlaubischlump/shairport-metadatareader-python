from .shairport import start_shairport_daemon, stop_shairport_daemon
from .airplaylistener import AirplayListener, DEFAULT_PIPE_FILE, DEFAULT_SOCKET
from .remote import AirplayRemote, AirplayCommand


import os

__all__ = ["AirplayListener", "AirplayRemote", "AirplayCommand", "DEFAULT_PIPE_FILE", "start_shairport_daemon",
           "stop_shairport_daemon"]


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
                   "and running with support for writing the metadata to the pipe.")
