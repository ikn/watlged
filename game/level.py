from math import cos, sin, atan2
from random import choice, expovariate as ev

import pygame as pg
import pymunk as pm

from conf import conf
from obj import Player, Enemy
from util import randsgn, rand_in, weighted_rand


class Level (object):
    def __init__ (self, game, event_handler, n_players = 1, ident = None):
        self.game = game
        self.event_handler = event_handler
        w, h = conf.RES
        self.centre = (w / 2, h / 2)
        self.space = s = pm.Space()
        s.collision_bias = conf.COL_BIAS
        # boundaries for players
        r = conf.BDY_RADIUS
        w += r
        h += r
        z = -r
        for a, b in (((z, z), (w, z)), ((w, z), (w, h)), ((z, h), (w, h)),
                     ((z, z), (z, h))):
            body = pm.Body(pm.inf, pm.inf)
            shape = pm.Segment(body, a, b, r)
            s.add(shape)
            shape.layers = conf.PLAYER_LAYER
        self.init_players(n_players)
        self.init_level(ident)
        self.wave = 0
        self.init()

    def init_level (self, ident):
        if ident is None:
            ident = choice(conf.LEVELS.keys())
        data = conf.LEVELS[ident]

    def init_players (self, n):
        w, h = conf.RES
        pos = (float(w) / 2, float(h) / 2)
        self.players = [Player(self, pos, scheme)
                        for scheme in conf.CONTROL_SCHEMES[:n]]

    def init (self):
        pg.mouse.set_pos(self.centre)
        self.mouse_pos = pm.Vec2d(pg.mouse.get_pos())
        self.enemies = []
        self.add_enemies(10)
        self.bullets = []

    def add_enemies (self, difficulty):
        es = self.enemies
        d = difficulty
        ws = conf.ENEMY_WEIGHTINGS
        e_types = conf.ENEMIES
        # position
        w, h = conf.RES
        axis, side = choice(((0, 0), (0, 1), (1, 0), (1, 1)))
        bdys = ((-50, w + 50), (-50, h + 50))
        x = bdys[axis][side]
        a, b = bdys[not axis]
        y = rand_in(a, b)
        pos = [0, 0]
        while d > 0:
            e = conf.ENEMIES[weighted_rand(ws)]
            d -= e['diff']
            pos[axis] = x + rand_in(-25, 25)
            pos[not axis] = ev(.5 / difficulty)
            es.append(Enemy(self, pos, e['size'], e['mass'], e['health'],
                            e['speed'], e['intelligence']))

    def shoot (self, start, angle, rnge, damage, kb, *exclude):
        end = start + (rnge * cos(angle), rnge * sin(angle))
        self.bullets.append((start, end))
        for o in self.players + self.enemies:
            if o not in exclude and o.shape.segment_query(start, end):
                o.hit(damage, kb, angle)

    def update (self):
        # mouse
        x0, y0 = self.centre
        x, y = pg.mouse.get_pos()
        pg.mouse.set_pos(self.centre)
        mp = self.mouse_pos
        mp += (x - x0, y - y0)
        p = self.players[0]
        dp = mp - p.body.position
        p.angle = atan2(dp[1], dp[0])
        # update players
        for e in self.players + self.enemies:
            e.update()
        self.space.step(conf.STEP)

    def draw (self, screen):
        screen.fill((255, 255, 255))
        for e in self.enemies + self.players:
            e.draw(screen)
        x, y = self.mouse_pos
        pg.draw.circle(screen, (0, 0, 255), (int(x), int(y)), 3)
        for start, end in self.bullets:
            pg.draw.line(screen, (150, 150, 150), start, end)
        self.bullets = []
        return True
