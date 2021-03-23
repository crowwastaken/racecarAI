import pygame
import os
import math

from math import pi

localpath = os.path.dirname(os.path.abspath(__file__))

#constants
playerTopSpeed = 1
playerAcceleration = 0.01
playerTurnSpeed = 0.4
playerDeadzoneSpeed = 0.05
raycastRange = 500

playerSprite = pygame.image.load(os.path.join(localpath, "car.png"))





roadColor = pygame.Color(255, 255, 255, 255)
wallColor = pygame.Color(0, 0, 0, 255)
checkpoint1Color = pygame.Color(34, 177, 76, 255)
checkpoint2Color = pygame.Color(0, 162, 232, 255)
checkpoint3Color = pygame.Color(63, 72, 204, 255)
finishLineColor = pygame.Color(237, 28, 36, 255)


class car(pygame.sprite.Sprite):
    
    def __init__(self, position, rotation):
        global playerSprite

        pygame.sprite.Sprite.__init__(self)
        
        #variables referenceable outside
        #image and rect required by pygame to render
        self.image = playerSprite
        self.rect = playerSprite.get_rect(center = playerSprite.get_rect(center = position).center)

        #variables
        self.playerSpeed = 0
        self.playerPos = position
        self.playerRotation = 0
        self.playerRotationRad = self.playerRotation * pi / 180

        self.checkpoint1 = False
        self.checkpoint2 = False
        self.checkpoint3 = False

        self.lapTimer = pygame.time.Clock()
        self.lapTimer.tick()

        self.playerSpeed = 0
        self.playerPos = position
        self.playerRotation = rotation
        self.playerRotationRad = rotation * pi / 180

    def updateMovement(self, input, deltaT):
        global playerTopSpeed
        global playerAcceleration
        global playerTurnSpeed
        global playerDeadzoneSpeed

        #input values are forward & back, and left & right
        forwardBackward = input[0]
        leftRight = input[1]
        
        #not accelerating
        if forwardBackward == 0 and self.playerSpeed != 0:
            self.playerSpeed += playerAcceleration * (int(self.playerSpeed < 0) * 2 - 1) / 5

        #set deadzone
        if abs(self.playerSpeed) < playerDeadzoneSpeed and forwardBackward == 0:
            self.playerSpeed = 0

        #acceleration
        if forwardBackward != 0 and abs(self.playerSpeed) < playerTopSpeed:
            #accelerating
            braking = 1 # not braking
            if int(forwardBackward > 0) != int(self.playerSpeed > 0): # braking
                braking = 2
            self.playerSpeed += forwardBackward * playerAcceleration * braking


        #turn influence is a turningspeed variable affected by playerspeed
        if self.playerSpeed == 0:
            turnInfluence = 0
        else:
            turnInfluence = 1 / abs(self.playerSpeed)
            if turnInfluence > playerTurnSpeed:
                turnInfluence = playerTurnSpeed
        self.playerRotation += leftRight * playerTurnSpeed * turnInfluence * (int(self.playerSpeed < 0) * 2 - 1) * deltaT
        self.playerRotationRad = self.playerRotation * pi / 180

        self.playerPos[0] += math.sin(self.playerRotationRad) * self.playerSpeed * deltaT
        self.playerPos[1] += math.cos(self.playerRotationRad) * self.playerSpeed * deltaT

        self.status = True

        self.image = pygame.transform.rotate(playerSprite, self.playerRotation)
        self.rect = self.image.get_rect(center = playerSprite.get_rect(center = (0, 0)).center)

        self.rect.move_ip(self.playerPos)


        #playerPos[0] += (playerMovement[3] - playerMovement[2]) * playerTopSpeed

    def checkStatus(self, map):
        
        playerPixel = colorAtPos(map, self.playerPos)
        if(playerPixel != roadColor):
            #if crashed, return false, else return true as in alive
            
            if playerPixel == finishLineColor and self.checkpoint1 and self.checkpoint2 and self.checkpoint3:
                self.lapTimer.tick()
                self.checkpoint1 = False
                self.checkpoint2 = False
                self.checkpoint3 = False
                return ['finish', lapTimer.get_time()/1000]
            
            if playerPixel == wallColor:
                return ['crash', 0]

            if playerPixel == checkpoint1Color and not self.checkpoint1:
                self.checkpoint1 = True
                return ['checkpoint', 0]

            #must be successive, thus check previous checkpoints
            if playerPixel == checkpoint2Color and not self.checkpoint2 and self.checkpoint1:
                self.checkpoint2 = True
                return ['checkpoint', 0]

            if playerPixel == checkpoint3Color and not self.checkpoint3 and self.checkpoint1 and self.checkpoint2:
                self.checkpoint3 = True
                return ['checkpoint', 0]
            
        return ['', 0]

    def rayDistances(self, map):
        distances = []

        for r in [pi/2, pi/4, 0, -pi/4, -pi/2]:
            x = raycastDistance(map, self.playerPos, self.playerRotationRad + r) * math.sin(self.playerRotationRad + r)
            y = raycastDistance(map, self.playerPos, self.playerRotationRad + r) * math.cos(self.playerRotationRad + r)
            distances.append(math.sqrt(x**2 + y**2))

        return distances

    def drawRay(self, display, map):
        rays = []
    
        for x in [pi/2, pi/4, 0, -pi/4, -pi/2]:
            rays.append([display, (255,0,0), playerPos, (playerPos[0] - raycastDistance(map, playerPos, playerRotationRad + x) * math.sin(playerRotationRad + x), playerPos[1] - raycastDistance(map, playerPos, playerRotationRad + x) * math.cos(playerRotationRad + x)), 2])
        
        return rays

    def changeStatus(self, status):
        if not status:
            self.playerSpeed = 0
            self.status = False


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
    for p in position:
        if p < 0:
            return roadColor
    return map.get_at([round(coord) for coord in position])
        