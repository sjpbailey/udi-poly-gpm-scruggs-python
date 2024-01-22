

import udi_interface
import socket
import sys
import time

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
        
    def calPsi(self, command):
        # Calibration
        psi = float(command.get('value'))
        def set_psi(self, command):
            psi = float(command.get('value'))
        if psi < -100 or psi > 100:
            LOGGER.error('Invalid selection {}'.format(psi))
        else:
            self.setDriver('GV15', psi)
            LOGGER.info('Calibration = ' + str(psi/10) + 'INT')
        
            psi1 = self.getDriver('GV15')
            LOGGER.info("PSI Calibration From GV15")
            LOGGER.info(psi1)

    def discover(self, *args, **kwargs):        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind the socket to the port
        host, port =  self.ip, 10000
        server_address = (host, port)
        LOGGER.info(f'Starting UDP server on {host} port {port}')
        sock.bind(server_address)

        while True:
            # Wait for messages
            message, address = sock.recvfrom(4096)
            message = message.decode('utf-8')
            dataArray=message.split(' , ')
            # Inputs from Simple Socket Server
            self.setDriver('GV1', dataArray[0]) # GPM
            self.setDriver('GV2', dataArray[1]) # GPM Total
            self.setDriver('GV3', dataArray[2]) # PSI
            self.setDriver('GV4', dataArray[3]) # Low Level
            self.setDriver('GV5', dataArray[4]) # High Level
            self.setDriver('GV6', dataArray[5]) # pH
            self.setDriver('GV7', dataArray[6]) # orp
            self.setDriver('GV8', dataArray[7]) # Temperature1
            self.setDriver('GV9', dataArray[8]) # Temperature2
            self.setDriver('GV10', dataArray[9]) # Temperature3
            
            # Online and Reading GPM
            if dataArray[0] == 0:
                time.sleep(10)
                self.setDriver('ST', 0)
            if dataArray[0] != 0:
                self.setDriver('ST', 1)
            
            """# PSI input to Float
            psiin = dataArray[2]
            LOGGER.info("PSI input from Socket Server")
            LOGGER.info(float(str(psiin)))            
            self.setDriver('GV3', float(psiin)) # PSI Driver
            
            # Calibration input from AC
            psist = self.getDriver('GV15') # Calibration Input
            LOGGER.info("Calibration Set Point")
            LOGGER.info(psist) 

            # Calibration added to PSI
            if float(psiin) == 0:
                psitotal = float(psist)
            else:
                psitotal = float(psist) - float(str(psiin))
                LOGGER.info("Subtracted Calibration and PSI Output to GV3")
                LOGGER.info(psitotal)
                self.setDriver('GV16', float(psitotal)) # PSI Driver"""

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
        'CALGO': calPsi,
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
        {'driver': 'GV8', 'value': 0, 'uom': 17, 'name': "Temperature1"},
        {'driver': 'GV9', 'value': 0, 'uom': 17, 'name': "Temperature2"},
        {'driver': 'GV10', 'value': 0, 'uom': 17, 'name': "Temperature3"},
        #{'driver': 'GV15', 'value': 0, 'uom': 70, 'name': "Calibration SETP"},
        #{'driver': 'GV16', 'value': 0, 'uom': 52, 'name': "Calibrated PSI"},
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
    