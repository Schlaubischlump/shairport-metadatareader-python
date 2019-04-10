# Shairport-Metadatareader-Python
   
**What is this?**    
This python (>= 2.7 or >= 3.4) library includes a package `shairportmetadatareader` which parses the airplay metadata from the 
shairport-sync pipe or the specified shairport-sync udp server.
In addition, it includes a `remote` sub-package to remotely control the Airplay client. 

**Requirements**    
- [enum34](https://pypi.org/project/enum34/) `pip install enum34` (Python 2 only)   
- [requests](http://www.python-requests.org/en/master/) `pip install requests`   
- [zeroconf](https://pypi.org/project/zeroconf/) `pip install zeroconf` (use version 0.19.1 or lower for python 2)   
- [kivy](https://kivy.org/) `pip install kivy` **or** [eventdispatcher](https://github.com/lobocv/eventdispatcher)
`pip install eventdispatcher`    
- [paho-mqtt](https://pypi.org/project/paho-mqtt/) `pip install paho-mqtt`  (if you want to use AirplayMQTTListener)  

## Installation
`pip install git+https://github.com/Schlaubischlump/shairport-metadatareader-python`

## Bugs:
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
For more advanced examples take a look at the examples folder.

**Special thanks goes to**   
- luckydonald for his [shairport-decoder](https://github.com/luckydonald/shairport-decoder)   
- roblan for his [shairport-sync-reader](https://github.com/roblan/shairport-sync-reader)    
