import random
import sys
import time
import traceback
from optparse import OptionParser

# local imports
from allegro import *
from gui import Wall64_Visualizer
from motion import Watcher, DebugWatcher
from effects import Effects

class Wall64(object):
    def __init__(self, chain, debug=False, gui=False, copy=False):
        self.chain = chain
        self.debug = debug
        if not copy:
            self.chain.length = 64
            self.gui = None
            if gui:
                self.gui = Wall64_Visualizer()
        else:
            self.gui = gui
        
    def clear(self, draw=False):
        self.chain.clear(draw)

    def ascii(self):
        txt = ''
        for y in range(8):
            for x in range(8):
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

    def pixel(self, x, y, wrap=False, debug=False):
        if wrap:
            y = int(y) % 8
            x = 7 - (int(x) % 8)
        else:
            if x < 0 or x > 7 or y < 0 or y > 7:
                return None
            x = 7 - int(x)
            y = int(y)
        if debug:
            print "==>", x, y
        if (y % 2):
            pixel = (y * 8) + 7 - x
        else:
            pixel = (y * 8) + x
        return self.chain[pixel]

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
    wall = Wall64(chain, debug=opts['debug'], gui=opts['gui'])
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

    dport = '__unknown__'
    if sys.platform.startswith('linux'):
        dport = '/dev/ttyUSB0'
    elif sys.platform.startswith('darwin'):
        dport = '/dev/tty.usbserial-A800ewuP'
    parser.set_defaults(port=dport, debug=False, dummy=False, gui=False,
                        crash=False, nocam=False, effect_order="random")
    (opts, args) = parser.parse_args()
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
