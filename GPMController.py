

import udi_interface
import socket
from struct import unpack
import sys
import time
#import urllib3
#import requests
import xml.etree.ElementTree as ET

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER
Custom = udi_interface.Custom


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
        self.speed = None

    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()    

    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()
        self.discover()

    def discover(self, *args, **kwargs):        
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        host, port =  self.ip, 10000
        server_address = (host, port)

        print(f'Starting UDP server on {host} port {port}')
        sock.bind(server_address)

        while True:
            # Wait for message
            message, address = sock.recvfrom(4096)
            message = message.decode('utf-8')
            dataArray=message.split(' , ')
            self.setDriver('GV1', dataArray[0]) # GPM
            self.setDriver('GV2', dataArray[1]) # GPM Total
            self.setDriver('GV3', dataArray[2]) # PSI
            self.setDriver('GV4', dataArray[3]) # Low Level
            self.setDriver('GV5', dataArray[4]) # High Level
            self.setDriver('GV6', dataArray[5]) # pH
            self.setDriver('GV7', dataArray[6]) # orp
            self.setDriver('GV8', dataArray[7]) # Temperature
            
            # Online and Reading GPM
            if dataArray[0] == 0:
                time.sleep(10)
                self.setDriver('ST', 0)
            if dataArray[0] != 0:
                self.setDriver('ST', 1)
                
            # Calibration
    def calValue(self, command):
        output_ao1 = 'speed'
        speed = float(command.get('value'))

        def set_speed(self, command):
            speed = float(command.get('value'))
        if speed < -100 or speed > 110:
            LOGGER.error('Invalid selection {}'.format(speed))
        else:
            self.setDriver('GV9', speed/10)
            LOGGER.info('Calibration = ' + str(speed/10) + 'INT')
            res = 'GV9'
        self.speed = speed/10
        LOGGER.info("SPEED")
        LOGGER.info(self.speed)
        speed1 = 'GV3'
        
        self.setDriver('GV10', speed1 + speed)
        return self.speed
        
        """for i in res:    #res = [int(i) for i in 'GV9'.split() if i.isdigit()]    
            LOGGER.info(i)#'Calibration = ' + str(speed) + 'INT')
            LOGGER.info('GV9')"""
        

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

    def query(self, command=None):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def poll(self, flag):
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()
            #self.discover()
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
        'CALGO': calValue,
    }
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2, 'name': "Online"},
        {'driver': 'GV1', 'value': 0, 'uom': 69, 'name': "GPM"},
        {'driver': 'GV2', 'value': 0, 'uom': 69, 'name': "GPM Total"},
        {'driver': 'GV3', 'value': 0, 'uom': 52, 'name': "PSI"},
        {'driver': 'GV4', 'value': 0, 'uom': 25, 'name': "Level Low"},
        {'driver': 'GV5', 'value': 0, 'uom': 25, 'name': "Level High"},
        {'driver': 'GV6', 'value': 0, 'uom': 56, 'name': "pH"},
        {'driver': 'GV7', 'value': 0, 'uom': 43, 'name': "ORP"},
        {'driver': 'GV8', 'value': 0, 'uom': 17, 'name': "Temperature"},
        {'driver': 'GV9', 'value': 0, 'uom': 70, 'name': "Calibration"},
        {'driver': 'GV10', 'value': 0, 'uom': 70, 'name': "New PSI?"},
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
    