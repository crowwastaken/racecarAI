import pygame
import neat
import os
import math
from car import *
#from car2 import *

from math import pi



    
def run(neatConfig):
    neatPopulation = neat.population.Population(neatConfig)
    
    neatPopulation.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    neatPopulation.add_reporter(stats)
    neatPopulation.add_reporter(neat.Checkpointer(5))

    winner = neatPopulation.run(eval_genomes, 1)

#actual game
def eval_genomes(ge, config):
    width = 1920
    height = 900
    fps = 60

    playerSprite = pygame.image.load(os.path.join(localpath, "car.png"))
    map = pygame.image.load(os.path.join(localpath, "map.png"))
    mapRect = map.get_rect()

    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('racecar')

    #initialize and track each genome
    nets = []
    genomes = []
    playerList = pygame.sprite.Group()

    for id, genome in ge:
        genome.fitness = 0

        nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
        genomes.append(genome)
        playerList.add(car([200, 300], 0))


    #60 fps
    clock = pygame.time.Clock()
    deltaT = clock.tick(fps)

    #intialize player (human)
 #   player = car([200, 300], 0)
 #   playerList.add(player)

    quit = False
    drawRays = False

    while not quit:
        deltaT = clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYUP and event.key == pygame.K_r:
                drawRays = not drawRays



        #human controls
#        keysPressed = pygame.key.get_pressed()
#        input = [-(int(keysPressed[pygame.K_w]) - int(keysPressed[pygame.K_s])), (int(keysPressed[pygame.K_a]) - int(keysPressed[pygame.K_d]))]

        #update genomes
        for x, player in enumerate(playerList):
            inputs = nets[x].activate(player.rayDistances(map))
            roundedInputs = [round(a) for a in inputs]
            player.updateMovement(roundedInputs, deltaT)

            status = player.checkStatus(map)
            if(status[0] == 'finish'):
                print('finished a lap, time: ', status[1])
                genome[x].fitness += 50 + int(100/status[1])
                
            if(status[0] == 'checkpoint'):
                print('checkpoint achieved')
                genome[x].fitness += 5

            if(status[0] == 'crash'):
                print('crashed')
                
                #genome[x].fitness -= 1
                player.changeStatus(False)

                #nets.pop(x)
                #genomes.pop(x)
                #playerList.remove(player)
            
        survivingPlayerList = pygame.sprite.Group()
        survivingGenomes = []
        survivingNets = []

        for x, player in enumerate(playerList):
            if player.status == True:
                survivingPlayerList.add(player)
                survivingGenomes.append(genomes[x])
                survivingNets.append(nets[x])

        playerList = survivingPlayerList
        genomes = survivingGenomes
        nets = survivingNets


        #check current generation population
        if len(playerList) < 1:
            quit = True
            break

        #render goes bottom first, top last
        display.blit(map, mapRect)
        playerList.draw(display)
        if drawRays:
            for player in playerList:
                for ray in player.drawRay(display, map):
                    pygame.draw.line(display, ray[1], ray[2], ray[3], ray[4])
            
        pygame.display.update()
                
    pygame.quit()


if __name__ == "__main__":
    localpath = os.path.dirname(os.path.abspath(__file__))

    neatConfig = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, localpath + '/neatConfig.txt')
    run(neatConfig)