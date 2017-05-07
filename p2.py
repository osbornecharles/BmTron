import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from client import *

media_files = "./mediafiles/"
COMMAND_PORT = 40128

class GameSpace:
    def titleScene(self, factory): 
        '''Title scene with start button'''
        # Save factory
        self.factory = factory

        # Initialize the game space
        pygame.init()
        self.size = self.width, self.height = 640, 420
        self.black = 0,0,0
        self.screen = pygame.display.set_mode(self.size)
        pygame.key.set_repeat(10, 30)

        # Menu's game title text
        font = pygame.font.Font(None, 20)
        self.startText = font.render('Start', 0, (30, 120, 50))
        bigfont = pygame.font.Font(None, 40)
        self.title = bigfont.render('Game', 0, (250, 250, 250))

        # Menu's start button 
        self.startButton = pygame.Rect(0, 0, 100, 40)
        self.startButton.topleft = (self.width/2 - self.startButton.width/2, self.height/2)
        self.textRect = self.startText.get_rect()
        self.textRect.topleft = (self.width/2 - self.textRect.width/2, self.height/2 + 10)
        self.titleRect = self.title.get_rect()
        self.titleRect.topleft = (self.width/2 - self.titleRect.width/2, 10)
        pygame.draw.rect(self.screen, (30, 120, 50), self.startButton, 1)

        # Draw title and startText to screen
        self.screen.blit(self.startText, self.textRect)
        self.screen.blit(self.title, self.titleRect)
        pygame.display.flip()

        # Start game loop
        self.loop = LoopingCall(self.titleloop)
        self.loop.start(1/60)

    def titleloop(self):
        # Stay at title scene if both players have not selected start
        if (not self.factory.command_connection.start()):
            for event in pygame.event.get():
                # Close pygame
                if event.type == pygame.QUIT:
                    reactor.stop()
                # Key detection
                elif event.type == pygame.KEYDOWN:
                    # Escape key to end pygame
                    if (event.key == pygame.K_ESCAPE):
                        reactor.stop()
                # Mouse detection
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # User clicked start
                    if self.startButton.collidepoint(mouse_pos):
                        self.factory.command_connection.sendStart()
            self.screen.blit(self.startText, self.textRect)
            self.screen.blit(self.title, self.titleRect)
            pygame.display.flip()
        # Transition to game scene
        else:
            print("hello")
            self.screen.fill(self.black)
            pygame.display.flip()
            # Stop title loop and go to game scene
            self.loop.stop()
            self.gameScene()

    def gameScene(self):
        # Set up game objects

        # List to hold all other game objects
        self.all_objects = []

        # Start game loop
        self.loop = LoopingCall(self.gameloop)
        self.loop.start(1/60)
        print("In game scene: started game loop")

    def gameloop(self):
        print("In game loop")
        pass
                      

if __name__ == "__main__":
    # Instantiate CommandConnectionFactory 
    factory = CommandConnectionFactory()

    # Instantiate gamspace and call its menu function
    gs = GameSpace()
    gs.titleScene(factory)

    # Connect to host's command port and start the reactor for event driven system 
    reactor.connectTCP("ash.campus.nd.edu", COMMAND_PORT, factory)
    reactor.run()

