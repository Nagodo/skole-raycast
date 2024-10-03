import pygame
import random
import math
from player import Player
from bullet import Bullet
#Multi threading
from threading import Thread

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Create the screen
screensize = (800, 800)
screen = pygame.display.set_mode(screensize, pygame.DOUBLEBUF, 32)
screen.fill((0, 0, 0))


newRaycastDone = False
grasscolor = [(64, 176, 56), (45, 171, 36)]

rayAmount = 48 #Amount of rays
rayLength = 20 #Length of the rays


precalc = [[None for _ in range(rayLength)] for _ in range(rayAmount)]
USE_PRECALC = True

class Game:
    def __init__(self):
        self.gridsize = 40
        self.mapsize = 1600, 1600
        self.grid = Grid(self.gridsize, self.mapsize)
        self.Player = Player(self.gridsize)

        self.bullets = []


        #Place camera in the middle of the map
        x = (self.mapsize[0] - screensize[0]) / 2
        y = (self.mapsize[1] - screensize[1]) / 2

        #Place player in center of screen
        self.Player.x = (screensize[0] / 2) - (self.Player.size / 2)
        self.Player.y = (screensize[1] / 2) - (self.Player.size / 2)

        self.camOffset = [x, y]

        self.PreCalcRaycast()


        self.MoveObjects([-x, -y])
    
    def MoveObjects(self, move):
        self.camOffset[0] += move[0]
        self.camOffset[1] += move[1]
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                self.grid.grid[i][j].x += move[0]
                self.grid.grid[i][j].y += move[1]
        
        for i in range(len(self.bullets)):
            self.bullets[i].x += move[0]
            self.bullets[i].y += move[1]

    def PreCalcRaycast(self):
        for i in range(0, rayAmount):
            precalc.append([])
            for j in range(0, rayLength):
                x = (self.Player.size / 2) + (math.cos(math.radians(i *(360 / rayAmount))) * (rayLength * j))
                y = (self.Player.size / 2) + (math.sin(math.radians(i *(360 / rayAmount))) * (rayLength * j))
                
                precalc[i][j] = [x, y]

    
    def RayCast(self):
        #Raycast
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                if self.grid.grid[i][j].makeblack:
                    self.grid.grid[i][j].visible = False
                    self.grid.grid[i][j].faded = False   
                self.grid.grid[i][j].makeblack = True

        
        rayAmount = 48 #Amount of rays
        for i in range(0, rayAmount):
          
            stopNext = False
            for j in range(0, 20): #Ray length

                if USE_PRECALC:
                    x = self.Player.x + precalc[i][j][0]
                    y = self.Player.y + precalc[i][j][1]
                else:
                    x = self.Player.x + (self.Player.size / 2) + (math.cos(math.radians(i *(360 / rayAmount))) * (rayLength * j))
                    y = self.Player.y + (self.Player.size / 2) + (math.sin(math.radians(i *(360 / rayAmount))) * (rayLength * j))
            
                
                tile = self.grid.GetTile(int(x), int(y))
                if stopNext:
                    break
                if tile != None:
                    if tile.type == "wall":
                        stopNext = True
                    tile.visible = True
                    if j > 18:
                        tile.faded = 180
                    elif j > 17:
                        tile.faded = 145
                    elif j > 16:
                        tile.faded = 110
                    else:
                        tile.faded = False
                    tile.makeblack = False
                

    def CheckWallCollision(self, move):
        #Check if the player is colliding with a wall
        #Check if the player is colliding with a wall
        x = self.Player.x + move[0]
        y = self.Player.y + move[1]
        #Check all 4 corners of the player
        for i in range(0, 2):
            for j in range(0, 2):
                tile = self.grid.GetTile(int(x + (self.Player.size * i) + move[0] * -2), int(y + (self.Player.size * j) + move[1] * -2))
                if tile != None:
                    if tile.type == "wall":
                        return [0, 0]
        return move

    def CheckBulletWallCollision(self, bullet):
        #Check if the bullet is colliding with a wall
        x = bullet.x
        y = bullet.y

        tile = self.grid.GetTile(int(x), int(y))
        if tile != None:
            if tile.type == "wall":
                return bullet.Explode()

            
        

    def Shoot(self):
        #Get Direction from mouse
        mouse = pygame.mouse.get_pos()
        x = mouse[0] - (self.Player.x + (self.Player.size / 2))
        y = mouse[1] - (self.Player.y + (self.Player.size / 2))
        direction = [x, y]
        #Normalize the direction
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        direction[0] /= length
        direction[1] /= length
        #Create the bullet
        self.bullets.append(Bullet(self.Player.x + (self.Player.size / 2), self.Player.y + (self.Player.size / 2), direction))

    def draw(self):   
        # Draw the screen
        screen.fill((0, 0, 0))

        # Draw the grid if visible to the player
        for i in range(len(self.grid.grid)):
            for j in range(len(self.grid.grid[i])):
                tile = self.grid.grid[i][j]
                if tile.visible:
                    pygame.draw.rect(screen, (tile.color), (tile.x, tile.y, self.gridsize, self.gridsize))
                    f = tile.faded
                    if f != False:
                        rect = (tile.x, tile.y, self.gridsize, self.gridsize)
                        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
                        pygame.draw.rect(shape_surf, (0, 0, 0, f), shape_surf.get_rect())
                        screen.blit(shape_surf, rect)


        #Draw the bullets
        for i in range(len(self.bullets)):
            pygame.draw.rect(screen, (255, 255, 255), (self.bullets[i].x, self.bullets[i].y, 5, 5))
        #Draw the player as a rect
        pygame.draw.rect(screen, (255, 255, 255), (self.Player.x, self.Player.y, self.Player.size, self.Player.size))
        
        #Draw text
        
        text = font.render("Right click to place wall", True, (255, 255, 255))
        screen.blit(text, (10, 10))

class Grid:
    def __init__(self, gridsize, mapsize):
        self.gridsize = gridsize
        self.mapsize = mapsize
        self.grid = []
        self.Setup()

      
    def Setup(self):
        color = grasscolor[0]
        a = int(self.mapsize[0] / self.gridsize)
        b = int(self.mapsize[1] / self.gridsize)

        for i in range(0, a):
            self.grid.append([])
            for j in range(0, b):
                
                self.grid[i].append(Tile(i, j, color))
                if color == grasscolor[0]:
                    color = grasscolor[1]
                else:
                    color = grasscolor[0]
            if color == grasscolor[0]:
                color = grasscolor[1]
            else:
                color = grasscolor[0]
        


    def GetTile(self, x, y):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j].x < x < self.grid[i][j].x + self.gridsize and self.grid[i][j].y < y < self.grid[i][j].y + self.gridsize:
                    return self.grid[i][j]
        return None      
        

class Tile:
    def __init__(self, x, y, color, type="grass"):
        self.x = x * 40
        self.y = y * 40
        self.color = color
        self.type = type
        self.makeblack = True
        self.collider = False
        self.visible = False
        self.faded = False
    
   
def DrawThread():
    while running:
        game.draw()

        pygame.display.flip()

pauseRayCast = False
def RayCastThread():
    game.RayCast()
    while running:
        if game.Player.moving and not pauseRayCast:
            game.RayCast()

def BulletHandlerThread():
    while running:
        for i in range(len(game.bullets)):
            out = game.bullets[i].Move()
            if out:
                game.bullets.pop(i)
                break
            else:
                ex = game.CheckBulletWallCollision(game.bullets[i])
                if ex:
                    game.bullets.pop(i)
                    break
        

game = Game()

#Start the raycast thread


# Game loop
running = True
drawthread = Thread(target=DrawThread).start()
raycastthread = Thread(target=RayCastThread).start()
bullethandlerthread = Thread(target=BulletHandlerThread).start()
mousepos = [0, 0]
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_p:
                pauseRayCast = not pauseRayCast
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                #get Clicked Tile
                mousepos = pygame.mouse.get_pos()
                tile = game.grid.GetTile(mousepos[0], mousepos[1])
                tile.type = "wall"
                tile.color = (100, 100, 100)
            
            if event.button == 1:
                game.Shoot()
            
            
    
    keys = pygame.key.get_pressed()  #checking pressed keys

    movespeed = 1.5
    move = [0, 0]
    if keys[pygame.K_w]:
        move[1] += movespeed
    if keys[pygame.K_s]:
        move[1] -= movespeed
    if keys[pygame.K_a]:
        move[0] += movespeed
    if keys[pygame.K_d]:
        move[0] -= movespeed
        
    if (move[0] != 0 or move[1] != 0):
        game.Player.moving = True
        #Check if the player is colliding with a wall
        move = game.CheckWallCollision(move)
        game.MoveObjects(move)
    else:
        game.Player.moving = False

    
        
    clock.tick(60)
    
