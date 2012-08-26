from math import cos, sin, atan2, pi
from random import expovariate as ev, random

import pygame as pg
import pymunk as pm

from conf import conf
from util import ir, randsgn, rand_in, weighted_rand
from ext import evthandler as eh


class Obj (object):
    def __init__ (self, level, pos, radius, mass, layers = 0):
        self.level = level
        self.radius = radius
        self.mass = mass
        self.body = b = pm.Body(mass, pm.moment_for_circle(mass, 0, radius))
        b.position = tuple(pos)
        b.elasticity = conf.ELAST
        self.shape = s = pm.Circle(b, radius)
        s.friction = conf.FRICTION
        s.layers = conf.MAIN_LAYER | layers
        level.space.add(b, s)
        self.angle = 0
        self.health = self.max_health
        self.to_move = [0, 0]

    def move (self, dirn):
        self.to_move[dirn % 2] += 1 if dirn >= 2 else -1

    def hit (self, damage, kb, angle):
        self.health -= damage
        self.body.apply_impulse((kb * cos(angle), kb * sin(angle)))
        if self.health <= 0:
            self.die()

    def update_aim (self, ax, ay, a):
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

    def update (self):
        # move
        ax, ay = self.to_move
        self.to_move = [0, 0]
        # normalise impulse
        a = (ax * ax + ay * ay) ** .5
        if a != 0:
            ax /= a
            ay /= a
            # apply impulse
            r = self.mass * self.speed
            self.body.apply_impulse((ax * r, ay * r))
        # damp movement
        self.body.velocity *= conf.MOVE_FRICTION
        self.body.angular_velocity *= conf.ROTATE_FRICTION
        return (ax, ay, a)

    def draw (self, screen):
        x, y = self.body.position
        c = (255, 0, 0) if isinstance(self, Player) else (0, 150, 0)
        pg.draw.circle(screen, c, (ir(x), ir(y)), self.radius)
        a = self.angle
        length = 1.5 * self.radius
        end = (x + length * cos(a), y + length * sin(a))
        pg.draw.line(screen, (0, 0, 255), (x, y), end)


class Enemy (Obj):
    def __init__ (self, level, pos, size, mass, health, speed, intelligence,
                  damage, kb):
        self.max_health = health
        self.max_speed = speed
        self.intelligence = intelligence
        self.damage = damage
        self.kb = kb
        Obj.__init__(self, level, pos, size, mass)
        self.target_angle = self.angle
        self.re_eval = 0

    def die (self):
        self.level.space.remove(self.body, self.shape)
        self.level.enemies.remove(self)

    def update (self):
        pos = self.body.position
        if self.re_eval <= 0:
            intelligence = self.intelligence
            # aim at the nearest player
            ps = self.level.players
            r = conf.ENEMY_TARGET_ACC * intelligence
            targets = [
                ((1 / p.body.position.get_distance(pos)) * r, p)
                for p in ps
            ] + [(conf.ENEMY_LOST, None)]
            target = targets[weighted_rand(zip(*targets)[0])][1]
            if target is None:
                # aim somewhere random
                w, h = conf.RES
                b = conf.ENEMY_LOST_BORDER
                self.target = (rand_in(b, 1 - b) * w, rand_in(b, 1 - b) * h)
                self.targeting_player = False
            else:
                self.targeting_player = target
                self.target = target.body.position
            # speed
            mean_loss = conf.ENEMY_SPEED_THRESHOLD / intelligence
            self.speed = self.max_speed * (1 - ev(1. / mean_loss))
            self.re_eval = ev(1. / conf.ENEMY_REEVAL)
        self.re_eval -= 1
        to_move = tm = self.target - pos
        if to_move.get_length() < conf.ENEMY_MOVE_THRESHOLD:
            to_move = [0, 0]
        t = self.targeting_player
        if t:
            d = tm.get_length()
            if d < self.radius + t.radius:
                t.hit(self.damage * conf.ENEMY_DAMAGE,
                      self.kb * conf.ENEMY_KNOCKBACK, tm.get_angle())
        self.to_move = to_move
        ax, ay, a = Obj.update(self)
        self.update_aim(ax, ay, a)


class Player (Obj):
    def __init__ (self, level, pos, scheme):
        # initial properties
        self.max_health = conf.PLAYER_HEALTH
        self.shoot_range = conf.SHOOT_RANGE
        self.damage = conf.SHOOT_DAMAGE
        self.max_cooldown = conf.SHOOT_COOLDOWN
        self.shoot_acc = conf.SHOOT_ACCURACY
        self.knockback = conf.SHOOT_KNOCKBACK
        self.bullets_at_once = conf.BULLETS_AT_ONCE
        self.speed = conf.PLAYER_SPEED
        Obj.__init__(self, level, pos, conf.PLAYER_SIZE, conf.PLAYER_MASS,
                     conf.PLAYER_LAYER)
        (move_t, move_i), self.aim_scheme, (shoot_t, shoot_i) = scheme
        self.shoot_scheme = shoot_t
        l_eh = level.event_handler
        if move_t == 'kb':
            l_eh.add_key_handlers([
                (ks, [(lambda k, t, m, i: self.move(i), (i,))], eh.MODE_HELD)
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
        # varying properties
        self.cooldown = 0
        self.weapon = conf.INITIAL_WEAPON
        self.weapon_data = conf.WEAPONS[self.weapon]

    def click (self, evt):
        if evt.button in self.shoot_btns:
            md = self.mouse_down
            f = md.add if evt.type == pg.MOUSEBUTTONDOWN else md.remove
            f(evt.button)

    def shoot (self, *args):
        if self.cooldown <= 0:
            w = self.weapon_data
            if self.aim_scheme == 'move':
                a = self.target_angle
            else:
                a = self.angle
            acc = self.shoot_acc * w['acc']
            pos = self.body.position
            args = (w['range'] * self.shoot_range, w['damage'] * self.damage,
                    w['kb'] * self.knockback, self)
            shoot = self.level.shoot
            # decide number of times to shoot
            cooldown = self.max_cooldown * w['cooldown']
            self.cooldown = ir(cooldown)
            frame = self.level.game.scheduler.timer.frame
            at_once = frame / cooldown + conf.BULLETS_AT_ONCE * w['at_once']
            for i in xrange(max(1, ir(at_once))):
                da = randsgn() * ev(acc)
                shoot(pos, a + da, *args)
            # play sound
            #self.level.game.play_snd(self.weapon)

    def update (self):
        self.cooldown -= 1
        if self.shoot_scheme == 'click':
            if self.mouse_down:
                self.shoot()
        ax, ay, a = Obj.update(self)
        if self.aim_scheme == 'move':
            self.update_aim(ax, ay, a)
