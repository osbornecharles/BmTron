import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from server import *
from GameObjects import *

media_file_path = "./mediafiles/"
COMMAND_PORT = 40128
CELL_SIZE = 20
        
if __name__ == "__main__":
    gs = GameSpace()
    factory = CommandConnectionFactory()
    gs.titleScene(factory, "host")
    reactor.listenTCP(COMMAND_PORT, factory) 
    reactor.run()

