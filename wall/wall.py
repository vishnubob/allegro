import random
import sys
import time
import traceback
from optparse import OptionParser

# local imports
from allegro import *
from gui import Wall_Visualizer
from motion import Watcher, DebugWatcher
from effects import Effects

class Wall(object):
    def __init__(self, width, height, chain, debug=False, gui=False, copy=False):
        self.chain = chain
        self.debug = debug
        self.width = width
        self.height = height

        if not copy:
            self.chain.length = self.width * self.height
            self.gui = None
            if gui:
                self.gui = Wall_Visualizer(self.width, self.height)
        else:
            self.gui = gui

    def clear(self, draw=False):
        self.chain.clear(draw)

    def ascii(self):
        txt = ''
        for y in range(self.height):
            for x in range(self.width):
                txt += self.pixel(x, y).ascii()
            txt += '\n'
        return txt

    def draw(self):
        self.chain.draw()
        if self.gui:
            self.gui.draw(self)

    def copy(self, clear=False):
        chain2 = self.chain.copy(clear)
        return self.__class__(chain2, self.debug, self.gui, True)

    def __len__(self):
        return len(self.chain)

    def __iter__(self):
        return iter(self.chain)

    def __getitem__(self, key):
        return self.chain[key]

    def pixel(self, x, y, debug=False):
        """
        Turn x and y indices into a matrix into the corresponding pixel in the
        linear chain that actually describes the lights.

        x: integer
        y: integer

        Returns: the ShiftBright at that location

        The assumed light configuration is a snake, ie:

        1 -- 2 -- 3
                  |
        6 -- 5 -- 4
        |
        7 -- 8 -- 9
        """
        if debug:
            print "==>", x, y

        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            return None

        # Get the length of the snake corresponding to the full-width rectangle
        # that sits above the pixel. Then add the remaining x length. This gives
        # you the index into the physical light chain.
        #
        # For example, if this is your matrix:
        #
        # O O O
        # O O O
        # O X O
        # O O O
        #
        # If X is the pixel we are dealing with, we were given x = 1, y = 2. The
        # length of the snake corresponding to the full-width rectangle that
        # sits above the pixel is the area of the * rectangle, minus 1:
        #
        # * * *     0 1 2
        # * * *     5 4 3
        # O X O ===>      == (3 x 2 - 1)
        # O O O
        #
        # To finish the length of the snake, we need to know which direction the
        # snake is going to get the remaining x length. In this example, the
        # snake is curving right, so we get:
        #
        # 0 1 2
        # 5 4 3
        # 6 7
        #
        rectangle = self.width * y - 1
        if y % 2:
            return self.chain[rectangle + x + 1]
        else:
            return self.chain[rectangle + self.width - x]

class WatchAndEffect(object):
    def __init__(self, wall, nocam=False, effect_order="random"):
        self.wall = wall
        self.nocam = nocam
        if not self.nocam:
            self.watcher = Watcher()
        else:
            self.watcher = DebugWatcher()
        self.effect_order = effect_order
        if self.effect_order:
            self.current_effect = 0

    def run(self):
        while 1:
            vector = self.watcher.vector()
            if vector[0] in (1, -1):
                speed = vector[1] / 8
                speed = min(1, speed)
                direction = vector[0]
            # simul
            elif vector[0] == 2:
                speed = random.random() / 32
                dir_stack = [1, -1]
                direction = random.choice(dir_stack)
            # timeout
            elif vector[0] == 0:
                speed = random.random() / 8
                direction = vector[1]

            effect = self.pick_effect()
            effect = effect(self.wall, speed=speed, direction=direction)
            print effect
            effect.run()
            self.wall.clear(True)

    def pick_effect(self):
        """
        Returns an Effect (sub)class based on the effect_order.
        """
        if self.effect_order == "serial":
            effect = Effects[self.current_effect]
            self.current_effect += 1
            if self.current_effect > len(Effects) - 1:
                self.current_effect = 0
            return effect
        elif self.effect_order == "random":
            return random.choice(Effects)
        else:
            print "Unknown effect order: choosing random"
            return random.choice(Effects)

def run(opts, args):
    if opts['dummy']:
        hwport = DummyPort(debug=opts['debug'])
    else:
        hwport = Arduino(opts['port'], debug=opts['debug'])
        hwport.reset()
    chain = Chain(hwport, ack_flag=False)
    wall = Wall(opts['width'], opts['height'], chain, debug=opts['debug'],
                gui=opts['gui'])
    for clear_it in range(10):
        wall.clear(True)
        time.sleep(.1)
    waf = WatchAndEffect(wall, nocam=opts['nocam'],
                         effect_order=opts['effect_order'])
    waf.run()

def get_args():
    parser = OptionParser()
    parser.add_option("-p", "--port", help="arduino port")
    parser.add_option("-d", "--debug", action="store_true",
                        help="enable communication debugging")
    parser.add_option("-R", "--nocam", action="store_true",
                        help="No camera, random stimulus")
    parser.add_option("-D", "--dummy", action="store_true",
                        help="enable dummy port")
    parser.add_option("-G", "--gui", action="store_true",
                        help="enable GUI")
    parser.add_option("-C", "--crash", action="store_true",
                        help="Disable crash protection")
    parser.add_option("-o", "--order", action="store", dest="effect_order",
                      help="Specify the effects order: one of 'random' or 'serial'")
    parser.add_option("-w", "--width", action="store", help="Width of light wall")
    parser.add_option("-t", "--height", action="store", help="Height of light wall")

    dport = '__unknown__'
    if sys.platform.startswith('linux'):
        dport = '/dev/ttyUSB0'
    elif sys.platform.startswith('darwin'):
        dport = '/dev/tty.usbserial-A800ewuP'
    parser.set_defaults(port=dport, debug=False, dummy=False, gui=False,
                        crash=False, nocam=False, effect_order="random",
                        width=8, height=8)
    (opts, args) = parser.parse_args()

    opts.width = int(opts.width)
    opts.height = int(opts.height)

    opts = eval(str(opts))
    return opts, args

if __name__ == '__main__':
    opts, args = get_args()
    crash = opts['crash']
    while 1:
        try:
            run(opts, args)
        except KeyboardInterrupt:
            break
        except Exception:
            txt = ''
            txt += time.strftime("%c") + '\n'
            txt = traceback.format_exc() + '\n'
            f = open('traceback.txt', 'a')
            f.write(txt)
            f.close()
            print "!!! CRASH !!!"
            print txt
            if crash:
                break
