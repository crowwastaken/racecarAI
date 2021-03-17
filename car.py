import pygame
import os
import math

from math import pi

localpath = os.path.dirname(os.path.abspath(__file__))
lapTimer = pygame.time.Clock()

#constants
playerTopSpeed = 1
playerAcceleration = 0.01
playerTurnSpeed = 0.4
playerDeadzoneSpeed = 0.05

playerSprite = pygame.image.load(os.path.join(localpath, "car.png"))

#variables
playerSpeed = 0
playerPos = [0, 0]
playerRotation = 0
playerRotationRad = playerRotation * pi / 180

raycastRange = 500

checkpoint = False

roadColor = pygame.Color(255, 255, 255, 255)
wallColor = pygame.Color(0, 0, 0, 255)
checkpointColor = pygame.Color(0, 162, 232, 255)
finishLineColor = pygame.Color(237, 28, 36, 255)


class car(pygame.sprite.Sprite):
    
    def __init__(self, position, rotation):
        global playerSprite

        pygame.sprite.Sprite.__init__(self)
        
        #variables referenceable outside
        #image and rect required by pygame to render
        self.image = playerSprite
        self.rect = playerSprite.get_rect(center = playerSprite.get_rect(center = position).center)

        global lapTimer
        lapTimer.tick()

        global playerSpeed
        global playerPos
        global playerRotation
        global playerRotationRad
        playerSpeed = 0
        playerPos = position
        playerRotation = rotation
        playerRotationRad = rotation * pi / 180

    def updateMovement(self, keysPressed, deltaT):
        global playerTopSpeed
        global playerAcceleration
        global playerTurnSpeed
        global playerDeadzoneSpeed

        global playerSpeed
        global playerPos
        global playerRotation
        global playerRotationRad

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

        self.image = pygame.transform.rotate(playerSprite, playerRotation)
        self.rect = self.image.get_rect(center = playerSprite.get_rect(center = (0, 0)).center)

        self.rect.move_ip(playerPos)


        #playerPos[0] += (playerMovement[3] - playerMovement[2]) * playerTopSpeed

    def checkStatus(self, map):
        global lapTimer
        global checkpoint
        
        playerPixel = colorAtPos(map, playerPos)
        if(playerPixel != roadColor):
            #if crashed, return false, else return true as in alive
            
            if playerPixel == finishLineColor and checkpoint:
                lapTimer.tick()
                checkpoint = False
                return ['finish', lapTimer.get_time()/1000]
            
            if playerPixel == wallColor:
                return ['crash', 0]

            if playerPixel == checkpointColor:
                checkpoint = True
            
        return ['', 0]

    def drawRay(self, display, map):
        rays = []
    
        for x in [pi/2, pi/4, 0, -pi/4, -pi/2]:
            rays.append([display, (255,0,0), playerPos, (playerPos[0] - raycastDistance(map, playerPos, playerRotationRad + x) * math.sin(playerRotationRad + x), playerPos[1] - raycastDistance(map, playerPos, playerRotationRad + x) * math.cos(playerRotationRad + x)), 2])
        
        return rays

    def status(self, status):
        global playerTopSpeed
        global playerSpeed
        if status:
            playerTopSpeed = 1
        if not status:
            playerTopSpeed = 0
            playerSpeed = 0


def raycastDistance(map, currentPosition, angle):
    counter = 0
    rayPos = currentPosition[:]

    while(counter < raycastRange):
        rayPos[0] += math.sin(-angle)
        rayPos[1] -= math.cos(-angle)

        if(colorAtPos(map, rayPos) == wallColor):
            return math.sqrt((currentPosition[0] - rayPos[0])**2 + (currentPosition[1] - rayPos[1])**2)

        counter += 1
        
    return raycastRange

def colorAtPos(map, position):
    return map.get_at([round(coord) for coord in position])
        