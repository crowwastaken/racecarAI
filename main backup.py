import pygame
import os
import math

from math import pi

width = 1920
height = 980

pygame.init()
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('backup')
localpath = os.path.dirname(os.path.abspath(__file__))

#60 fps
clock = pygame.time.Clock()
deltaT = clock.tick(60)

playerSprite = pygame.image.load(os.path.join(localpath, "car.png"))
map = pygame.image.load(os.path.join(localpath, "map.png"))
#map = pygame.transform.rotozoom(map, 0, width/1920)

raycastRange = 500

roadColor = pygame.Color(255, 255, 255, 255)
wallColor = pygame.Color(0, 0, 0, 255)
finishLineColor = pygame.Color(237, 28, 36, 255)

#forward, backward, left, right
player = playerSprite
playerRect = playerSprite.get_rect(center = playerSprite.get_rect(center = (0, 0)).center)
playerMovement = [0, 0, 0, 0]
playerPos = [200, 300]
playerRotation = 0
playerRotationRad = playerRotation * pi / 180

playerTopSpeed = 1
playerAcceleration = 0.01
playerSpeed = 0
playerTurnSpeed = 0.4
playerDeadzoneSpeed = 0.05

def updateMovement(keysPressed):
    global player
    global playerRect
    global playerPos
    global playerRotation
    global playerRotationRad
    global playerSpeed
    global playerTopSpeed
    global playerAcceleration
    global playerDeadzoneSpeed

    #keys pressed convert to values
    forwardBackward = -(int(keysPressed[pygame.K_w]) - int(keysPressed[pygame.K_s]))
    rotation = (int(keysPressed[pygame.K_a]) - int(keysPressed[pygame.K_d]))
    
    #not accelerating
    if forwardBackward == 0 and playerSpeed != 0:
        playerSpeed += playerAcceleration * (int(playerSpeed < 0) * 2 - 1) / 5

    #set deadzone
    if abs(playerSpeed) < playerDeadzoneSpeed and forwardBackward == 0:
        playerSpeed = 0

    #acceleration
    if forwardBackward != 0 and abs(playerSpeed) < playerTopSpeed:
        #accelerating
        braking = 1 # not braking
        if int(forwardBackward > 0) != int(playerSpeed > 0): # braking
            braking = 2
        playerSpeed += forwardBackward * playerAcceleration * braking


    #turn influence is a turningspeed variable affected by playerspeed
    if playerSpeed == 0:
        turnInfluence = 0
    else:
        turnInfluence = 1 / abs(playerSpeed)
        if turnInfluence > playerTurnSpeed:
            turnInfluence = playerTurnSpeed
    playerRotation += rotation * playerTurnSpeed * turnInfluence * (int(playerSpeed < 0) * 2 - 1) * deltaT
    playerRotationRad = playerRotation * pi / 180

    playerPos[0] += math.sin(playerRotationRad) * playerSpeed * deltaT
    playerPos[1] += math.cos(playerRotationRad) * playerSpeed * deltaT

    player = pygame.transform.rotate(playerSprite, playerRotation)
    playerRect = player.get_rect(center = playerSprite.get_rect(center = (0, 0)).center)

    playerRect.move_ip(playerPos)


    #playerPos[0] += (playerMovement[3] - playerMovement[2]) * playerTopSpeed

def raycastDistance(currentPosition, angle):
    counter = 0
    rayPos = currentPosition[:]

    while(counter < raycastRange):
        rayPos[0] += math.sin(-angle)
        rayPos[1] -= math.cos(-angle)

        if(colorAtPos(rayPos) == wallColor):
            return math.sqrt((currentPosition[0] - rayPos[0])**2 + (currentPosition[1] - rayPos[1])**2)

        counter += 1
    
    return raycastRange

def colorAtPos(position):
    return map.get_at([round(coord) for coord in position])

quit = False

while not quit:
    deltaT = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        
    keysPressed = pygame.key.get_pressed()
    updateMovement(keysPressed)

    #print(playerPos)
    #print(playerRotation)
    #print(playerRect.center)
    playerPixel = colorAtPos(playerPos)
    if(playerPixel != roadColor):
        #something happened
        if(playerPixel == wallColor):
            print("crashed!!!")
            playerTopSpeed = 0
            playerSpeed = 0
    
    print(raycastDistance(playerPos, playerRotationRad))

    display.blit(map, (0, 0))
    display.blit(player, playerRect)


    rays = [raycastDistance(playerPos, playerRotationRad + pi/4), raycastDistance(playerPos, playerRotationRad), raycastDistance(playerPos, playerRotationRad - pi/4)]
    
    for x in [pi/2, pi/4, 0, -pi/4, -pi/2]:
        pygame.draw.line(display, (255,0,0), playerPos, (playerPos[0] - raycastDistance(playerPos, playerRotationRad + x) * math.sin(playerRotationRad + x), playerPos[1] - raycastDistance(playerPos, playerRotationRad + x) * math.cos(playerRotationRad + x)), 2)

    pygame.display.update()
            
        

pygame.quit()
exit()