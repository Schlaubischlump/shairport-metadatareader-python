# Shairport-Metadatareader-Python
   
**What is this?**   
This package is inspired by [luckydonald's shairport-decoder project](https://github.com/luckydonald/shairport-decoder/).   
 
It includes a library which reads the airplay metadata from the shairport-sync pipe. In addition, it includes a `remote` sub-package to remotely control the Airplay client. 

**Requirements**    
- [zeroconf](https://pypi.org/project/zeroconf/) `pip install zeroconf` (use Version 0.19.1 or lower for python 2)   
- [kivy](https://kivy.org/) `pip install kivy` **or** [eventdispatcher](https://github.com/lobocv/eventdispatcher) `pip install eventdispatcher`    


## Bugs:
- I don't know. Let me know!   
...

## Todo:
- Does the remote control work if the airplay server is password protected?

## Example (Read Metadata)
```
from time import sleep
from shairportmetadatareader import AirplayListener

def on_track_info(lis, info):
    """
    Print the current track information.
    :param lis: listener instance
    :param info: track information
    """
    print(info)

listener = AirplayListener()
listener.start_listening() # this method is none blocking
listener.bind(track_info=on_track_info) # receive callbacks for metadata
sleep(60) # receive data for 60 seconds
listener.stop_listening()
```
For more examples take a look at the main.py.