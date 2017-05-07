import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from server import *

media_file_path = "./mediafiles/"
COMMAND_PORT = 40128
CELL_SIZE = 20

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, val):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.dead = 0
        self.fat = 0
        self.slow = 0
        self.fast = 0
        self.powerUpTurns = 0
        self.currentDirection = 1

    def get_array_pos(self, board):
        x = self.x / CELL_SIZE
        y = self.y / CELL_SIZE
        return (x, y)

    def updatePlayer(self, boardVal):
        self.powerUpTurns--
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

    def move_up(self, board):
        if self.currentDirection == 2:
            self.dead = 1
        tup = get_array_pos(board)
        board[tup[1]][tup[0]] = 11
        boardVal = board[tup[1]-1][tup[0]]
        self.currentDirection = 0
        updatePlayer(boardVal)

    def move_down(self, board): 
        if self.y + CELL_SIZE > self.height - CELL_SIZE or self.currentDirection == 0:
            self.dead = 1
        tup = get_array_pos(board)
        board[tup[1]][tup[0]] = 11
        boardVal = board[tup[1]-1][tup[0]]
        self.currentDirection = 2
        updatePlayer(boardVal)

    def move_left(self, board) or self.currentDirecion == 1:
        if self.x - CELL_SIZE < 0:
            self.dead = 1
        tup = get_array_pos(board)
        board[tup[1]][tup[0]] = 11
        boardVal = board[tup[1]-1][tup[0]]
        self.currentDirection = 3
        updatePlayer(boardVal)

    def move_right(self, board):
        if self.x + CELL_SIZE > self.width - CELL_SIZE or self.currentDirection == 3:
            self.dead = 1
        tup = get_array_pos(board)
        board[tup[1]][tup[0]] = 11
        boardVal = board[tup[1]][tup[0]+1]
        self.currentDirection = 4
        updatePlayer(boardVal)


class GameSpace:
    def main(self, factory): 
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
    gs.main(factory)
    reactor.listenTCP(COMMAND_PORT, factory)
    reactor.run()

