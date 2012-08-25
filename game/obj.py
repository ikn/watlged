from math import cos, sin, atan2, pi

import pygame as pg
import pymunk as pm

from conf import conf
from util import ir
from ext import evthandler as eh


class Obj (object):
    def __init__ (self, level, pos, radius, mass, layers):
        self.level = level
        self.radius = radius
        self.mass = mass
        self.body = b = pm.Body(mass, pm.moment_for_circle(mass, 0, radius))
        b.position = pos
        b.elasticity = conf.ELAST
        self.shape = s = pm.Circle(b, radius)
        s.friction = conf.FRICTION
        s.layers = conf.MAIN_LAYER | layers
        level.space.add(b, s)
        self.angle = 0
        self.health = self.max_health

    def hit (self, damage):
        self.health -= self.shoot_d
        if self.health <= 0:
            self.die()

    def update (self):
        # damp movement
        self.body.velocity *= conf.MOVE_FRICTION
        self.body.angular_velocity *= conf.ROTATE_FRICTION

    def draw (self, screen):
        x, y = self.body.position
        pg.draw.circle(screen, (255, 0, 0), (ir(x), ir(y)), self.radius)
        a = self.angle
        length = 1.5 * self.radius
        end = (x + length * cos(a), y + length * sin(a))
        pg.draw.line(screen, (0, 0, 255), (x, y), end)


class Player (Obj):
    def __init__ (self, level, pos, scheme):
        # initial properties
        self.shoot_r = conf.SHOOT_RANGE
        self.shoot_d = conf.SHOOT_DAMAGE
        self.max_health = conf.PLAYER_HEALTH
        Obj.__init__(self, level, pos, conf.PLAYER_SIZE, conf.PLAYER_MASS,
                     conf.PLAYER_LAYER)
        self.to_move = [0, 0]
        (move_t, move_i), self.aim_scheme, (shoot_t, shoot_i) = scheme
        self.shoot_scheme = shoot_t
        l_eh = level.event_handler
        if move_t == 'kb':
            l_eh.add_key_handlers([
                (ks, [(self.move, (i,))], eh.MODE_HELD)
                for i, ks in enumerate(conf.KEYS_MOVE[move_i])
            ])
        else:
            raise ValueError('invalid move scheme: {0}'.format(move_t))
        if self.aim_scheme == 'move':
            self.target_angle = self.angle
        if shoot_t == 'kb':
            l_eh.add_key_handlers([
                (conf.KEYS_SHOOT[shoot_i], self.shoot, eh.MODE_ONDOWN),
                (conf.KEYS_SHOOT[shoot_i], self.shoot, eh.MODE_HELD)
            ])
        elif shoot_t == 'click':
            self.shoot_btns = shoot_i
            self.mouse_down = set()
            l_eh.add_event_handlers({
                pg.MOUSEBUTTONDOWN: self.click,
                pg.MOUSEBUTTONUP: self.click,
            })
        else:
            raise ValueError('invalid shoot scheme: {0}'.format(shoot_t))

    def move (self, key, mode, mods, dirn):
        self.to_move[dirn % 2] += 1 if dirn >= 2 else -1

    def click (self, evt):
        if evt.button in self.shoot_btns:
            md = self.mouse_down
            f = md.add if evt.type == pg.MOUSEBUTTONDOWN else md.remove
            f(evt.button)

    def shoot (self, *args):
        self.level.shoot(self.body.position, self.angle, self.shoot_r,
                         self.shoot_d, self)

    def update (self):
        if self.shoot_scheme == 'click':
            if self.mouse_down:
                self.shoot()
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
        Obj.update(self)
        if self.aim_scheme == 'move':
            if a != 0:
                # aim
                self.target_angle = atan2(ay, ax)
            # adjust angle
            a = self.angle
            target_a = self.target_angle
            a %= 2 * pi
            if a >= pi:
                a -= 2 * pi
            dists = dict((abs(x), x) for x in
                         (target_a - a, target_a - a + 2 * pi,
                          target_a - a - 2 * pi))
            a += .2 * dists[min(dists)]
            self.angle = a
