import pygame, sys
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from client import *
from GameObjects import * 

media_files = "./mediafiles/"
COMMAND_PORT = 41128
CELL_SIZE = 20 
SERVER = "newt.campus.nd.edu"

if __name__ == "__main__":
    # Instantiate CommandConnectionFactory 
    factory = CommandConnectionFactory()

    # Instantiate gamspace and call its menu function
    gs = GameSpace()
    gs.titleScene(factory, "client")

    # Connect to host's command port and start the reactor for event driven system 
    reactor.connectTCP(SERVER, COMMAND_PORT, factory)
    reactor.run()
