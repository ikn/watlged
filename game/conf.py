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
    SOUNDS = {} # numbers of sound files
    SOUND_VOLUMES = {}

    # text rendering
    # per-backend, each a {key: value} dict to update fonthandler.Fonts with
    REQUIRED_FONTS = dd({})

    # gameplay
    STEP = .01
    MAIN_LAYER = 1
    PLAYER_LAYER = 2
    COL_BIAS = .01
    MOVE_FRICTION = .85
    ROTATE_FRICTION = .9
    # entities
    ELAST = 1
    FRICTION = .7
    PLAYER_SIZE = 15
    PLAYER_MASS = 10
    PLAYER_SPEED = 700
    PLAYER_HEALTH = 1
    SHOOT_RANGE = 200
    SHOOT_DAMAGE = .1
    SHOOT_COOLDOWN = 25 # frames between shots
    SHOOT_ACCURACY = 15
    SHOOT_KNOCKBACK = 1000

    WEAPONS = {
        'pistol': {
            'range': 1,
            'damage': .5,
            'cooldown': 1,
            'acc': 2,
            'kb': .7
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
