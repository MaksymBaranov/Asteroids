import pygame
import sys
from random import randint, uniform


class Ship(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)
		self.image = pygame.image.load('graphics/ship.png').convert_alpha()
		self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
		self.mask = pygame.mask.from_surface(self.image)
		self.laser_sound = pygame.mixer.Sound('sounds/laser.ogg')

		# Timer
		self.can_shoot = True
		self.shoot_time = None

	def input_position(self):
		pos = pygame.mouse.get_pos()
		self.rect.center = pos

	def laser_timer(self):
		if not self.can_shoot:
			current_time = pygame.time.get_ticks()
			if current_time - self.shoot_time > 500:
				self.can_shoot = True

	def laser_shoot(self):
		if pygame.mouse.get_pressed()[0] and self.can_shoot:
			self.can_shoot = False
			self.shoot_time = pygame.time.get_ticks()

			Laser(self.rect.midtop, laser_group)
			self.laser_sound.play()

	def meteor_collision(self):
		if pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask):
			pygame.quit()
			sys.exit()

	def update(self):
		self.laser_timer()
		self.input_position()
		self.laser_shoot()
		self.meteor_collision()


class Laser(pygame.sprite.Sprite):
	def __init__(self, position, groups):
		super().__init__(groups)
		self.image = pygame.image.load('graphics/laser.png').convert_alpha()
		self.rect = self.image.get_rect(midbottom=position)
		self.mask = pygame.mask.from_surface(self.image)
		self.explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')

		# Float based position
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2(0, -1)
		self.speed = 600

	def meteor_collision(self):
		if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
			self.explosion_sound.play()
			self.kill()

	def update(self):
		self.pos += self.direction * self.speed * dt
		self.rect.topleft = (round(self.pos.x), round(self.pos.y))

		if self.rect.bottom < 0:
			self.kill()

		self.meteor_collision()


class Meteor(pygame.sprite.Sprite):
	def __init__(self, position, groups):

		# Badic setup
		super().__init__(groups)
		meteor_surf = pygame.image.load('graphics/meteor.png').convert_alpha()
		meteor_size = pygame.math.Vector2(meteor_surf.get_size()) * uniform(0.5, 2)
		self.scaled_surf = pygame.transform.scale(meteor_surf, meteor_size)
		self.image = self.scaled_surf
		self.rect = self.image.get_rect(center=position)
		self.mask = pygame.mask.from_surface(self.image)

		# Float based positioning
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
		self.speed = randint(400, 600)

		# Rotation logic
		self.rotation = 0
		self.rotation_speed = randint(20, 50)

	def rotate(self):
		self.rotation += self.rotation_speed * dt
		rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
		self.image = rotated_surf
		self.rect = self.image.get_rect(center=self.rect.center)
		self.mask = pygame.mask.from_surface(self.image)

	def update(self):
		self.pos += self.direction * self.speed * dt
		self.rect.topleft = (round(self.pos.x), round(self.pos.y))
		self.rotate()
		if self.rect.top > WINDOW_HEIGHT:
			self.kill()


class Score:
	def __init__(self):
		self.font = pygame.font.Font('graphics/subatomic.ttf', 50)

	def display(self):
		score_text = f'Score: {pygame.time.get_ticks() // 1000}'
		text_surf = self.font.render(score_text, True, (255, 255, 255))
		text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
		display_surf.blit(text_surf, text_rect)
		pygame.draw.rect(display_surf, (255, 255, 255), text_rect.inflate(30, 30), width=8, border_radius=5)


# Basic setup
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Asteroid shooter')
clock = pygame.time.Clock()
pygame.init()

# Background
background_surf = pygame.image.load('graphics/background.png').convert_alpha()

# Music
bg_music = pygame.mixer.Sound('sounds/music.wav')
bg_music.play(loops=-1)

# Sprite groups
space_ship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# Sprite creation
ship = Ship(space_ship_group)

# Score
score = Score()

# Timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 200)

# Game loop
while True:
	# Event loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		if event.type == meteor_timer:
			meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
			meteor_y_pos = randint(-150, -50)
			Meteor((meteor_x_pos, meteor_y_pos), meteor_group)

	# Delta time
	dt = clock.tick() / 1000

	# Background
	display_surf.blit(background_surf, (0, 0))

	# Update
	space_ship_group.update()
	laser_group.update()
	meteor_group.update()

	# Score
	score.display()

	# Graphics
	space_ship_group.draw(display_surf)
	laser_group.draw(display_surf)
	meteor_group.draw(display_surf)

	# Draw the frame
	pygame.display.update()
