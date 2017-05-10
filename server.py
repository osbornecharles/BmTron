# Host player

from twisted.internet.protocol import Factory, ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.python import log
from queue import *
import sys
import json
log.startLogging(sys.stdout)

COMMAND_PORT = 40440
DATA_PORT    = 40441


# ======================= CONNECTIONS =========================================
class CommandConnection(Protocol):
    '''Handles command connection between home.py and work.py'''
    def __init__(self, factory): 
        self.factory = factory
        self.sentStart = 0
        self.receivedStart = 0
        self.sentGo = False
        self.receivedGo = False
        self.ready = False

    def connectionMade(self):
        print("Command connection: created between host and client players")
        # Listen for client port
        print("Command connection: beginning to listen on DATA_PORT {} for data".format(DATA_PORT))
        reactor.listenTCP(DATA_PORT, DataConnectionFactory(self.factory)) 
        # Tell client player that the host player is listening on data port
        self.transport.write("opened_dataport".encode())

    def sendStart(self):
        print("Command connection: sent start to client")
        self.transport.write("Start pressed".encode())
        self.sentStart = 1
    
    def sendGo(self):
        print("Command connection: sent go to client player")
        self.transport.write("Go".encode())
        self.sentGo = True

    def sendEnd(self):
        print("Command connection: sent end to client")
        self.transport.write("Host quit".encode())

    def dataReceived(self, data):
        print('got data', data.decode())
        if(data.decode() == 'Start pressed'):
            self.receivedStart = 1
        elif (data.decode() == "Client quit"):
            print("Command connection: client player quit")
        elif (data.decode() == "Connections established"):
            self.ready = True
        elif (data.decode() == "Go"):
            print("Command connection: client player sent go")
            self.receivedGo = True
    
    def start(self):
        return self.receivedStart and self.sentStart
    
    def go(self):
        return self.receivedGo and self.sentGo

class DataConnection(Protocol):
    '''Handles data connection between home.py and work.py'''
    def __init__(self, factory):
        self.factory = factory
        self.queue = Queue()

    def connectionMade(self):
        '''Upon establishing data connection, start forwarding what is in client connection's queue'''
        print("Data conection: Created connection between host and client players")
        self.factory.command_connection.transport.write("Connections established".encode())

    def dataReceived(self, data):
        '''Use client conection to forward data from work.py to client'''
        print("Data connection: Received data from client player", data.decode())
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
        data = {"state": "dead"}
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


# ======================= CONNECTION FACTORY ==================================
class CommandConnectionFactory(ServerFactory):
    '''Generates command connection'''
    def __init__(self):
        self.command_connection = CommandConnection(self)
        self.data_connection = ""

    def buildProtocol(self, addr):
        return self.command_connection

    def startedConnecting(self, connector):
        print("Command connection factory: Started connecting with client player: {}".format(connector))

    def clientConnectionLost(self, connector, reason):
        print('Command connection factory: Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Command connection factory: Connection failed. Reason:', reason)


class DataConnectionFactory(ServerFactory):
    '''Generates data connection'''
    def __init__(self, factory):
        self.command_connection = factory.command_connection
        self.data_connection = DataConnection(self)
        factory.data_connection = self.data_connection

    def buildProtocol(self, addr):
        return self.data_connection

    def startedConnecting(self, connector):
        print("Data connection factory: Started connecting with client player: {}".format(connector))

    def clientConnectionLost(self, connector, reason):
        print('Data connection factory: Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Data connection factory: Connection failed. Reason:', reason)


