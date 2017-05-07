import pygame, sys
from twisted.internet import reactor
from client import *
from GameObjects import * 

COMMAND_PORT = 40128

# DIRECTION
    # 0 is north
    # 1 is east
    # 2 is south
    # 3 is west

if __name__ == "__main__":
    # Instantiate CommandConnectionFactory 
    factory = CommandConnectionFactory()

    # Instantiate gamspace and call its menu function
    gs = GameSpace()
    gs.titleScene(factory, "client")

    # Connect to host's command port and start the reactor for event driven system 
    reactor.connectTCP("ash.campus.nd.edu", COMMAND_PORT, factory)
    reactor.run()
