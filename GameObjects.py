import pygame, sys
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import json

mediafile = "./mediafiles/"
CELL_SIZE = 10
SYNC_FREQ = 2

class Board():
    '''Game board to hold position of characters and their trails'''
    def __init__(self, gamespace):
        self.gs = gamespace
        self.board = []
        for y in range(int(self.gs.height / CELL_SIZE)):
            row = []
            for x in range(int(self.gs.width / CELL_SIZE)):
                row.append(0)
            self.board.append(row)

        print('board length', len(self.board))
        print('board width', len(self.board[0]))

    def putOnBoard(self, thing, x, y):
        if (thing.name == "gabe"):
            self.board[int(y)][int(x)] = 1
        elif (thing.name == "doge"):
            self.board[int(y)][int(x)] = 2

    def deleteFromBoard(self, x, y):
        self.board[y][x] = 0

class Player(pygame.sprite.Sprite):
    '''You as the player!'''
    def __init__(self, x, y, image, name, gamespace):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = name
        if self.name == "doge":
            self.currentDirection = 3
            self.trail = 22
        else:
            self.currentDirection = 1
            self.trail = 11
        self.dead = 0
        self.fat = 0
        self.slow = 0
        self.fast = 0
        self.powerUpTurns = 0
        self.gs = gamespace
        self.gs.gameboard.putOnBoard(self, int(self.x/CELL_SIZE), int(self.y/CELL_SIZE))
        self.moveAmount = 20
        
    def get_array_pos(self):
        '''Return board position given position in game window'''
        x = int(self.x / CELL_SIZE)
        y = int(self.y / CELL_SIZE)
        return (x, y)

    def tick(self, totalTicks):
        x,y = self.get_array_pos()
        boardVal = 0
        boardVal2 = 0

        # Check if board cells are valid
        if self.currentDirection == 0: 
            try:
                boardVal = self.gs.gameboard.board[y-1][x]
                boardVal2 = self.gs.gameboard.board[y-2][x]
            except IndexError:
                pass
        elif self.currentDirection == 1:
            try:
                boardVal = self.gs.gameboard.board[y][x+1]
                boardVal2 = self.gs.gameboard.board[y][x+2]
            except IndexError:
                pass
        elif self.currentDirection == 2:
            try:
                boardVal = self.gs.gameboard.board[y+1][x]
                boardVal2 = self.gs.gameboard.board[y+2][x]
            except IndexError:
                pass
        elif self.currentDirection == 3:
            try:
                boardVal = self.gs.gameboard.board[y][x-1]
                boardVal2 = self.gs.gameboard.board[y][x-2]
            except IndexError:
                pass

        self.powerUpTurns -= 1
        if self.powerUpTurns <= 0:
            self.powerUpTurns = 0
            self.fat = 0
            self.slow = 0
            self.fast = 0

        # Collided into Gabe
        if boardVal == 1 or boardVal2 == 1:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        # Collided into Doge
        elif boardVal == 2 or boardVal2 == 1:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        # Collided into trail
        elif boardVal == 11 or boardVal == 22 or boardVal2 == 11 or boardVal2 ==22:
            print('IMDEAD')
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        # Got the taco or pizza
        elif boardVal == 3 or boardVal2 == 3:
            self.fat = 1
            self.powerUpTurns = 5
            self.gs.factory.data_connection.sendSizeChange()
        # Stepped into dog poop
        elif boardVal == 4 or boardVal2 == 4:
            self.slow = 1
            self.gs.factory.data_connection.sendSpeed(10)
            self.powerUpTurns = 5
        # Got energy drink
        elif boardVal == 5 or boardVal2 == 5:
            self.fast = 1
            self.gs.factory.data_connection.sendSpeed(30)
            self.powerUpTurns = 5

        if not self.dead:
            if self.slow:
                self.moveAmount = 10
            elif self.fast:
                self.moveAmount = 30
            # Moving up
            if self.currentDirection == 0:
                # Collided into top wall
                if self.y - self.moveAmount < 0:
                    self.dead = 1
                    self.gs.factory.data_connection.sendCollision()
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y-1][x] = self.trail
                    self.gs.gameboard.board[y-2][x] = 1
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y-1][x] = self.trail
                    self.gs.gameboard.board[y-2][x] = self.trail
                    self.gs.gameboard.board[y-3][x] = 1
                else:
                    self.gs.gameboard.board[y-1][x] = 1
                self.gs.gameboard.board[y][x] = self.trail
                self.y -= self.moveAmount 
            # Moving down
            elif self.currentDirection == 2:
                # Collided into bottom wall
                if self.y + self.moveAmount > self.gs.height - CELL_SIZE:
                    self.dead = 1
                    self.gs.factory.data_connection.sendCollision()
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y+1][x] = self.trail
                    self.gs.gameboard.board[y+2][x] = 1
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y+1][x] = self.trail
                    self.gs.gameboard.board[y+2][x] = self.trail
                    self.gs.gameboard.board[y+3][x] = 1
                else:
                    self.gs.gameboard.board[y+1][x] = 1
                self.gs.gameboard.board[y][x] = self.trail
                self.y += self.moveAmount
            # Moving left
            elif self.currentDirection == 3:
                # Collided into left wall
                if self.x - self.moveAmount < 0:
                    self.dead = 1
                    self.gs.factory.data_connection.sendCollision()
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y][x-1] = self.trail
                    self.gs.gameboard.board[y][x-2] = 1
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y][x-1] = self.trail
                    self.gs.gameboard.board[y][x-2] = self.trail
                    self.gs.gameboard.board[y][x-3] = 1
                else:
                    self.gs.gameboard.board[y][x-1] = 1
                self.gs.gameboard.board[y][x] = self.trail
                self.x -= self.moveAmount
            # Moving right
            else:
                # Collided into right wall
                if self.x + self.moveAmount > self.gs.width - CELL_SIZE:
                    self.dead = 1
                    self.gs.factory.data_connection.sendCollision()
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y][x+1] = self.trail
                    self.gs.gameboard.board[y][x+2] = 1
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y][x+1] = self.trail
                    self.gs.gameboard.board[y][x+2] = self.trail
                    self.gs.gameboard.board[y][x+3] = 1
                else:
                    self.gs.gameboard.board[y][x+1] = 1
                self.gs.gameboard.board[y][x] = self.trail
                self.x += self.moveAmount
            self.rect.topleft = (self.x, self.y)
            
        # Synchronize 30 times a second
        if (not totalTicks % SYNC_FREQ):
            print("Synchronizing: {}".format(totalTicks))
            self.gs.factory.data_connection.sendData(self.x, self.y, self.currentDirection, self.moveAmount, self.dead)

    def move_up(self, totalTicks):
        if self.currentDirection == 2:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        self.currentDirection = 0
        if (totalTicks % SYNC_FREQ):
            print("UP: {}".format(totalTicks))
            self.gs.factory.data_connection.sendData(self.x, self.y, self.currentDirection, self.moveAmount, self.dead)

    def move_down(self, totalTicks): 
        if self.currentDirection == 0:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        self.currentDirection = 2
        if (totalTicks % SYNC_FREQ):
            print("DOWN: {}".format(totalTicks))
            self.gs.factory.data_connection.sendData(self.x, self.y, self.currentDirection, self.moveAmount, self.dead)

    def move_left(self, totalTicks): 
        if self.currentDirection == 1:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        self.currentDirection = 3
        if (totalTicks % SYNC_FREQ):
            print("LEFT: {}".format(totalTicks))
            self.gs.factory.data_connection.sendData(self.x, self.y, self.currentDirection, self.moveAmount, self.dead)

    def move_right(self, totalTicks):
        if self.currentDirection == 3:
            self.dead = 1
            self.gs.factory.data_connection.sendCollision()
            return
        self.currentDirection = 1
        if (totalTicks % SYNC_FREQ):
            print("RIGHT: {}".format(totalTicks))
            self.gs.factory.data_connection.sendData(self.x, self.y, self.currentDirection, self.moveAmount, self.dead)

class OtherPlayer(pygame.sprite.Sprite):
    '''Other player's movements are dictated by what is sent from the other player'''
    def __init__(self, x, y, image, name, gamespace):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.name = name
        self.dead = 0
        if self.name == "gabe":
            self.currentDirection = 1
            self.trail = 11
        else:
            self.currentDirection = 3
            self.trail = 22
        self.moveAmount = 0
        self.gs = gamespace
        self.gs.gameboard.putOnBoard(self, int(self.x/CELL_SIZE), int(self.y/CELL_SIZE))

    def get_array_pos(self):
        x = int(self.x / CELL_SIZE)
        y = int(self.y / CELL_SIZE)
        return (x, y)

    def tick(self, totalTicks):
        '''Send location to other player'''

        # Retrieve data from host player about Player 1
        dataQueue = self.gs.factory.data_connection.returnData()
        while (not dataQueue.empty()):
            data = dataQueue.get()
            try:
                data = json.loads(data) # dictionary
            except:
                print("OtherPlayer: could not decode data {}".format(data))
                continue

            for key, value in data.items():
                if key == "state":
                    self.dead = 1
                    print("TICK: you win!")
                    return
                elif key == "x":
                    self.x = int(value)
                elif key == "y":
                    self.y = int(value)
                elif key == "dir":
                    self.currentDirection = int(value)
                elif key == "speed":
                    self.moveAmount = int(value)
                elif key == "dead":
                    self.dead = int(value)
            
        # UPDATE other player with received data
        x,y = self.get_array_pos()
        if not self.dead:
            # Other player moving up 
            if self.currentDirection == 0:
                if self.y - self.moveAmount < 0:
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y-1][x] = self.trail
                    self.gs.gameboard.board[y-2][x] = 2 
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y-1][x] = self.trail
                    self.gs.gameboard.board[y-2][x] = self.trail
                    self.gs.gameboard.board[y-3][x] = 2
                else:
                    self.gs.gameboard.board[y-1][x] = 2
                self.gs.gameboard.board[y][x] = self.trail
                self.y -= self.moveAmount 
            # Other player moving down
            elif self.currentDirection == 2:
                if self.y + self.moveAmount > self.gs.height - CELL_SIZE:
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y+1][x] = self.trail
                    self.gs.gameboard.board[y+2][x] = 2 
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y+1][x] = self.trail
                    self.gs.gameboard.board[y+2][x] = self.trail
                    self.gs.gameboard.board[y+3][x] = 2
                else:
                    self.gs.gameboard.board[y+1][x] = 2
                self.gs.gameboard.board[y][x] = self.trail
                self.y += self.moveAmount
            # Other player moving left
            elif self.currentDirection == 3:
                if self.x - self.moveAmount < 0:
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y][x-1] = self.trail
                    self.gs.gameboard.board[y][x-2] = 2 
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y][x-1] = self.trail
                    self.gs.gameboard.board[y][x-2] = self.trail
                    self.gs.gameboard.board[y][x-3] = 2
                else:
                    self.gs.gameboard.board[y][x-1] = 2
                self.gs.gameboard.board[y][x] = self.trail
                self.x -= self.moveAmount
            # Other player moving right
            else:
                if self.x + self.moveAmount > self.gs.width - CELL_SIZE:
                    return
                if self.moveAmount == 20:
                    self.gs.gameboard.board[y][x+1] = self.trail
                    self.gs.gameboard.board[y][x+2] = 2 
                elif self.moveAmount == 30:
                    self.gs.gameboard.board[y][x+1] = self.trail
                    self.gs.gameboard.board[y][x+2] = self.trail
                    self.gs.gameboard.board[y][x+3] = 2
                else:
                    self.gs.gameboard.board[y][x+1] = 2
                self.gs.gameboard.board[y][x] = self.trail
                self.x += self.moveAmount
            self.rect.topleft = (self.x, self.y)

class GameSpace:
    def loadScene(self, factory, who): 
        '''Loading scene while connections are being established'''
        # Save factory
        self.factory = factory
        self.who = who

        # Initialize the game space
        pygame.init()
        if (self.who == "host"):
            pygame.display.set_caption("Host player")
        else:
            pygame.display.set_caption("Client player")
        self.size = self.width, self.height = 640, 420
        self.black = 0,0,0
        self.screen = pygame.display.set_mode(self.size)
        #pygame.key.set_repeat(10, 30)

        bigfont = pygame.font.Font(None, 40)
        if (self.who == "host"):
            text = "Waiting for P2..."
        else:
            text = "Waiting for P1..."
        self.load = bigfont.render(text, 0, (250, 250, 250))
        self.loadRect = self.load.get_rect()
        self.loadRect.topleft = (self.width/2 - self.loadRect.width/2, self.height/2)
        self.screen.blit(self.load, self.loadRect)
        pygame.display.flip()

        self.loop = LoopingCall(self.loadLoop)
        self.loop.start(1/60)
    
    def loadLoop(self):
        if self.factory.command_connection.ready:
            self.screen.fill(self.black)
            pygame.display.flip()
            self.loop.stop()
            self.titleScene()

        for event in pygame.event.get():
            # Close pygame
            if event.type == pygame.QUIT:
                reactor.stop()
            # Key detection
            elif event.type == pygame.KEYDOWN:
                # Escape key to end pygame
                if (event.key == pygame.K_ESCAPE):
                    reactor.stop()

    def titleScene(self):
        '''Start scene with button'''
        # Menu's game title text
        bigfont = pygame.font.Font(None, 40)
        self.title = bigfont.render('Gabe vs. Doge', 0, (250, 250, 250))
        self.titleRect = self.title.get_rect()
        self.titleRect.topleft = (self.width/2 - self.titleRect.width/2, 80)

        # Menu's start button 
        font = pygame.font.Font(None, 20)
        self.startText = font.render('Start', 0, (30, 120, 50))
        self.textRect = self.startText.get_rect()
        self.textRect.topleft = (self.width/2 - self.textRect.width/2, self.height/2 + 10)
        self.startButton = pygame.Rect(0, 0, 100, 40)
        self.startButton.topleft = (self.width/2 - self.startButton.width/2, self.height/2)
        pygame.draw.rect(self.screen, (30, 120, 50), self.startButton, 1)

        # Game items
        self.dogetrail = pygame.image.load(mediafile + "dogetrail.png")
        self.gabetrail = pygame.image.load(mediafile + "gabetrail.png")
        self.taco = pygame.image.load(mediafile + "Taco_Emoji.png")
        self.pizza = pygame.image.load(mediafile + "Pizza_Emoji.png")
        self.poop = pygame.image.load(mediafile + "Poop_Emoji.png")
        self.energy = pygame.image.load(mediafile + "5hourenergy.png")

        # Pretty pictures for scene
        self.GiantDoge = pygame.image.load(mediafile + "GiantDoge.png")
        self.GiantDogerect = self.GiantDoge.get_rect()
        self.GiantDogerect.move_ip(self.width*3/4-80, self.height/2)
        self.GiantGabe = pygame.image.load(mediafile + "GiantGabe.png")
        self.GiantGaberect = self.GiantGabe.get_rect()
        self.GiantGaberect.move_ip(30, self.height/2)

        # Draw title and startText to screen
        self.screen.blit(self.startText, self.textRect)
        self.screen.blit(self.title, self.titleRect)
        self.screen.blit(self.GiantGabe, self.GiantGaberect)
        self.screen.blit(self.GiantDoge, self.GiantDogerect)
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
                    self.factory.command_connection.sendEnd()
                    reactor.stop()
                # Key detection
                elif event.type == pygame.KEYDOWN:
                    # Escape key to end pygame
                    if (event.key == pygame.K_ESCAPE):
                        self.factory.command_connection.sendEnd()
                        reactor.stop()
                # Mouse detection
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # User clicked start
                    if self.startButton.collidepoint(mouse_pos):
                        self.factory.command_connection.sendStart()
            self.screen.blit(self.startText, self.textRect)
            self.screen.blit(self.title, self.titleRect)
            self.screen.blit(self.GiantGabe, self.GiantGaberect)
            self.screen.blit(self.GiantDoge, self.GiantDogerect)

            pygame.display.flip()
        # Transition to game scene
        else:
            print("hello")
            self.screen.fill(self.black)
            pygame.display.flip()
            # Stop title loop and go to game scene
            self.loop.stop()
            self.gameScene()

    def get_real_pos(self, y, x):
        '''Translate board position to game window position'''
        return (x*CELL_SIZE, y*CELL_SIZE)

    def gameScene(self):
        '''Actual game!'''
        # Set up game objects
        self.gameboard = Board(self)
        self.totalTicks = 0

        # Host player
        if (self.who == "host"):
            self.you = Player(self.width/4, self.height/2, mediafile + "gabe.png", "gabe", self)
            self.other = OtherPlayer(self.width*3/4, self.height/2, mediafile + "doge.png", "doge", self)
        # Client player
        else:
            self.you = Player(self.width*3/4, self.height/2,  mediafile + "doge.png", "doge", self)
            self.other = OtherPlayer(self.width/4, self.height/2, mediafile + "gabe.png", "gabe", self)

        # List to hold all other game objects
        self.all_objects = [self.you, self.other]

        # Draw players onto screen
        self.screen.blit(self.you.image, self.you.rect)
        self.screen.blit(self.other.image, self.other.rect)

        # Start game loop
        self.loop = LoopingCall(self.gameloop)
        self.loop.start(1/60)

    def gameloop(self):

        if self.you.dead:
            self.loop.stop()
            self.endScene("You lost :(")
            return

        elif self.other.dead:
            self.loop.stop()
            self.endScene("You win!")
            return

        for event in pygame.event.get():
            # Close pygame
            if event.type == pygame.QUIT:
                self.factory.command_connection.sendEnd()
                reactor.stop()
            # Key detection
            elif event.type == pygame.KEYDOWN:
                # Escape key to end pygame
                if (event.key == pygame.K_ESCAPE):
                    self.factory.command_connection.sendEnd()
                    reactor.stop()
                elif (event.key == pygame.K_UP):
                    if self.you.currentDirection != 0:
                        self.you.move_up(self.totalTicks)
                elif (event.key == pygame.K_DOWN):
                    if self.you.currentDirection != 2:
                        self.you.move_down(self.totalTicks)
                elif (event.key == pygame.K_RIGHT):
                    if self.you.currentDirection != 1:
                        self.you.move_right(self.totalTicks)
                elif (event.key == pygame.K_LEFT):
                    if self.you.currentDirection != 3:
                        self.you.move_left(self.totalTicks)
    
        for obj in self.all_objects:
            obj.tick(self.totalTicks)

        self.screen.fill(self.black)

        # Draw to screen based on things on board
        for y in range(0, len(self.gameboard.board)):
            for x in range(0, len(self.gameboard.board[0])):
                    if self.gameboard.board[y][x] == 11:
                        tup = self.get_real_pos(y, x)
                        img = self.gabetrail
                        rect = img.get_rect()
                        rect.topleft = tup 
                        self.screen.blit(img, rect)
                    elif self.gameboard.board[y][x] == 22:
                        tup = self.get_real_pos(y, x)
                        img = self.dogetrail
                        rect = img.get_rect()
                        rect.topleft = tup 
                        self.screen.blit(img, rect)
                    elif self.gameboard.board[y][x] == 3:
                        tup = self.get_real_pos(y, x)
                        rect = self.taco.get_rect()
                        rect.topleft = tup
                        self.screen.blit(self.taco, rect)
                    elif self.gameboard.board[y][x] == 4:
                        tup = get_real_pos(y, x)
                        rect = self.poop.get_rect()
                        rect.topleft = tup 
                        self.screen.blit(self.poop, rect)
                    elif self.gameboard.board[y][x] == 5:
                        tup = get_real_pos(y, x)
                        rect = self.energy.get_rect()
                        rect.topleft = tup 
                        self.screen.blit(self.energy, rect)
                        
        self.screen.blit(self.you.image, self.you.rect)
        self.screen.blit(self.other.image, self.other.rect)
        pygame.display.flip()

        self.totalTicks += 1

    def endScene(self, text):
        self.screen.blit(self.GiantGabe, self.GiantGaberect)
        self.screen.blit(self.GiantDoge, self.GiantDogerect)
        bigfont = pygame.font.Font(None, 40)
        self.endText = bigfont.render(text, 0, (250, 250, 250))
        self.endTextRect = self.endText.get_rect()
        self.endTextRect.move_ip(self.width/2 - 40, self.height/2)
        print("Location: {}, {}".format(self.endTextRect.left, self.endTextRect.top))
        self.screen.blit(self.endText, self.endTextRect)
        pygame.display.flip()
        self.loop = LoopingCall(self.endLoop)
        self.loop.start(1/60)

    def endLoop(self):
        '''Handle proper closing of game'''
        for event in pygame.event.get():
            # Close pygame
            if event.type == pygame.QUIT:
                self.factory.command_connection.sendEnd()
                reactor.stop()
            # Key detection
            elif event.type == pygame.KEYDOWN:
                # Escape key to end pygame
                if (event.key == pygame.K_ESCAPE):
                    self.factory.command_connection.sendEnd()
                    reactor.stop()

