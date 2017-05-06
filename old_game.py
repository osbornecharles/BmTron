import pygame, sys
import math
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

media_file_path = "./mediafiles/"


class DeathStar(pygame.sprite.Sprite):
    # Every player consists of an image and a rectangle
    def __init__(self, gamespace):
        self.gs = gamespace
        self.image = pygame.image.load(media_file_path + "deathstar.png")
        self.rect = self.image.get_rect()
        self.rect.move_ip(50, 50) # set location 
        self.copy = self.image

    def tick(self):
        '''Process rotation'''
        # Get image center
        xcenter = self.rect.centerx
        ycenter = self.rect.centery

        # Get new mouse position
        xf, yf = pygame.mouse.get_pos()

        # Reset image
        self.image = self.copy

        # Find adjacent and opposite
        opp = xf - xcenter
        adj = yf - ycenter
        
        # Calculate degree for rotation
        rad = math.atan2(opp, adj)
        deg = math.degrees(rad)

        # Rotate image and reset the center
        self.image = pygame.transform.rotate(self.image, deg - 130)
        self.rect.centerx = xcenter
        self.rect.centery = ycenter

    def move(self, key_event):
        '''Handle key events'''
        if (key_event == pygame.K_UP):
            self.rect.move_ip(0, -4)
            #print("UP")
        elif (key_event == pygame.K_DOWN):
            self.rect.move_ip(0, 4)
            #print("DOWN")
        elif (key_event == pygame.K_RIGHT):
            self.rect.move_ip(4,0)
            #print("RIGHT")
        elif (key_event == pygame.K_LEFT):
            self.rect.move_ip(-4,0)
            #print("LEFT")
        
class Doge(pygame.sprite.Sprite):
    # Every player consists of an image and a rectangle
    def __init__(self, gamespace):
        self.gs = gamespace
        #self.image = pygame.image.load(media_file_path + "globe.png")
        self.image = pygame.image.load(media_file_path + "doge.png")
        self.copy = self.image
        self.rect = self.image.get_rect()
        self.rect.move_ip(340, 150)
        self.hitpoint = 50
        self.frame_num = 0

    def tick(self):
        '''Need to process the hit points'''
        # Check if hit points is less than 0
        if self.hitpoint <= 0:
            #print("DESTROYED EARTH")
            xcenter = self.rect.centerx
            ycenter = self.rect.centery
            if (self.frame_num < 10):
                self.image = pygame.image.load(media_file_path + "explosion/frames00" + str(self.frame_num) + "a.png")
            elif (self.frame_num < 17): 
                self.image = pygame.image.load(media_file_path + "explosion/frames0" + str(self.frame_num) + "a.png")
            else: # earth is destroyed so remove from gamespace
                self.gs.all_objects.remove(self)
                self.gs.enemy = None
            self.rect.centerx = xcenter
            self.rect.centery = ycenter

            self.frame_num += 1

    def move(self):
        '''Handle key events'''
        pass

class Laser(pygame.sprite.Sprite):
    def __init__(self, gamespace, mouse):
        self.gs = gamespace
        self.image = pygame.image.load(media_file_path + "bubble.png")
        self.copy = self.image
        self.rect = self.image.get_rect()
        self.rect.move_ip(self.gs.player.rect.centerx, self.gs.player.rect.centery) # starts from the center of deathstar

        self.speed = 10. # speed of bubble
        distance = [ mouse[0] - self.rect.centerx , mouse[1] - self.rect.centery ] 
        norm = math.sqrt(distance[0] ** 2 + distance[1]**2 )
        self.direction = [distance[0]/ norm, distance[1]/ norm]
        self.bullet_vector = [ self.direction[0] * self.speed, self.direction[1] * self.speed ] 

    def tick(self):
        '''Move the laser'''
        self.rect.x += self.bullet_vector[0]
        self.rect.y += self.bullet_vector[1]

        if self.gs.enemy and pygame.sprite.collide_rect(self.gs.enemy, self): 
            self.gs.enemy.hitpoint -= 10
            print("Hit earth", self.gs.enemy.hitpoint)
            self.gs.all_objects.remove(self) # remove laser from game object list


class GameSpace:
    def main(self): 
        # Step 1: Initialize the game space
        pygame.init()
        self.size = self.width, self.height = 640, 420
        self.black = 0,0,0
        self.screen = pygame.display.set_mode(self.size)
        pygame.key.set_repeat(10, 30)

        # Step 2: Initialize the game objects and place into an array
        #self.clock = pygame.time.Clock()
        self.player1 = DeathStar(self)
        self.player2 = Doge(self)

        self.all_objects = []
        self.all_objects.append(self.player1)
        self.all_objects.append(self.player2)

    def loop():
        '''Step 3: Start the game loop
        Step 4: Tick regulation set at 60 seconds'''
        #self.clock.tick(60)     # frame rate is 60 fps

        # Step 5: Read user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Escape key
                if (event.key == pygame.K_ESCAPE):
                    sys.exit()
                # Space bar
                elif (event.key == pygame.K_SPACE):
                    self.laser = Laser(self, pygame.mouse.get_pos())
                    self.all_objects.append(self.laser)
                # Up, down, left, right keys
                else:
                    self.player.move(event.key) # call move method on game obj

        # Step 6: Call tick() on each game object
        for obj in self.all_objects:
            obj.tick()

        # Step 7: Update screen
        self.screen.fill(self.black)
        for obj in reversed(self.all_objects):
            self.screen.blit(obj.image, obj.rect)
        pygame.display.flip()

if __name__ == "__main__":
    gs = GameSpace()
    gs.main()

    # Step 3: Start the game loop using Twisted's Loopin Call
    lc = LoopingCall(gs.loop)
    lc.start(1/60)

    reactor.run()

