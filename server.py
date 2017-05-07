# Hosr player

from twisted.internet.protocol import Factory, ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.defer import DeferredQueue
import sys
log.startLogging(sys.stdout)

COMMAND_PORT = 40128
DATA_PORT = 42128


# ======================= CONNECTIONS =========================================
class CommandConnection(Protocol):
    '''Handles command connection between home.py and work.py'''
    def __init__(self, factory): 
        self.factory = factory
        self.sentStart = 0
        self.receivedStart = 0

    def connectionMade(self):
        print("Command connection: created between host and client players")
        # Listen for client port
        print("Command connection: beginning to listen on DATA_PORT {} for data".format(DATA_PORT))
        reactor.listenTCP(DATA_PORT, DataConnectionFactory(self.factory)) 
        # Tell client player that the host player is listening on data port
        self.transport.write("opened_dataport".encode())

    def sendStart(self):
        self.transport.write("Start pressed".encode())
        self.sentStart = 1

    def dataReceived(self, data):
        print('got data', data.decode())
        if(data.decode() == 'Start pressed'):
            self.receivedStart = 1
    
    def start(self):
        return self.receivedStart and self.sentStart

class DataConnection(Protocol):
    '''Handles data connection between home.py and work.py'''
    def __init__(self, factory):
        self.datafactory = factory

    def connectionMade(self):
        '''Upon establishing data connection, start forwarding what is in client connection's queue'''
        print("Data conection: Created connection between host and client players")

    def dataReceived(self, data):
        '''Use client conection to forward data from work.py to client'''
        print("Data connection: Received data from client player")


# ======================= CONNECTION FACTORY ==================================
class CommandConnectionFactory(ServerFactory):
    '''Generates command connection'''
    def __init__(self):
        self.command_connection = CommandConnection(self)

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

    def buildProtocol(self, addr):
        return self.data_connection
    def startedConnecting(self, connector):
        print("Data connection factory: Started connecting with client player: {}".format(connector))

    def clientConnectionLost(self, connector, reason):
        print('Data connection factory: Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Data connection factory: Connection failed. Reason:', reason)


# ================= MAIN EXECUTION =========================
#if __name__ == "__main__":
    # Establish connection with client player
#    reactor.listenTCP(COMMAND_PORT, CommandConnectionFactory())
#    reactor.run()

'''

class DataConnection(Protocol):
    def __init__(self):
        pass
        
    def connectionMade(self):
        pass

    def dataReceived(self, data):
        pass

    def writeData(self, data):
        pass

class DataConnectionFactory(ServerFactory):
    def __init__(self):
        self.dataConnection = DataConnection()

    def buildProtocol(self, addr):
        return self.dataConnection

    def startedConnecting(self, connector):
        print(connector)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)

class ClientConnection(Protocol): 
    def __init__(self, factory):
        self.factory = factory
        self.queue = DeferredQueue()

    def connectionMade(self):
        print("Client connection: created between client and home.py")
        self.factory = DataConnectionFactory(self.factory)
        reactor.listenTCP(DATA_PORT, self.factory)
        self.factory.command_connection.sendCommand()

    def dataReceived(self, data): 
        print("Client connection: received data from client")#.format(data)
        self.queue.put(data)

    def startForward(self):
        print("Client connection: start forwarding data to client")
        # Add a callback to the deferred object waiting in the queue
        self.queue.get().addCallback(self.forwardData)
    
    def forwardData(self, data):
        print("Client connection: forwarding data to client")
        # Forward data by sending the data to work.py
        self.factory.data_connection.transport.write(data)
        # Since there may be multiple things on queue, must add itself back onto the 
            # next deferred object
        self.queue.get().addCallback(self.forwardData)

    def connectionLost(self, reason):
        print("Client connection: connection with client lost - {}".format(reason))
'''

