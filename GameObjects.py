import pygame, sys
from twisted.internet.task import LoopingCall

mediafile = "./mediafiles/"

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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, name, gamespace):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.name = name
        self.dead = 0
        self.fat = 0
        self.slow = 0
        self.fast = 0
        self.powerUpTurns = 0
        self.currentDirection = 1
        self.gs = gamespace

    def get_array_pos(self):
        x = self.x / CELL_SIZE
        y = self.y / CELL_SIZE
        return (x, y)

    def updatePlayer(self, boardVal):
        self.powerUpTurns -= 1
        if self.powerUpTurns <= 0:
            self.powerUpTurns = 0
            self.fat = 0
            self.slow = 0
            self.fast = 0
        if boardVal == 1:
            self.dead = 1
        elif boardVal == 2:
            self.dead = 1
        elif boardVal == 11:
            self.dead = 1
        elif boardVal == 22:
            self.dead = 1
        elif boardVal == 3:
            self.fat = 1
            self.powerUpTurns = 5
        elif boardVal == 4:
            self.slow = 1
            self.powerUpTurns = 5
        elif boardVal == 5:
            self.fast = 1
            self.powerUpTurns = 5
        if not self.dead:
            moveAmount = CELL_SIZE
            if self.slow:
                moveAmount = 10
            elif self.fast:
                moveAmount = 30
            if self.currentDirection == 0:
                if self.y - moveAmount < 0:
                    self.dead = 1
                    return
                self.y -= moveAmount 
            elif self.currentDirection == 2:
                if self.y + moveAmount > self.height - CELL_SIZE:
                    self.dead = 1
                    return
                self.y += moveAmount
            elif self.currentDirection == 3:
                if self.x - moveAmount < 0:
                    self.dead = 1
                    return
                self.x -= moveAmount
            else:
                if self.x + moveAmount > self.width - CELL_SIZE:
                    self.dead = 1
                    return
                self.x += moveAmount

    def move_up(self):
        if self.currentDirection == 2:
            self.dead = 1
        tup = get_array_pos()
        self.gs.board[tup[1]][tup[0]] = 11
        boardVal = self.gs.board[tup[1]-1][tup[0]]
        self.currentDirection = 0
        updatePlayer(boardVal)

    def move_down(self): 
        if self.currentDirection == 0:
            self.dead = 1
        tup = get_array_pos()
        self.gs.board[tup[1]][tup[0]] = 11
        boardVal = self.gs.board[tup[1]-1][tup[0]]
        self.currentDirection = 2
        updatePlayer(boardVal)

    def move_left(self): 
        if self.currentDirection == 1:
            self.dead = 1
        tup = get_array_pos()
        self.gs.board[tup[1]][tup[0]] = 11
        boardVal = self.gs.board[tup[1]-1][tup[0]]
        self.currentDirection = 3
        updatePlayer(boardVal)

    def move_right(self):
        if self.currentDirection == 3:
            self.dead = 1
        tup = get_array_pos()
        self.gs.board[tup[1]][tup[0]] = 11
        boardVal = self.gs.board[tup[1]][tup[0]+1]
        self.currentDirection = 4
        updatePlayer(boardVal)

class OtherPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, image, name, gamespace):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.name = name
        self.dead = 0
        self.fat = 0
        self.slow = 0
        self.fast = 0
        self.powerUpTurns = 0
        self.currentDirection = 3
        self.gs = gamespace
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


class GameSpace:

    def titleScene(self, factory, who): 
        '''Title scene with start button'''
        # Save factory
        self.factory = factory

        self.who = who

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

        if (who == "host"):
            self.p1 = Player1(self.width/4, self.height/2, mediafile + "gabe.png", "gabe", self)
            self.p2 = Player2(self.width*3/4, self.height/2, self, mediafile + "doge.png", "doge", self)
        else:
            self.p1 = Player2(self.width/4, self.height/2, mediafile + "gabe.png", "gabe", self)
            self.p2 = Player1(self.width*3/4, self.height/2, self, mediafile + "doge.png", "doge", self)

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


