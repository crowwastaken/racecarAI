import pygame
import os
import math
from car import *
#from car2 import *

from math import pi

localpath = os.path.dirname(os.path.abspath(__file__))

width = 1920
height = 900
fps = 60

playerSprite = pygame.image.load(os.path.join(localpath, "car.png"))
map = pygame.image.load(os.path.join(localpath, "map.png"))
mapRect = map.get_rect()

pygame.init()
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('racecar')

playerList = pygame.sprite.Group()

#60 fps
clock = pygame.time.Clock()
deltaT = clock.tick(fps)

#intialize player
player = car([200, 300], 0)
playerList.add(player)
#player2 = car2([200, 300], 0)
#playerList.add(player2)

quit = False
drawRays = False

while not quit:
    deltaT = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        if event.type == pygame.KEYUP and event.key == pygame.K_r:
            drawRays = not drawRays
        

    keysPressed = pygame.key.get_pressed()


    player.updateMovement(keysPressed, deltaT)
    #player2.updateMovement(keysPressed, deltaT)


    
    status = player.checkStatus(map)
    if(status[0] == 'finish'):
        print('you finished a lap, time: ', status[1])
        
    if(status[0] == 'crash'):
        print('crashed!!! oops')
        player.status(False)

    #if player2.checkCrashed(map):
    #    player2.status(False)


    #print(player.playerPos)
    #print(playerRotation)
    #print(playerRect.center)
    

    #render goes bottom first, top last

    display.blit(map, mapRect)
    playerList.draw(display)
    if drawRays:
        for ray in player.drawRay(display, map):
            pygame.draw.line(display, ray[1], ray[2], ray[3], ray[4])
    
    pygame.display.update()
            
        

pygame.quit()
exit()