import atexit
import logging
import subprocess

logger = logging.getLogger("ShairportLogger")

# internal variable to indicate that shairport was started as daemon by this process
SHAIRPORT_RUNNING = False


def start_shairport_daemon(exec_path="shairport-sync"):
    """
    Start the shairport daemon if it is not already running.
    :param exec_path: path to the executable
    """
    # you can configure the remaining variables by changing the shairport-sync config file
    # maybe this should be changed to a local binary and a local config file
    ret = subprocess.Popen([exec_path, "-d"], stderr=subprocess.PIPE)
    ret.wait()

    if ret.returncode != 0:
        _, err = ret.communicate()
        logger.warning("Can not launch shairport-sync: {0}".format(err.decode("utf-8")))
    else:
        logger.info("Starting shairport-sync daemon.")
        global SHAIRPORT_RUNNING
        SHAIRPORT_RUNNING = True


def stop_shairport_daemon(exce_path="shairport-sync"):
    """
    Stop the shairport daemon if it is running.
    :param exec_path: path to the executable
    """
    global SHAIRPORT_RUNNING
    if not SHAIRPORT_RUNNING:
        return

    ret = subprocess.Popen([exce_path, "-k"], stderr=subprocess.PIPE)
    ret.wait()

    if ret.returncode != 0:
        _, err = ret.communicate()
        logger.warning("Can not stop shairport-sync: {0}".format(err.decode("utf-8")))
    else:
        logger.info("Stopping shairport-sync daemon.")
        SHAIRPORT_RUNNING = False


# if __del__ is not called, we should try to kill shairport when the program terminates
# if this fails, shairport should still be killed when it was started as daemon, but the cleanup of the pid file
# does not happen in this case
atexit.register(stop_shairport_daemon)