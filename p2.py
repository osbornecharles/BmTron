import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from client import *

media_files = "./mediafiles/"
COMMAND_PORT = 40128
CELL_SIZE = 20 

# DIRECTION
    # 0 is north
    # 1 is east
    # 2 is south
    # 3 is west

class Player2(pygame.sprite.Sprite):
    def __init__(self, gamespace):
        self.gs = gamespace
        self.name = "doge"
        self.image = pygame.image.load(media_files + "doge.png")
        self.rect = self.image.get_rect()
        self.x = self.gs.width * 3 /4
        self.y = self.gs.height / 2
        self.direction = 3 # heads west
        self.rect.move_ip(self.x, self.y) # start on right side
        self.copy = self.image

        self.gs.board.putOnBoard(self, self.x/CELL_SIZE, self.y/CELL_SIZE)

    def tick(self):
        pass
 
    def move(self, key_event):
        pass

class Player1(pygame.sprite.Sprite):
    def __init__(self, gamespace):
        self.gs = gamespace
        self.name = "gabe"
        self.image = pygame.image.load(media_files + "gabe.png")
        self.rect = self.image.get_rect()
        self.x = self.gs.width/4 
        self.y = self.gs.height/2
        self.direction = 1 # Heads east
        self.rect.move_ip(self.x, self.y) # start on left side
        self.copy = self.image
        
        self.gs.board.putOnBoard(self, self.x/CELL_SIZE, self.y/CELL_SIZE)

    def tick(self):
        '''Send location to other player'''
        # Retrieve data from host player about Player 1
        dataQueue = self.gs.data_connection.returnData()
        while (not dataQueue.empty()):
            data = dataQueue.get().split()

            # Host player died
            if (data[0] == "dead"):
                print("Client player wins!")

            # Host player changed size
            elif (data[0] == "size"):
                size = int(data[1])

            # Host player got item
            #elif (data[0] == "item"):
            #    item = data[1]

            # Host player changed direction
            elif (data[0] == "direction"):
                direction = int(data[1])

            # Host player changed speed
            elif (data[0] == "speed"):
                speed = int(data[1])

        # UPDATE Player 1 (host player) with received data

    def move(self):
        pass

class Mud(pygame.sprite.Sprite):
    def __init__(self, gamespace): 
        self.gs = gamespace
        self.name = "mud"
        self.image = pygame.image.load(media_files + "Poop_Emoji.png")

class Board():
    def __init__(self, gamespace):
        self.gs = gamespace
        self.board = []
        for y in range(int(self.gs.height / CELL_SIZE)):
            row = []
            for x in range(int(self.gs.width / CELL_SIZE)):
                row.append(0)
            self.board.append(row)

    def putOnBoard(self, thing, x, y):
        print("{} at x = {}, y = {}".format(thing.name, x,y))
        if (thing.name == "gabe"):
            self.board[y][x] = 1
        elif (thing.name == "doge"):
            self.board[y][x] = 2

    def deleteFromBoard(self, x, y):
        self.board[y][x] = 0

    def printBoard(self):
        for y in range(len(board)):
            for x in range(len(board[0])):
                print("| {} ".format(board[y][x]), end = '')
            print ("\n----------------------------")

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
        self.board = Board(self)
        self.p1 = Player1(self)
        self.p2 = Player2(self)

        # Draw players onto screen
        self.screen.blit(self.p1.image, self.p1.rect)
        self.screen.blit(self.p2.image, self.p2.rect)

        self.board.printBoard()

        # List to hold all other game objects
        #self.all_objects = [self.p1, self.p2]

        # Start game loop
        self.loop = LoopingCall(self.gameloop)
        self.loop.start(1/60)
        print("In game scene: started game loop")

    def gameloop(self):
        print("In game loop")
        #for event in pygame.event.get():
            #if event.type == pygame.KEYDOWN:
        
        for obj in self.all_objects:
            obj.tick()

        pygame.display.flip()
                

if __name__ == "__main__":
    # Instantiate CommandConnectionFactory 
    factory = CommandConnectionFactory()

    # Instantiate gamspace and call its menu function
    gs = GameSpace()
    gs.titleScene(factory)

    # Connect to host's command port and start the reactor for event driven system 
    reactor.connectTCP("ash.campus.nd.edu", COMMAND_PORT, factory)
    reactor.run()

