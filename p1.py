import pygame, sys
from twisted.internet import reactor
from server import *
from GameObjects import *

media_file_path = "./mediafiles/"
COMMAND_PORT = 41128
CELL_SIZE = 20
        
if __name__ == "__main__":
    gs = GameSpace()
    factory = CommandConnectionFactory()
    gs.titleScene(factory, "host")
    reactor.listenTCP(COMMAND_PORT, factory) 
    reactor.run()
