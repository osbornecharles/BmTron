import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from server import *

media_file_path = "./mediafiles/"
title = 1
COMMAND_PORT = 40128

class GameSpace:
    def main(self): 
        # Step 1: Initialize the game space
        pygame.init()
        self.size = self.width, self.height = 640, 420
        self.black = 0,0,0
        self.screen = pygame.display.set_mode(self.size)
        pygame.key.set_repeat(10, 30)

        font = pygame.font.Font(None, 20)
        self.startText = font.render('Start', 0, (30, 120, 50))
        bigfont = pygame.font.Font(None, 40)
        self.title = bigfont.render('Game', 0, (250, 250, 250))


        self.startButton = pygame.Rect(0, 0, 100, 40)
        self.startButton.topleft = (self.width/2 - self.startButton.width/2, self.height/2)
        self.textRect = self.startText.get_rect()
        self.textRect.topleft = (self.width/2 - self.textRect.width/2, self.height/2 + 10)
        self.titleRect = self.title.get_rect()
        self.titleRect.topleft = (self.width/2 - self.titleRect.width/2, 10)
        pygame.draw.rect(self.screen, (30, 120, 50), self.startButton, 1)
        self.screen.blit(self.startText, self.textRect)
        self.screen.blit(self.title, self.titleRect)
        pygame.display.flip()


        # Step 2: Initialize the game objects and place into an array
        #self.clock = pygame.time.Clock()

        self.all_objects = []

    def titleloop(self, factory):
        global title
        if title:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE):
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.startButton.collidepoint(mouse_pos):
                        title = 0
                        factory.command_connection.transport.write('start pressed'.encode())

            self.screen.blit(self.startText, self.textRect)
            self.screen.blit(self.title, self.titleRect)
            pygame.display.flip()
        else:
            print("hello")
            self.screen.fill(self.black)
            pygame.display.flip()
                      

if __name__ == "__main__":
    gs = GameSpace()
    gs.main()
    factory = CommandConnectionFactory()
    reactor.listenTCP(COMMAND_PORT, factory)
    tl = LoopingCall(gs.titleloop, (factory))
    tl.start(1/60)
    reactor.run()

