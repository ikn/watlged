from random import choice

import pygame as pg
import pymunk as pm

from conf import conf
from player import Player
from ext import evthandler as eh


class Level (object):
    def __init__ (self, game, event_handler, n_players = 1, ident = None):
        self.game = game

        event_handler.add_key_handlers(sum([
            [
                (ks, [(self.move, (i, j,))], eh.MODE_HELD)
                for j, ks in enumerate(all_ks)
            ] for i, all_ks in enumerate(conf.KEYS_MOVE[:n_players])
        ], []))

        self.space = s = pm.Space()
        s.collision_bias = conf.COL_BIAS
        self.init_players(n_players)
        self.init_level(ident)
        self.n = 0
        self.init()

    def init_level (self, ident):
        if ident is None:
            ident = choice(conf.LEVELS.keys())
        data = conf.LEVELS[ident]

    def init_players (self, n):
        w, h = conf.RES
        pos = (float(w) / 2, float(h) / 2)
        self.players = [Player(self, pos) for i in xrange(n)]

    def init (self):
        pass

    def move (self, key, mode, mods, player, dirn):
        self.players[player].move(dirn)

    def update (self):
        for p in self.players:
            p.update()
        self.space.step(conf.STEP)

    def draw (self, screen):
        screen.fill((255, 255, 255))
        for p in self.players:
            p.draw(screen)
        return True
