import pygame, sys
from twisted.internet import reactor
from client import *
from GameObjects import * 

COMMAND_PORT = 40440
SERVER = "ash.campus.nd.edu"

if __name__ == "__main__":
    # Instantiate CommandConnectionFactory 
    factory = CommandConnectionFactory()

    # Instantiate gamspace and call its menu function
    gs = GameSpace()
    gs.loadScene(factory, "client")

    # Connect to host's command port and start the reactor for event driven system 
    reactor.connectTCP(SERVER, COMMAND_PORT, factory)
    reactor.run()
