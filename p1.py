import pygame, sys
from twisted.internet import reactor
from server import *
from GameObjects import *

COMMAND_PORT = 40128
        
if __name__ == "__main__":
    gs = GameSpace()
    factory = CommandConnectionFactory()
    gs.titleScene(factory, "host")
    reactor.listenTCP(COMMAND_PORT, factory) 
    reactor.run()

