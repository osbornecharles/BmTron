import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from server import *

media_file_path = "./mediafiles/"

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

    def titleloop(self):
        global tl
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Escape key
                if (event.key == pygame.K_ESCAPE):
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.startButton.collidepoint(mouse_pos):
                    lc = LoopingCall(gs.loop)
                    lc.start(1/60)
                    tl.stop()

        self.screen.blit(self.startText, self.textRect)
        self.screen.blit(self.title, self.titleRect)
        pygame.display.flip()
                      

    def loop(self):
        '''Step 3: Start the game loop
        Step 4: Tick regulation set at 60 seconds'''
        print('hi')

        # Step 5: Read user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Escape key
                if (event.key == pygame.K_ESCAPE):
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

        # Step 6: Call tick() on each game object
        for obj in self.all_objects:
            obj.tick()

        # Step 7: Update screen
        self.screen.fill(self.black)
        for obj in reversed(self.all_objects):
            self.screen.blit(obj.image, obj.rect)
        pygame.display.flip()

gs = GameSpace()
t1 = LoopingCall(gs.titleloop)

if __name__ == "__main__":
    global tl
    global gs
    gs.main()

    # Step 3: Start the game loop using Twisted's Loopin Call
    tl.start(1/60)

    reactor.listenTCP(40091, DataConnectionFactory())
    reactor.run()

