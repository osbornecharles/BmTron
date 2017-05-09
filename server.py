# Host player

from twisted.internet.protocol import Factory, ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.python import log
from queue import *
import sys
log.startLogging(sys.stdout)

COMMAND_PORT = 41148
DATA_PORT    = 42148


# ======================= CONNECTIONS =========================================
class CommandConnection(Protocol):
    '''Handles command connection between home.py and work.py'''
    def __init__(self, factory): 
        self.factory = factory
        self.sentStart = 0
        self.receivedStart = 0
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
    
    def start(self):
        return self.receivedStart and self.sentStart

class DataConnection(Protocol):
    '''Handles data connection between home.py and work.py'''
    def __init__(self, factory):
        self.factory = factory
        self.queue = Queue()

    def connectionMade(self):
        '''Upon establishing data connection, start forwarding what is in client connection's queue'''
        print("Data conection: Created connection between host and client players")

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
        beforestr = "direction " + str(direction) 
        self.transport.write(beforestr.encode())

    def sendCollision(self):
        self.transport.write("dead".encode())

    def sendSizeChange(self):
        self.transport.write("size".encode())


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
        #self.command_connection = factory.command_connection
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


