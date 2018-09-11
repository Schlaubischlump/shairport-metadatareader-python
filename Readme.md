# Shairport-Metadatareader-Python
   
**What is this?**    
This python (>= 2.7 or >= 3.4) library includes a package `shairportmetadatareader` which parses the airplay metadata from the 
shairport-sync pipe or the specified shairport-sync udp server.
In addition, it includes a `remote` sub-package to remotely control the Airplay client. 

**Requirements**    
- [zeroconf](https://pypi.org/project/zeroconf/) `pip install zeroconf` (use version 0.19.1 or lower for python 2)   
- [kivy](https://kivy.org/) `pip install kivy` **or** [eventdispatcher](https://github.com/lobocv/eventdispatcher) 
`pip install eventdispatcher`    


## Bugs:
- I don't know. Let me know!   
...

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
listener.bind(track_info=on_track_info) # receive callbacks for metadata changes
listener.start_listening() # read the data asynchronously from the pipe
sleep(60) # receive data for 60 seconds
listener.stop_listening()
```
For a more advanced example take a look at the main.py.

**Special thanks goes to**   
- luckydonald for his [shairport-decoder](https://github.com/luckydonald/shairport-decoder)   
- roblan for his [shairport-sync-reader](https://github.com/roblan/shairport-sync-reader)    