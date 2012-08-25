import pygame as pg
import pymunk as pm

from conf import conf
from util import ir


class Obj (object):
    def __init__ (self, level, pos, radius, mass, layers):
        self.level = level
        self.radius = radius # TODO: rm
        self.mass = mass
        self.body = b = pm.Body(mass, pm.moment_for_circle(mass, 0, radius))
        b.position = pos
        b.elasticity = conf.ELAST
        self.shape = s = pm.Circle(b, radius)
        s.friction = conf.FRICTION
        s.layers = conf.MAIN_LAYER | layers
        level.space.add(b, s)
        self.angle = 0

    def update (self):
        # damp movement
        self.body.velocity *= conf.MOVE_FRICTION
        self.body.angular_velocity *= conf.ROTATE_FRICTION

    def draw (self, screen):
        x, y = self.body.position
        pg.draw.circle(screen, (255, 0, 0), (ir(x), ir(y)), self.radius)


class Player (Obj):
    def __init__ (self, level, pos):
        Obj.__init__(self, level, pos, conf.PLAYER_SIZE, conf.PLAYER_MASS,
                     conf.PLAYER_LAYER)
        self.to_move = [0, 0]

    def move (self, dirn):
        self.to_move[dirn % 2] += 1 if dirn >= 2 else -1

    def update (self):
        Obj.update(self)
        ax, ay = self.to_move
        self.to_move = [0, 0]
        # normalise impulse
        a = (ax * ax + ay * ay) ** .5
        if a != 0:
            ax /= a
            ay /= a
            # apply impulse
            r = conf.PLAYER_SPEED
            self.body.apply_impulse((ax * r, ay * r))
