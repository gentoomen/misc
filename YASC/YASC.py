#!/usr/bin/python
# ===========================================================================
#
# YASC - YASC is another spacewars clone
#
# Version: BETA 0.1
# Requires: pygame
# Mon fromage: :/
#
# TODO: * Fix wierd initial collision when starting loop
#       * Port to LayeredDirty from RenderUpdates
#       * Make a Game class that will handle game loop
# ===========================================================================

import pygame
from pygame.locals import *
import sys, math, os
global_sprite_list = pygame.sprite.RenderUpdates()
gravity_sprite_list = pygame.sprite.RenderUpdates()
screen_size = (1024, 768)
def Load_pic(name):
    """ Wrapper function for pygame.image.load.
        Takes image name as argument, returns pygame.surface and pygame.rect """
    fullname = os.path.join('./', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        raise SystemExit, message
    return image, image.get_rect()

class Physics(object):

    G = 6.67428 * math.pow(10.0, -11.0)

    def Turn(self):
        """ Calculate new angle = vector[0] """
        self.vector[0] += self.turn
        if self.vector[0] >= 360: self.vector[0] = self.vector[0] - 360
        if self.vector[0] < 0: self.vector[0] = self.vector[0] + 360

    def Accelerate(self):
        """ Calculate new velocity = [dx,dy] from vector = [angle, thrust] """
        # a = F/m
        acceleration = self.vector[1] / self.mass
        rad_angle = math.radians(self.vector[0])
        self.velocity = [self.velocity[0] + ( acceleration * math.cos(rad_angle) ), self.velocity[1] + ( acceleration * math.sin(rad_angle) )]

    def Wrap(self):
        """ Wrap around edges, mutually exclusive with Bounce """
        #Wrapping using rect collision techniques is another approach
        if (self.position[0] - ( self.rect.width / 2 ) < 0):
            self.position[0] += screen_size[0]
        elif (self.position[0] + ( self.rect.width / 2 ) > screen_size[0]):
            self.position [0] -= screen_size[0]
        if (self.position[1] + ( self.rect.width / 2 ) < 0):
            self.position[1] += screen_size[1]
        elif (self.position[1] + ( self.rect.width / 2 ) > screen_size[1]):
            self.position[1] -= screen_size[1]

    def Bounce(self):
        """ Bounce from walls, mutually exclusive with Wrap """
        bouncy = 0.90  #slowing effect of bounce
        if ( self.position[0] - ( self.rect.width / 2 ) < 0):
            self.position[0] = 0 + ( self.rect.width / 2 )
            self.velocity[0] = -self.velocity[0] * bouncy
        elif (self.position[0] + ( self.rect.width / 2 ) > screen_size[0]):
            self.position[0] = screen_size[0] - ( self.rect.width / 2 )
            self.velocity[0] = -self.velocity[0] * bouncy
        if (self.position[1] - ( self.rect.height / 2 ) < 0):
            self.position[1] = 0 + ( self.rect.height / 2 )
            self.velocity[1] = -self.velocity[1] * bouncy
        elif (self.position[1] + ( self.rect.height / 2 ) > screen_size[1]):
            self.position[1] = screen_size[1] - ( self.rect.height / 2 )
            self.velocity[1] = -self.velocity[1] * bouncy

    def Gravity(self, obj2):
        """ Apply gravity, modifies self.velocity, obj2 is not modified"""
        (diffx, diffy) = (self.position[0] - obj2.position[0], self.position[1] - obj2.position[1])
        distance = math.sqrt(( diffx**2 ) + ( diffy**2 ))
        if distance < 10: distance = 10
        force = self.G * ( self.mass * obj2.mass ) / ( distance**2 )
        acceleration = force / self.mass
        xmod = ( diffx / distance ) * acceleration
        ymod = ( diffy / distance ) * acceleration
        self.velocity[0] -= xmod
        self.velocity[1] -= ymod

    def CollisionDetect(self):
        """ Collision detection using pygame.spritegroup methods """
        for obj2 in pygame.sprite.spritecollide(self, global_sprite_list, False, pygame.sprite.collide_rect_ratio(0.8)):
            #if cmp(self,obj2): # if obj != obj2
            if self != obj2:
                print self
                print obj2
                self.GoBang(obj2)
                obj2.GoBang(self)

    def Move(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def DUpdate(self):
        """ Update wrapper for all Physics.methods, used for testing """
        for obj2 in global_sprite_list:
                if self != obj2: self.Gravity(obj2)
        try: self.Turn()
        except: pass
        try: self.Accelerate()
        except: pass
        #self.Wrap()
        self.Bounce()
        self.CollisionDetect()

    def Gupdate(self):
        """ Gravity batch update for instance """
        for obj2 in gravity_sprite_list:
            if self != obj2: self.Gravity(obj2)

class Entity(pygame.sprite.Sprite, Physics):
    """ . """

    def __init__(self, entity_id, image, position, mass, vector, velocity, turn_value, wall_type, gravity_bit):
        """ constructor """
        pygame.sprite.Sprite.__init__(self)
        global_sprite_list.add(self)
        self.sprite_list = pygame.sprite.RenderUpdates(self)
        self.entity_id = entity_id #ie. player id
        self.image, self.rect = Load_pic(image)
        self.base_image = self.image #let's keep a copy of the orginal
        self.position = position
        self.mass = mass
        self.vector = vector
        self.velocity = velocity

        self.burn = False

        self.turn = 0
        self.right = False
        self.left = False

        self.turn_value = 1.5

        #Wrap or Bounce or Vanish(missing currently)
        if wall_type.lower() == "wrap": self.wall = self.Wrap
        elif wall_type.lower() == "bounce": self.wall = self.Bounce
        #elif lower(wall_type) == "vanish": self.wall = Vanish
        else: self.wall = Bounce

        #0 None, 1 = affects others, 2 = is affected by, 3 = both
        if gravity_bit == 3:
            self.gravity == True
            gravity_sprite_list.add(self)
        elif gravity_bit == 2:
            self.gravity = True
        elif gravity_bit == 1:
            self.gravity = False
            gravity_sprite_list.add(self)
        else:
            self.gravity = False

#        self.mouse_pos = (0,0)

    def ToggleLeft(self):
        """ Toggles turn *correctly* """
        if self.left:
            self.left = False
            if self.right: self.turn = self.turn_value
            else: self.turn = 0
        else:
            self.left = True
            self.turn = -self.turn_value
    def ToggleRight(self):
        if self.right:
            self.right = False
            if self.left: self.turn = -self.turn_value
            else: self.turn = 0
        else:
            self.right = True
            self.turn = self.turn_value

    def ToggleBurn(self):

        if self.burn: self.burn = False
        else: self.burn = True
        print self.burn
    def update(self):
        """ Update position, orientation """
        #self.Physics.DUpdate(self)
        if self.gravity:
            self.Gupdate()
        if self.turn != 0:
            self.Turn()
            self.image = pygame.transform.rotate(self.base_image, 360 - self.vector[0])
            self.rect = self.image.get_rect()
        if self.burn:
            self.Accelerate()
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        if self.wall: self.wall()
        self.CollisionDetect()

        self.rect.center = self.position

    def GoBang(self, collided_obj):
        """ Destructor """
        print "Global GoBangy, so BANG"

class Ship(Entity):

    def __init__(self,
                entity_id = 1,
                image = 'v_b.png',
                position = [100, 100],
                mass = 800.0,
                vector = [0.0, 30.0],
                velocity = [0.0, 0.0],
                turn_value = 1.5,
                wall_type = "bounce",
                gravity_bit = 2
                ):
        Entity.__init__(self, entity_id, image, position, mass, vector, velocity, turn_value, wall_type, gravity_bit)
        self.missiles = 9

    def Shoot(self):
        if self.missiles > 0:
            p_x, p_y = self.position
            m_angle = self.vector[0]
            v_x, v_y = self.velocity
            self.sprite_list.add(Entity(self.entity_id, 'missile_1b.png', [p_x,p_y], 80.0, [m_angle, 1.0], [v_x,v_y], 0, "wrap",2))
            self.missiles -= 1

class CelestialBody(Entity):
    def __init__(self,
                entity_id = 0,
                image = 'earth.png',
                position = [screen_size[0] / 2, screen_size[1] / 2],
                mass = 5973600000000,
                vector = [0, 0],
                velocity = [0, 0],
                turn_value = 0,
                wall_type = "bounce",
                gravity_bit = 1
                ):
        Entity.__init__(self, entity_id, image, position, mass, vector, velocity, turn_value, wall_type, gravity_bit)



pygame.init()

screen = pygame.display.set_mode(screen_size)
background = pygame.Surface(screen_size).convert()
background, backgroundRect = Load_pic('milkyway-2.jpg')
#background.fill((0, 0, 0))
screen.blit(background, backgroundRect)
pygame.display.flip()
clock = pygame.time.Clock()

player_1 = Ship(1, 'shiptest2.png')
earth = CelestialBody('earth.png')
running = True
while running:
    for event in pygame.event.get():
        #player_1.mouse_pos = pygame.mouse.get_pos()
        #print event
        if (event.type == KEYDOWN):
            if (event.key == K_ESCAPE): running = False
            if (event.key == K_LEFT): player_1.ToggleLeft()
            elif (event.key == K_RIGHT): player_1.ToggleRight()
            if (event.key == K_UP): player_1.ToggleBurn()
            if event.key == K_RETURN: player_1.Shoot()
        if (event.type == KEYUP):
            if (event.key == K_LEFT): player_1.ToggleLeft()
            elif (event.key == K_RIGHT): player_1.ToggleRight()
            if (event.key == K_UP): player_1.ToggleBurn()


    global_sprite_list.update()
    global_sprite_list.clear(screen, background)

    changes = global_sprite_list.draw(screen)
    pygame.display.update(changes)
    clock.tick(120)
