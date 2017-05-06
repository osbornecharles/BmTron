from twisted.internet.protocol import Factory, ServerFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.defer import DeferredQueue
import sys
log.startLogging(sys.stdout)


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


