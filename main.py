import sys
import logging
from shairportmetadatareader import AirplayListener, AirplayCommand

# disable logging for input
logging.basicConfig(level=logging.INFO)

# python2 support
input = raw_input if sys.version_info.major <= 2 else input

# list of all possible commands
allowed_cmds = [cmd.value for cmd in AirplayCommand]


def on_track_info(lis, info):
    """
    Print the current track information.
    :param lis: listener instance
    :param info: track information
    """
    print(info)


listener = AirplayListener()
listener.start_listening() # this method is not blocking
listener.bind(track_info=on_track_info)

# wait until the airplay listener is connected
while not listener.connected:
    pass

# get an airplay remote instance ... this might take some time
print("Waiting for active connection...")
remote = listener.get_remote()
print("Connected to device: {0}".format(remote.hostname))
print("Available commands:")
for i, cmd in enumerate(allowed_cmds, 1):
    print("{0}.\t{1}".format(i, cmd))

while True:
    cmd = input("Enter command number: ").strip()
    if cmd == "exit":
        listener.stop_listening()
        break

    # send command
    try:
        cmd = int(cmd)
        if not (1 <= cmd <= len(allowed_cmds)):
            print("Illegal command: {0}".format(cmd))
        else:
            remote.send_command(allowed_cmds[cmd-1])
    except Exception:
        print("Illegal command: {0}".format(cmd))
