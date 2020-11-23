import pygame
import neat
import time
import os
import math
import pickle

#I don't believe that these values can be very dynamic, since the .pngs aren't being scaled to fit the resolution
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
		self.ySpeed = 2
		self.xSpeed = -16
		self.angle = math.radians(360)
		self.thrust = 0.03
		self.gravity = 0.25
		self.index = 1
		self.rocket_thruster_off = ROCKET_IMGS[1]
		self.img = ROCKET_IMGS[1]
		self.flag = False
		#self.clamp = 0


	def rotateLeft(self):
		#180 = min angle, could store this in a variable, but don't want to add an int to
		#each ship since it feels like some memory usage that could be avoidable, in the cost
		#of a code that's a bit less readable and more hard-coded (I'm not that happy about it, but whatever)
		if math.degrees(self.angle) <=180:
			self.angle = math.radians(180)
		else:
			self.angle-= math.pi/20


	def rotateRight(self):
		#360 = max angle, same about the "rotateLeft" function
		if math.degrees(self.angle) >=360:
			self.angle = math.radians(360)
		else:
			self.angle+= math.pi/20


	def thrusting(self):
		if self.fuel>0:
			self.fuel-=1
			self.xSpeed += math.degrees(math.cos(self.angle)) * self.thrust
			self.ySpeed += math.degrees(math.sin(self.angle)) * self.thrust
			self.img = ROCKET_IMGS[0]
			self.index = 0
			self.flag = True		

	def update(self):

		#Updating the rocket sprite when the "thrusting" function hasn't been called for more than 1 frame
		if self.flag == True:
			self.flag = False
		else:
			self.img = ROCKET_IMGS[1]
			self.index = 1

		#Clamp the rotation if the limiter on both "rotateLeft" and "rotateRight" aren't present
		#
		#Created the limiter to better "emulate" the original game
		"""
		if math.degrees(self.angle) > 360:
			self.angle -= 2*math.pi
			self.clamp+=1
		elif math.degrees(self.angle) < 0:
			self.angle += 2*math.pi
			self.clamp+=1
		"""

		self.ySpeed += self.gravity

		#applying the xSpeed/ySpeed to the x and y coords
		self.x += self.xSpeed * 0.8
		self.y += self.ySpeed


	def draw(self,win):

		rotated_image = pygame.transform.rotate(self.img,-math.degrees(self.angle))
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
		win.blit(rotated_image,new_rect.topleft)


	def get_mask(self):
		return pygame.mask.from_surface(self.rocket_thruster_off)


	def collide(self,floor):
		if self.index == 0:
			self.img = ROCKET_IMGS[1]

		ship_mask = self.get_mask()
		floor_mask = floor.get_mask()

		floor_offset = (floor.x - round(self.x), floor.y - round(self.y))
		ship_offset = (round(self.x) - floor.x, round(self.y) - floor.y)

		result3 = floor_mask.overlap(ship_mask,ship_offset)
		result5 = ship_mask.overlap(floor_mask,floor_offset)

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

		if ship.index == 0:
			ship.img = ROCKET_IMGS[0]
		if result3 or result5:
			return True

		return False

	
	def draw(self,win):
		win.blit(self.img,[self.x, self.y])


def draw_window(win,ships,base,background):
	win.blit(BACKGROUND,(0,0))
	base.draw(win)

	for ship in ships:
		ship.draw(win)

	pygame.display.update()

#Main "game" function, closes and opens the pygame window, so it's not IDEAL.
#I'll do it differently next time
def eval_genomes(genomes,config):
	#Change 'genomes' to 'g' while displaying the winner
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	floor = Floor(0,750)
	clock = pygame.time.Clock()
	run = True

	nets = []
	ge = []
	ships = []

	#_ is used to skip the genome's id, which won't be used here
	#Comment line below and shift+tab the lines indented while displaying the winner
	for _, g in genomes:
		#creates the ship, the neural network and the genome(ge)
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		ships.append(Ship(WIN_WIDTH/2 - ROCKET_IMGS[1].get_width()/2,80))
		g.fitness = 0
		ge.append(g)

	while run:
		clock.tick(90)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				#activated if "X" is pressed on the game window
				#abruptly closes the game
				run = False
				pygame.quit()
				quit()
		if(len(ships)==0):
			run = False
			break

		for x,ship in enumerate(ships):
			ship.update()

			#what the ship knows about the environment
			output = nets[x].activate((ship.y,ship.x,ship.ySpeed,ship.xSpeed,math.degrees(ship.angle),ge[x].fitness))

			"""
			If the neural net (the line of code above (nets[x].activate)) decided that, given the inputs,
			( --ship.y,ship.x[...]math.degrees(ship.angle)-- ) 
			it feels inclined to do something or not, the output can vary from -1 to 1 (float).
			So doing something if the output is > 0.5 is basically making the threshold of +75%
			(which feels kinda high IMO), but I'm still testing these numbers.
			"""
			if output[0] > 0.6:
				ship.thrusting()
			if output[1] > 0.6 and output[1] > output[2]:
				ship.rotateLeft()
			elif output[2] > 0.6:
				ship.rotateRight()
		
		#Fitness manipulation
		for x,ship in enumerate(ships):
			#Huge thanks to github.com/patetico for some neat *haha* ideas
			ge[x].fitness+= 10 - math.sqrt(abs(270-math.degrees(ship.angle)))
			if ship.ySpeed > 0:
				ge[x].fitness-=ship.ySpeed
			if ship.x + ROCKET_IMGS[1].get_width() > WIN_WIDTH or ship.x < 0 or ship.y < 0:
				ge[x].fitness -= 8000
				ships.pop(x)
				nets.pop(x)
				ge.pop(x)
			elif ship.collide(floor):
				if math.degrees(ship.angle) >=267 and math.degrees(ship.angle) <=273:
					ge[x].fitness += 800
				elif math.degrees(ship.angle) >=260 and math.degrees(ship.angle) <=280:
					ge[x].fitness += 30
				if abs(ship.xSpeed) < 1:
					ge[x].fitness += 15
				if ship.ySpeed < 1:
					ge[x].fitness += 200
				ships.pop(x)
				nets.pop(x)
				ge.pop(x)

			

		draw_window(win,ships,floor,BACKGROUND)

def showBestGenome(genomes,config):
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	floor = Floor(0,750)
	clock = pygame.time.Clock()
	run = True
	nets = []
	ge = []
	ships = []
	net = neat.nn.FeedForwardNetwork.create(genomes, config)
	nets.append(net)
	ships.append(Ship(WIN_WIDTH/2 - ROCKET_IMGS[1].get_width()/2,80))
	genomes.fitness = 0
	ge.append(genomes)
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
		if(len(ships)==0):
			run = False
			break
		for x,ship in enumerate(ships):
			ship.update()
			output = nets[x].activate((ship.y,ship.x,ship.ySpeed,ship.xSpeed,math.degrees(ship.angle),ge[x].fitness))
			if output[0] > 0.5:
				ship.thrusting()
			if output[1] > 0.5 and output[1] > output[2]:
				ship.rotateLeft()
			elif output[2] > 0.5:
				ship.rotateRight()
		for x,ship in enumerate(ships):
			if ship.x + ROCKET_IMGS[1].get_width() > WIN_WIDTH or ship.x < 0 or ship.y < 0 or ship.collide(floor):
				ships.pop(x)
				nets.pop(x)
				ge.pop(x)
		draw_window(win,ships,floor,BACKGROUND)


#----------------------------------Neat Config---------------------------------------------------
def run(config_path):

	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
		neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

	#Generates Population using the config file set previously
	p = neat.Population(config)

	#Optional output in the console about the details of each generation
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	
	

	#We should call 'BLOCK 1' to train the rockets and then save the best one on a file
	#We should call 'BLOCK 2' to display only the best rocket

	#BLOCK 1
	#"""
	#'50' are how many generations are going to be run	
	winner = p.run(eval_genomes,150)
	pickle_out = open("neatRockets.pickle","wb")
	pickle.dump(winner,pickle_out)
	pickle_out.close()
	#"""

	#BLOCK 2
	"""
	pickle_in = open("neatRockets.pickle","rb")
	winner = pickle.load(pickle_in)
	showBestGenome(winner,config)
	"""

#This "if" calls the entire game
if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
