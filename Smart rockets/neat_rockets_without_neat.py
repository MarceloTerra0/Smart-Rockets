#JOGO NO ESTADO: JOGAVEL

import pygame
import neat
import time
import os
import random
import math

WIN_WIDTH = 1200
WIN_HEIGHT = 800

FLOOR = pygame.image.load(os.path.join("imgs","floor.png"))
BACKGROUND = pygame.image.load(os.path.join("imgs","background.jpg"))
ROCKET_IMGS = [pygame.image.load(os.path.join("imgs","rocket_original.png")),pygame.image.load(os.path.join("imgs","rocket_original_idle.png"))]

class Ship:

	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.fuel = 100
		self.ySpeed = 0
		self.xSpeed = 0
		self.angle = math.radians(0)
		self.thrust = 0.006
		self.gravidade = 0.1
		#0.1
		self.thrusting = False
		self.keys = [False, False, False, False]
		self.index = 1
		self.img = ROCKET_IMGS[1]



	def update(self):

		#Thrust speed based on sin and cos
		#
		#if w is pressed
		if self.keys[0]:
			self.xSpeed += math.degrees(math.cos(self.angle)) * self.thrust
			self.ySpeed += math.degrees(math.sin(self.angle)) * self.thrust
			self.img = ROCKET_IMGS[0]
			self.index = 0
		else:
			self.index = 1
			self.img = ROCKET_IMGS[1]
			#0 = up, 1 = left, 2= down, 3=right
		#Left then right
		if self.keys[1]:
			self.angle-= math.pi/60;

		elif self.keys[3]:
			self.angle+= math.pi/60;

		#Clamp the rotation
		if math.degrees(self.angle) > 360:
			self.angle -= 2*math.pi
		elif math.degrees(self.angle) < 0:
			self.angle += 2*math.pi
		
		#Gravity
		if self.ySpeed > 5:
			self.ySpeed = 5
		else:
			self.ySpeed += self.gravidade

		#applying the xSpeed/ySpeed to the x and y coords
		self.x += self.xSpeed * 0.8
		self.y += self.ySpeed

		print(math.degrees(self.angle))


	def draw(self,win):

		rotated_image = pygame.transform.rotate(self.img,-math.degrees(self.angle))
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
		win.blit(rotated_image,new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


	def collide(self,floor):
		if self.index == 0:
			self.img = ROCKET_IMGS[1]

		ship_mask = self.get_mask()
		floor_mask = floor.get_mask()

		floor_offset = (floor.x - round(self.x), floor.y - round(self.y))
		ship_offset = (round(self.x) - floor.x, round(self.y) - floor.y)

		result3 = floor_mask.overlap(ship_mask,ship_offset)
		result5 = ship_mask.overlap(floor_mask,floor_offset)


		#debug
		print(result3,result5)
		#print([round(ship.x),round(ship.y)],floor_offset, result)


		if self.index == 0:
			self.img = ROCKET_IMGS[0]
		if result3 or result5:
			return True

		return False

class Floor:

	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.img = FLOOR


	def get_mask(self):
		return pygame.mask.from_surface(self.img)


	def collide(self,ship):
		if ship.index == 0:
			ship.img = ROCKET_IMGS[1]

		ship_mask = ship.get_mask()
		floor_mask = self.get_mask()

		floor_offset = (self.x - round(ship.x), self.y - round(ship.y))
		ship_offset = (round(ship.x) - self.x, round(ship.y) - self.y)

		result3 = floor_mask.overlap(ship_mask,ship_offset)
		result5 = ship_mask.overlap(floor_mask,floor_offset)


		#debug
		print(result3,result5)
		#print([round(ship.x),round(ship.y)],floor_offset, result)


		if ship.index == 0:
			ship.img = ROCKET_IMGS[0]
		if result3 or result5:
			return True

		return False

	


	def draw(self,win):
		win.blit(self.img,[self.x, self.y])


def draw_window(win,ship,base,background):
	win.blit(BACKGROUND,(0,0))

	ship.draw(win)
	base.draw(win)
	ship.draw(win)
	pygame.display.update()

def main():
	
	ship = Ship(WIN_WIDTH/2 - ROCKET_IMGS[1].get_width()/2,100)
	floor = Floor(0,750)
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))


	clock = pygame.time.Clock()
	run = True

	
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				#activated if "X" is pressed on the game window
				#abruptly closes the game
				run = False
				pygame.quit()
				quit()

			if event.type == pygame.KEYDOWN:
				if event.key==pygame.K_UP:
					ship.keys[0]=True
				if event.key==pygame.K_LEFT:
					ship.keys[1]=True
				if event.key==pygame.K_DOWN:
					ship.keys[2]=True
				if event.key==pygame.K_RIGHT:
					ship.keys[3]=True

			if event.type == pygame.KEYUP:
				if event.key==pygame.K_UP:
					ship.keys[0]=False
				if event.key==pygame.K_LEFT:
					ship.keys[1]=False
				if event.key==pygame.K_DOWN:
					ship.keys[2]=False
				if event.key==pygame.K_RIGHT:
					ship.keys[3]=False

		ship.collide(floor)
		ship.update()
		draw_window(win,ship,floor,BACKGROUND)

		

main()


def eval_genomes(genomes, config):

	nets = []
	ge = []
	ships = []

	#_, is used to ignore the first thingy that's created in "genomes" (useless,g)
	#well, not useless, but not used here
	for _, g in genomes:
		#creates the bird, the neural network and the genome(ge)
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230,350))
		g.fitness = 0
		ge.append(g)



#----------------------------------Neat Config---------------------------------------------------
def run(config_path):
	#picke pode ser usado para salvar

	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
		neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

	#Generates Population using the config file set previously
	p = neat.Population(config)

	#Optional output in the console about the details of each generation
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)


	#50 is how many generations are going to be run
	#
	#p.run is a function that belongs to neat-python!
	#(p is an object created by the neat function
	#so when using "p.run" we are using a function
	#that belongs to the neat lib)
	#winner = p.run(eval_genomes,50)

#This "if" calls the entire game
if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	#run(config_path)