"""
simple_print Example
====================================================
This example demonstrates a simple use of the AirplayListener and AirplayRemote.
The current track information will be printed on the commandline.
The airplay client can be controlled by entering the numbers which correspond to a command.
"""

# pylint: disable=C0103

# import logging
# show all warnings and info
# logging.basicConfig(level=logging.DEBUG)

from time import sleep
from shairportmetadatareader.util import IS_PY2
from shairportmetadatareader import AirplayCommand, AirplayUDPListener #, AirplayMQTTListener, AirplayPipeListener

# python2 support
if IS_PY2:
    # pylint: disable=W0622, C0103, E0602
    input = raw_input

# list of all possible commands
allowed_cmds = [cmd.value for cmd in AirplayCommand]


def on_track_info(lis, info):
    """
    Print the current track information.
    :param lis: listener instance
    :param info: track information
    """
    print("Listener: ", lis, "received info: ", info)


# listen for track information changes using shairport-syncs udp port
listener = AirplayUDPListener()
listener.bind(track_info=on_track_info)
listener.start_listening()

# wait till all data to create an airplay remote is available
while not listener.has_remote_data:
    sleep(1)

# get an airplay remote instance ... this might take some time
print("Waiting for active connection...")
remote = listener.get_remote()
if not remote:
    exit(-1)
print("Connected to device: {0}".format(remote.hostname))

# show the user a list with available commands
print("Available commands:")
for i, cmd in enumerate(allowed_cmds, 1):
    print("{0}.\t{1}".format(i, cmd))

# read and process the user input
while True:
    cmd = input("Enter command number: ").strip()

    # stop user input
    if cmd == "exit":
        listener.stop_listening()
        break

    # send command
    try:
        cmd = int(cmd)
        if not 1 <= cmd <= len(allowed_cmds):
            print("Illegal command: {0}".format(cmd))
        else:
            # you should catch exceptions thrown by this function, in case the remote connection is lost
            remote.send_command(allowed_cmds[cmd-1])
    except Exception: # pylint: disable=W0703
        print("Illegal command: {0}".format(cmd))
