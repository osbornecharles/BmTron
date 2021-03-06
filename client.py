# Client player

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.python import log
from queue import *
import sys
import json
log.startLogging(sys.stdout)

COMMAND_PORT = 40440
DATA_PORT    = 40441
SERVER = "ash.campus.nd.edu"

# ======================= CONNECTIONS =========================================
class CommandConnection(Protocol):
    '''Handles command connection between client and host players'''
    def __init__(self, factory):
        self.factory = factory 
        self.sentStart = False
        self.receivedStart = False
        self.sentGo = False
        self.receivedGo = False
        self.ready = False

    def connectionMade(self):
        print("Command connection: created from host player to client player")

    def sendStart(self): 
        '''Send to host player that client player has pressed "start"'''
        print("Command connection: sent start to host")
        self.sentStart = True
        self.transport.write("Start pressed".encode())

    def sendGo(self):
        print("go is away")
        self.sentGo = True
        self.transport.write("Go".encode())

    def sendEnd(self):
        print("Command connection: sent end to host")
        self.transport.write("Client quit".encode())
    
    def dataReceived(self,data):
        '''Handle received data from host player'''
        print("Command connection: client player received data from host player: {}".format(data))
        # Host player is listening on its data port
        if (data.decode() == "opened_dataport"):
            print("Command connection: client player connecting to host player's data port")
            # Create data connection
            reactor.connectTCP(SERVER, DATA_PORT, DataConnectionFactory(self.factory))

        # Host player clicked "start"
        elif (data.decode() == "Start pressed"):
            print("Command connection: host player pressed start")
            self.receivedStart = True
        elif (data.decode() == "Host quit"):
            print("Command connection: host player quit")
        elif (data.decode() == "Go"):
            print("Command connection: host player sent go")
            self.receivedGo = True
        elif (data.decode() == "Connections established"):
            self.ready = True

    def start(self):
        '''Return true only if both the host and the client players clicked "start"'''
        return self.sentStart and self.receivedStart
    
    def go(self):
        return self.sentGo and self.receivedGo

class DataConnection(Protocol):
    '''Handles data connection between host and client players'''
    def __init__(self, factory):
        self.factory = factory
        self.queue = Queue()

    def connectionMade(self):
        '''Upon establishing data connection, create service connection'''
        print("Data connection: created data connection between client player and host player")
        self.factory.command_connection.transport.write("Connections established".encode())

    def dataReceived(self, data):
        '''Upon receiving data as a string, decode it and return as an array'''
        print("Data connection: received data from host player", data.decode())
        self.queue.put(data.decode())

    def returnData(self):
        myQueue = self.queue
        self.queue = Queue() # new queue for next round of data
        return myQueue

    def sendSpeed(self, speed):
        beforestr = "speed " + str(speed)
        self.transport.write(beforestr.encode())

    def sendDirection(self, direction):
        data = {"dir": direction}
        self.transport.write((json.dumps(data)).encode())

    def sendCollision(self):
        #self.transport.write("dead".encode())
        data = {}
        data["state"] = "dead"
        self.transport.write((json.dumps(data)).encode())

    def sendSizeChange(self):
        self.transport.write("size".encode())

    def sendData(self, x, y, direction, speed, dead):
        data = {}
        data["x"] = x
        data["y"] = y
        data["dir"] = direction
        data["speed"] = speed
        data["dead"] = dead
        self.transport.write((json.dumps(data)).encode())


# ==================== CONNECTION FACTORY =====================================
class CommandConnectionFactory(ClientFactory):
    '''Generates command connection'''
    def __init__(self):
        self.command_connection = CommandConnection(self)
        self.data_connection = ''

    def buildProtocol(self, addr):
        return self.command_connection

    def startedConnecting(self, connector): 
        print("Command connection factory: started connecting with connector: {}".format(connector))

class DataConnectionFactory(ClientFactory):
    '''Generates data connections'''
    def __init__(self, factory):
        self.command_connection = factory.command_connection
        self.data_connection = DataConnection(self)
        factory.data_connection = self.data_connection

    def buildProtocol(self, addr):
        return self.data_connection 
    
    def startedConnecting(self, connector): 
        print("Data connection factory: started connecting with connector: {}".format(connector))

