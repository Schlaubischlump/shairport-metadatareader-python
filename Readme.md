# Shairport-Metadatareader-Python
   
## What is this? 
This python (>= 2.7 or >= 3.4) library includes a package `shairportmetadatareader` which parses the airplay metadata from the 
[shairport-sync](https://github.com/mikebrady/shairport-sync) pipe, the specified shairport-sync udp server or the shairport-sync mqtt server.
In addition, it includes a `remote` sub-package to remotely control the Airplay client. 

## Requirements
- [enum34](https://pypi.org/project/enum34/) `pip install enum34` (Python 2 only)   
- [requests](http://www.python-requests.org/en/master/) `pip install requests`   
- [zeroconf](https://pypi.org/project/zeroconf/) `pip install zeroconf` (use version 0.19.1 or lower for python 2)   
- [kivy](https://kivy.org/) `pip install kivy` **or** [eventdispatcher](https://github.com/lobocv/eventdispatcher)
`pip install eventdispatcher`    

**optional:**
- [paho-mqtt](https://pypi.org/project/paho-mqtt/) `pip install paho-mqtt`  (if you want to use AirplayMQTTListener)    
- [libconf](https://pypi.org/project/libconf/) `pip install libconf` (if you want to use the [`libconf_init.py`](examples/libconf_init.py) example)    

## Installation
`pip install git+https://github.com/Schlaubischlump/shairport-metadatareader-python`

## Bugs
- I don't know. Let me know!   
...

## Example (Read Metadata)
```Python
from time import sleep
from shairportmetadatareader import AirplayUDPListener #, AirplayPipeListener

def on_track_info(lis, info):
    """
    Print the current track information.
    :param lis: listener instance
    :param info: track information
    """
    print(info)

listener = AirplayUDPListener() # You can use AirplayPipeListener or AirplayMQTTListener
listener.bind(track_info=on_track_info) # receive callbacks for metadata changes
listener.start_listening() # read the data asynchronously from the udp server
sleep(60) # receive data for 60 seconds
listener.stop_listening()
```

## Events
Beside the current track information you can listen for the following events in the same manner as in the above example:
- `connected`: True if a device is connected, otherwise false.
- `dacp_id`: Current DACP-ID of connected device.
- `active_remote`: Active remote token used to remote control the airplay device.
- `has_remote_data`: True if the dacp_id and active_remote token are available
- `client_name`: Name of the airplay client e.g John's iPhone.
- `playback_state`: The current playback state as string (play, pause, stop).
- `track_info`: Information about the currently playing track.
- `playback_progress`: List consisting of two elements: current playback position, duration
- `artwork`: Path to the artwork file of the current track stored in a temporary directory.
- `user_agent`: Airplay user agent. e.g. iTunes/12.2 (Macintosh; OS X 10.9.5)
- `airplay_volume`: Normalized volume between 0 and 1 send by the source (-1 for mute).
- `volume`: Playback volume as normalized float value between 0 and 1.
- `mute`: True if the airplay device is muted, otherwise False.    
- `item`: Received item from shairport-sync pipe or server. Use this if you need more fine-grained control to react to a specific ssnc or core code.
    
For more advanced examples take a look at the [examples folder](examples).

## Special thanks goes to
- luckydonald for his [shairport-decoder](https://github.com/luckydonald/shairport-decoder)   
- roblan for his [shairport-sync-reader](https://github.com/roblan/shairport-sync-reader)    
