from platform import system
import os
from os.path import sep, expanduser, join as join_path
from collections import defaultdict

import pygame as pg

import settings
from util import dd


class Conf (object):

    IDENT = 'game'
    USE_SAVEDATA = False
    USE_FONTS = False

    # save data
    SAVE = ()
    # need to take care to get unicode path
    if system() == 'Windows':
        try:
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', None, 0)
            if n == 0:
                raise ValueError()
        except Exception:
            # fallback (doesn't get unicode string)
            CONF_DIR = os.environ[u'APPDATA']
        else:
            buf = ctypes.create_unicode_buffer(u'\0' * n)
            ctypes.windll.kernel32.GetEnvironmentVariableW(u'APPDATA', buf, n)
            CONF_DIR = buf.value
        CONF_DIR = join_path(CONF_DIR, IDENT)
    else:
        CONF_DIR = join_path(os.path.expanduser(u'~'), '.config', IDENT)
    CONF = join_path(CONF_DIR, 'conf')

    # data paths
    DATA_DIR = ''
    IMG_DIR = DATA_DIR + 'img' + sep
    SOUND_DIR = DATA_DIR + 'sound' + sep
    MUSIC_DIR = DATA_DIR + 'music' + sep
    FONT_DIR = DATA_DIR + 'font' + sep

    # display
    WINDOW_ICON = None #IMG_DIR + 'icon.png'
    WINDOW_TITLE = ''
    MOUSE_VISIBLE = dd(False) # per-backend
    FLAGS = 0
    FULLSCREEN = False
    RESIZABLE = True # also determines whether fullscreen togglable
    RES_W = (960, 540)
    RES_F = pg.display.list_modes()[0]
    RES = RES_W
    MIN_RES_W = (320, 180)
    ASPECT_RATIO = None

    # timing
    FPS = dd(60) # per-backend

    # debug
    PROFILE_STATS_FILE = '.profile_stats'
    DEFAULT_PROFILE_TIME = 5

    # input
    KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
    KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
    KEYS_MINIMISE = (pg.K_F10,)
    KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                    (pg.K_KP_ENTER, pg.KMOD_ALT, True))

    KEYS_MOVE = [
        ((pg.K_LEFT,), (pg.K_UP,), (pg.K_RIGHT,), (pg.K_DOWN,)),
        ((pg.K_a,), (pg.K_w, pg.K_COMMA), (pg.K_d, pg.K_e), (pg.K_s, pg.K_o))
    ]
    KEYS_SHOOT = [(pg.K_SPACE,)]

    # each is (move, aim, shoot)
    # move is (type, ident), type one of 'kb', 'joy'*
    # aim is one of 'move', 'mouse', 'joy'*
    # shoot is (type, ident), type one of 'kb', 'click', 'joy'*
    # *unsupported
    CONTROL_SCHEMES = (
        (('kb', 0), 'mouse', ('click', (1, 2, 3))),
        (('kb', 1), 'move', ('kb', 0))
    )

    # audio
    MUSIC_VOLUME = dd(.5) # per-backend
    SOUND_VOLUME = .5
    EVENT_ENDMUSIC = pg.USEREVENT
    SOUNDS = {'pistol': 5, 'hit': 6} # numbers of sound files
    SOUND_VOLUMES = dd(1)

    # text rendering
    # per-backend, each a {key: value} dict to update fonthandler.Fonts with
    REQUIRED_FONTS = dd({})

    # gameplay
    # level
    ENEMIES = {
        'weak': {
            'size': 10,
            'mass': 5,
            'health': .1,
            'speed': 30,
            'intelligence': 1,
            'damage': 3,
            'kb': 1,
            'diff': 1
        }, 'std': {
            'size': 15,
            'mass': 10,
            'health': .2,
            'speed': 40,
            'intelligence': 1.5,
            'damage': 6,
            'kb': 1.5,
            'diff': 2
        }, 'tank': {
            'size': 40,
            'mass': 70,
            'health': 1.8,
            'speed': 20,
            'intelligence': 5,
            'damage': 20,
            'kb': 4,
            'diff': 3
        }, 'swarm': {
            'size': 10,
            'mass': 5,
            'health': .1,
            'speed': 80,
            'intelligence': 1.5,
            'damage': 2,
            'kb': .5,
            'diff': 2
        }
    }
    ENEMY_WEIGHTINGS = {'weak': 1, 'std': .5, 'tank': .03, 'swarm': .3}
    # ai
    ENEMY_LOST = .003 # chance of aiming at a random location
    # proportion of screen around edges a lost enemy won't aim for
    ENEMY_LOST_BORDER = .1
    ENEMY_REEVAL = 60 # mean time in frames between re-evaluating the target
    ENEMY_TARGET_ACC = 2 # accuracy of choosing nearest target
    ENEMY_MOVE_THRESHOLD = 5
    ENEMY_SPEED_THRESHOLD = .3 # mean speed proportion loss
    ENEMY_DAMAGE = .01
    ENEMY_KNOCKBACK = 3000
    # physics
    STEP = .01
    MAIN_LAYER = 1
    PLAYER_LAYER = 2
    COL_BIAS = .005
    MOVE_FRICTION = .85
    ROTATE_FRICTION = .9
    BDY_RADIUS = 20
    # entities
    ELAST = 1
    FRICTION = .7
    PLAYER_SIZE = 15
    PLAYER_MASS = 10
    PLAYER_SPEED = 70
    PLAYER_HEALTH = 1
    SHOOT_RANGE = 300
    SHOOT_DAMAGE = .1
    SHOOT_COOLDOWN = 25 # frames between shots
    SHOOT_ACCURACY = 15
    SHOOT_KNOCKBACK = 5000
    BULLETS_AT_ONCE = 1

    WEAPONS = {
        'pistol': {
            'range': 1,
            'damage': .5,
            'cooldown': 1,
            'acc': 2,
            'kb': .7,
            'at_once': 1
        }, 'shotgun': {
            'range': .5,
            'damage': 1,
            'cooldown': 3,
            'acc': .5,
            'kb': 2,
            'at_once': 5
        }, 'laser': {
            'range': .5,
            'damage': .3,
            'cooldown': .1,
            'acc': 10,
            'kb': .1,
            'at_once': 1
        }, 'rifle': {
            'range': 5,
            'damage': 5,
            'cooldown': 3,
            'acc': 20,
            'kb': 10,
            'at_once': 1
        }, 'rocket': {
            'range': 2.5,
            'damage': 20,
            'cooldown': 10,
            'acc': .5,
            'kb': 50,
            'at_once': 3
        }, 'machine': {
            'range': .8,
            'damage': .1,
            'cooldown': .1,
            'acc': 1,
            'kb': .5,
            'at_once': 1
        }, 'knife': {
            'range': .2,
            'damage': 1.5,
            'cooldown': 1,
            'acc': .15,
            'kb': 0,
            'at_once': 10
        }
    }
    INITIAL_WEAPON = 'pistol'

    # levels
    LEVELS = {'main': {
        'objs': [
            ((0, 0), (5, 50), (40, 20))
        ]
    }}


def translate_dd (d):
    if isinstance(d, defaultdict):
        return defaultdict(d.default_factory, d)
    else:
        # should be (default, dict)
        return dd(*d)
conf = dict((k, v) for k, v in Conf.__dict__.iteritems()
            if not k.startswith('__'))
types = {
    defaultdict: translate_dd
}
if Conf.USE_SAVEDATA:
    conf = settings.SettingsManager(conf, Conf.CONF, Conf.SAVE, types)
else:
    conf = settings.DummySettingsManager(conf, types)
