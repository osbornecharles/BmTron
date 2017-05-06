# Client player

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.python import log
import sys
log.startLogging(sys.stdout)

COMMAND_PORT = 40128
DATA_PORT = 42128

# ======================= CONNECTIONS =========================================
class CommandConnection(Protocol):
    '''Handles command connection between work.py and home.py'''
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print("Command connection: created from host player to client player")
    
    def dataReceived(self,data):
        '''Upon receiving command that home.py connected with client, create data connection'''
        print("Command connection: client player received data from host player: {}".format(data))
        if (data.decode() == "opened_dataport"):
            print("Command connection: client player connecting to host player's data port")
            # Create data connection
            reactor.connectTCP("ash.campus.nd.edu", DATA_PORT, DataConnectionFactory(self.factory))

class DataConnection(Protocol):
    '''Handles data connection between home.py and work.py'''
    def __init__(self, factory):
        self.factory = factory
        self.queue = DeferredQueue()

    def connectionMade(self):
        '''Upon establishing data connection, create service connection'''
        print("Data connection: created data connection between client player and host player")

    def dataReceived(self, data):
        '''Queue up data received from home.py while service connection is being established'''
        print("Data connection: received data from host player")
        self.queue.put(data)

    def startForward(self):
        '''Add a callback to deferred object waiting in the queue'''
        print("Data connection: start forwarding from client player to host player")
        self.queue.get().addCallback(self.forwardData)
    
    def forwardData(self, data):
        '''Write data from work.py to home.py by getting from queue and calling its callback function'''
        print("Data connection: forwarding data from client player to host player")
        self.queue.get().addCallback(self.forwardData)

# ==================== CONNECTION FACTORY =====================================
class CommandConnectionFactory(ClientFactory):
    '''Generates command connection'''
    def __init__(self):
        self.command_connection = CommandConnection(self)

    def getConnection(self):
        return self.command_connection

    def buildProtocol(self, addr):
        return self.command_connection

    def startedConnecting(self, connector): 
        print("Command connection factory: started connecting with connector: {}".format(connector))

class DataConnectionFactory(ClientFactory):
    '''Generates data connections'''
    def __init__(self, factory):
        self.command_connection = factory.command_connection
        self.data_connection = DataConnection(self)

    def buildProtocol(self, addr):
        return self.data_connection 
    
    def startedConnecting(self, connector): 
        print("Data connection factory: started connecting with connector: {}".format(connector))


'''
class ServiceConnectionFactory(ClientFactory): 
    def __init__(self, factory):
        self.command_connection = factory.command_connection
        self.data_connection = factory.data_connection
        self.service_connection = ServiceConnection(self)   
    
    def buildProtocol(self, addr):
        return self.service_connection
class ServiceConnection(Protocol):
    def __init__(self, factory): 
        self.factory = factory
        self.queue = DeferredQueue()

    def connectionMade(self):
        print "Service connection: created service connection from work.py to student01"
        self.factory.data_connection.startForward()
    
    def dataReceived(self,data):
        print "Service connection: work.py received data from student01"
        self.factory.data_connection.transport.write(data)

    def connectionLost(self, reason):
        print "Service connection: connection with service lost - {}".format(reason)
'''

