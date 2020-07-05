#JOGO NO ESTADO: JOGAVEL

import pygame
import time
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
		self.thrusting = False
		self.keys = [False, False, False, False]
		self.index = 1
		self.img = ROCKET_IMGS[1]


	def update(self):

		#Thrust speed based on sin and cos
		#
		#if up is pressed
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

			#This chunk of code makes me want to commit /quit_life
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
