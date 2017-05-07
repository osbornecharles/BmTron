import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from server import *
from GameObjects import *

media_file_path = "./mediafiles/"
COMMAND_PORT = 40128
CELL_SIZE = 20

class GameSpace:
    def main(self, factory, who): 
        # Step 1: Initialize the game space
        pygame.init()
        self.who = who # host or client player
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

        self.board = [] 
        for i in range(int(self.width/CELL_SIZE)):
            row = []
            for x in range(int(self.width/CELL_SIZE)):
                row.append(x)
            self.board.append(row)

        self.player1 = Player()
        self.player2 = Player()
        # Step 2: Initialize the game objects and place into an array
        #self.clock = pygame.time.Clock()

        self.loop = LoopingCall(gs.titleloop, (factory))
        self.loop.start(1/60)

    def titleloop(self, factory):
        if not factory.command_connection.start():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE):
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.startButton.collidepoint(mouse_pos):
                        factory.command_connection.sendStart()

            self.screen.blit(self.startText, self.textRect)
            self.screen.blit(self.title, self.titleRect)
            pygame.display.flip()
        else:
            self.loop.stop()
            self.screen.fill(self.black)
            pygame.display.flip()
            lc = LoopingCall(gs.gameloop, (factory))
            lc.start(1/60)

    def gameloop(self, factory):
        pass
        
if __name__ == "__main__":
    gs = GameSpace()
    factory = CommandConnectionFactory()
    gs.main(factory, "host")
    reactor.listenTCP(COMMAND_PORT, factory) 
    reactor.run()

