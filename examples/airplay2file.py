"""
airplay2file example
====================================================
This examples shows how to automatically save an airplay stream including the current metadata to an m4a file
when the current track changes. This method is neither intended nor suitable for reliably saving audio files.
Sometimes frames are lost, sometimes the network is too slow leading to parts of the song being silent. The audio
files volume depends on the airplay device volume. Shairport-syncs output is piped to a file, therefore you will
not hear any sound while this program is running.

Do not use this tool for piracy!
"""
import os
import sys
import wave
import logging
import subprocess
from time import sleep
import audiotools


# pylint: disable=C0103, C0413, W0603, E0601, W0613, W0702

# Pipe all the logs to a file
# Note: do this before importing shairportmetadatareader
loggers = ["ShairportLogger", "AirplayListenerLogger", "AirplayServiceListenerLogger"]

fh = logging.FileHandler("airplay2file.log")
fh.setLevel(logging.DEBUG)

for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.addHandler(fh)

from shairportmetadatareader import AirplayUDPListener


def save_wave(data, filename, info=None):
    """
    Save the current pcm data to a m4a file.
    :param data: pcm data
    :param filename: output filename without file extension
    :param info: daap track information as dictionary
    """
    # convert the pcm stream to a wav file
    wave_file = filename+".wav"

    wf = wave.open(wave_file, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(44100)
    wf.writeframes(data)
    wf.close()

    # convert the wav file to m4a
    audio_file = audiotools.open(wave_file).convert(filename+".m4a", audiotools.M4AAudio)

    # remove the wav file
    if os.path.isfile(wave_file):
        os.remove(wave_file)

    # update the m4a metadata information
    if info:
        metadata = audiotools.MetaData(track_name=info["itemname"], album_name=info["songalbum"],
                                       artist_name=info["songartist"], track_number=1, track_total=1)
        audio_file.set_metadata(metadata)


def on_track_info(lis, info):
    """
    Callback when the track information changed.
    :param lis: listener instance
    :param info: current track information
    """
    global offset
    global last_file_info

    def get_file_name(info):
        """
        Create an output filename based on the track information.
        """
        if not info:
            return ""
        return "{0} - {1} - {2}".format(info["itemname"], info["songartist"], info["songalbum"])

    # get the filename for the current and last file info
    filename = get_file_name(info)
    last_file_name = get_file_name(last_file_info)

    # if the track changed
    if filename == last_file_name:
        return

    print("New track started: ", filename)

    if last_file_info:
        # get the data for the current track
        data = open(pipe_file+".pcm", "rb").read()

        # remove silence from the start of a track
        if skip_silence:
            while data[offset] == b"\x00":
                offset += 1

        data = data[offset:]

        # save the pcm data to a file
        print("Save track: ", last_file_name)
        try:
            save_wave(data, last_file_name, last_file_info)
            print("Finished saving track: ", last_file_name)
        except:
            print("Error saving track: ", last_file_name, file=sys.stderr)
        offset += len(data)

    last_file_info = info


if __name__ == "__main__":
    # last track information
    last_file_info = None
    # offset of the current file in the pipe data
    offset = 0
    # name of the pipe file
    pipe_file = "pipe"
    # skip the silence at the beginning of a track
    skip_silence = True

    # delete the pipe file
    if os.path.isfile(pipe_file):
        os.remove(pipe_file)

    # start shairport-sync
    subprocess.Popen("shairport-sync -o stdout > {0}.pcm".format(pipe_file), shell=True)

    # listen for track changes
    listener = AirplayUDPListener()
    listener.bind(track_info=on_track_info)
    listener.start_listening()

    # quit the program using a keyboard interrupt
    try:
        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit) as e:
        pass
    finally:
        listener.stop_listening()
