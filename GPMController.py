

import udi_interface
import socket
from struct import unpack
import sys
import time
import urllib3
import requests
import xml.etree.ElementTree as ET

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER
Custom = udi_interface.Custom
ISY = udi_interface.ISY 

LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class GPMController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(GPMController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'GPM Controller'  # override what was passed in
        self.hb = 0
        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.ready()
        self.poly.addNode(self)
        # Attributes
        self.user = None
        self.password = None
        self.ip = None
        #self.nem_oncor = None
        self.isy = ISY(self.poly)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()    

    def start(self):
        #self.poly.updateProfile()
        self.discover()

    def discover(self, *args, **kwargs):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        host, port =  self.ip, 10000      #'192.168.1.18', 10000
        server_address = (host, port)

        print(f'Starting UDP server on {host} port {port}')
        sock.bind(server_address)

        while True:
            # Wait for message
            message, address = sock.recvfrom(4096)
            message = message.decode('utf-8')
            self.setDriver('GV1', message)
            LOGGER.info(message)

    def delete(self):
        LOGGER.info('Deleting GPM Meter')

    def stop(self):
        LOGGER.debug('GPM Plugin stopped.')

    def set_module_logs(self,level):
        LOGGER.getLogger('urllib3').setLevel(level)

    def check_params(self):
        self.Notices.clear()
        default_ip = "0.0.0.0"
        
        self.ip = self.Parameters.ip
        if self.ip is None:
            self.ip = default_ip
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(default_ip))
            self.ip = default_ip

        if self.ip == default_ip:
            self.Notices['auth'] = 'Please set proper ip address in configuration page'
            self.setDriver('ST', 0)
        else:
            self.setDriver('ST', 1)

    def query(self, command=None):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def poll(self, flag):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()
            self.discover()
        if 'longPoll' in flag:
            LOGGER.debug('longPoll (controller)')
        else:
            LOGGER.debug('shortPoll (controller)')
            

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.Notices))
        # Remove all existing notices
        self.Notices.clear()

    id = 'controller'
    
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'REMOVE_NOTICES_ALL': remove_notices_all,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV1', 'value': 0, 'uom': 69},
    ]

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([GPMController])
        polyglot.start()
        control = GPMController(polyglot, 'controller', 'controller', 'GPMController')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Exception: {0}'.format(err), exc_info=True)
    sys.exit(0)
    