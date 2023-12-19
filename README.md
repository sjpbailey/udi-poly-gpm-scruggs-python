
# GPM Meter

![NetEnergyMeter](https://github.com/sjpbailey/udi-poly-ami-nem-python-master/blob/master/Images/AMI_NEM_Poly_2.png)

The purpose of this Simple Nodeserver is to display/report, GPM that comes from an Arduino UNO to a Raspberry Pi then passed to a socket server that displays GPM.
Adds your Arduino GPM Meter in the Administrative Console instead of just in the Event Viewer.
Requires additional programs:
talktoarduino.py loaded on your RPI
flow_GPM.ino sketch loaded on your Arduino

* Supported Nodes
* GPM Actual

## Configuration

### Defaults

* Default Short Poll:  Every 5 minutes
* Default Long Poll: Every 10 minutes (heartbeat)
* nem_oncor: Input your Meter type, 1000 for Landis+Gyr, 10000 for Oncor Meters

#### User Provided

* ip: Your Client Computers IP Address
* Save and restart the NodeServer
