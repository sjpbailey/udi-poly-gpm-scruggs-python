# GPM Meter

The purpose of this Simple Nodeserver is to display/report, GPM that comes from an Arduino UNO to a Raspberry Pi then passed to a socket server that displays GPM.
Adds your Arduino GPM Meter in the Administrative Console instead of just in the Event Viewer.
Requires additional programs:
talktoarduino.py loaded on your RPI
flow_GPM.ino sketch loaded on your Arduino

* Supported Nodes
* GPM Actual

## Configuration

### Defaults

* "ip": "0.0.0.0"

#### User Provided

* Enter your IP Address
* Save and restart the NodeServer
