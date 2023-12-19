#!/usr/bin/env python3
"""
Polyglot v3 node server Example 1
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import time
import xml.etree.ElementTree as ET

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
ISY = udi_interface.ISY
polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''
class AmiNemNode(udi_interface.Node):
    id = 'test'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            #{'driver': 'GV0', 'value': 0, 'uom': 56},
            #{'driver': 'GV1', 'value': 0, 'uom': 56},
            {'driver': 'GPV', 'value': 0, 'uom': 2},
            {'driver': 'CC', 'value': 0, 'uom': 30},
            {'driver': 'GV1', 'value': 0, 'uom': 73},
            {'driver': 'TPW', 'value': 0, 'uom': 33},
            {'driver': 'GV2', 'value': 0, 'uom': 33},
            {'driver': 'GV3', 'value': 0, 'uom': 33},
            ]

    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}

'''
node_queue() and wait_for_node_event() create a simple way to wait
for a node to be created.  The nodeAdd() API call is asynchronous and
will return before the node is fully created. Using this, we can wait
until it is fully created before we try to use it.
'''
def node_queue(data):
    n_queue.append(data['address'])

def wait_for_node_event():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()

'''
Read the user entered custom parameters. In this case, it is just
the 'multiplier' value.  Save the parameters in the global 'Parameters'
'''
def parameterHandler(params):
    global Parameters

    Parameters.load(params)


'''
This is where the real work happens.  When we get a shortPoll, increment the
count, report the current count in GV0 and the current count multiplied by
the user defined value in GV1. Then display a notice on the dashboard.
'''
def poll(polltype):
    global count
    global Parameters
    self.isy = ISY()

    if 'shortPoll' in polltype:
        if Parameters['multiplier'] is not None:
            mult = int(Parameters['multiplier'])
        else:
            mult = 1

        node = polyglot.getNode('my_address')
        #if node is not None:
        #    count += 1

        #    node.setDriver('GV0', count, True, True)
        #    node.setDriver('GV1', (count * mult), True, True)

            # be fancy and display a notice on the polyglot dashboard
        #    polyglot.Notices['count'] = 'Current count is {}'.format(count)
        
        amiem_resp = node.isy.cmd("/rest/emeter")
        amiem_count = 0
        amiem_count1 = 0
        ustdy_count = 0
        prevs_count = 0
        sumss_count = 0
        
        
    if amiem_resp is not None:
        amiem_root = ET.fromstring(amiem_resp)

        #amiem_count = float(amiem_root('instantaneousDemand'))
        for amie in amiem_root.iter('instantaneousDemand'):
            amiem_count = float(amie.text) 
            LOGGER.info("kW: " + str(amiem_count/float(mult)))
            node.setDriver('CC', amiem_count/float(mult))

            amiem_count1 = float(amiem_root.iter('instantaneousDemand'))
            LOGGER.info("WATTS: " + str(amiem_count1))
            node.setDriver('GV1', amiem_count1/float(mult)*1000)
            
            ustdy_count = float(amiem_root.iter('currDayDelivered'))
            LOGGER.info("kWh: " + str(ustdy_count))
            node.setDriver('TPW', ustdy_count/float(mult))
            
            prevs_count = float(amiem_root.iter('previousDayDelivered'))
            LOGGER.info("kWh: " + str(prevs_count))
            node.setDriver('GV2', prevs_count/float(mult))
            
            sumss_count = float(amiem_root.iter('currSumDelivered'))  #.text
            LOGGER.info("kWh: " + str(sumss_count))
            node.setDriver('GV3', sumss_count/float(mult))        


'''
When we are told to stop, we update the node's status to False.  Since
we don't have a 'controller', we have to do this ourselves.
'''
def stop():
    nodes = polyglot.getNodes()
    for n in nodes:
        nodes[n].setDriver('ST', 0, True, True)
    polyglot.stop()

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
        polyglot.subscribe(polyglot.STOP, stop)
        polyglot.subscribe(polyglot.POLL, poll)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        '''
        Here we create the device node.  In a real node server we may
        want to try and discover the device or devices and create nodes
        based on what we find.  Here, we simply create our node and wait
        for the add to complete.
        '''
        node = AmiNemNode(polyglot, 'my_address', 'my_address', 'Counter')
        polyglot.addNode(node)
        wait_for_node_event()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

