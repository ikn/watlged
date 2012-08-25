from random import choice
from math import cos, sin, atan2

import pygame as pg
import pymunk as pm

from conf import conf
from obj import Player


class Level (object):
    def __init__ (self, game, event_handler, n_players = 1, ident = None):
        self.game = game
        self.event_handler = event_handler
        w, h = conf.RES
        self.centre = (w / 2, h / 2)
        self.space = s = pm.Space()
        s.collision_bias = conf.COL_BIAS
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
        self.bullets = []

    def shoot (self, start, angle, r, damage, *exclude):
        end = start + (r * cos(angle), r * sin(angle))
        self.bullets.append((start, end))
        for o in self.players + self.enemies:
            if o not in exclude and o.shape.segment_query(start, end):
                o.hit(damage)

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
        for p in self.players:
            p.update()
        self.space.step(conf.STEP)

    def draw (self, screen):
        screen.fill((255, 255, 255))
        for p in self.players:
            p.draw(screen)
        x, y = self.mouse_pos
        pg.draw.circle(screen, (0, 0, 255), (int(x), int(y)), 3)
        for start, end in self.bullets:
            pg.draw.line(screen, (150, 150, 150), start, end)
        self.bullets = []
        return True
