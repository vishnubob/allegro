from allegro import *
import random

def init(port, length, debug=False):
    hwport = arduino.Arduino(port, debug=debug)
    chain = Chain(hwport)
    hwport.reset(5)
    chain.length = length
    chain.clear()
    return chain

def debug_chain(port, length):
    hwport = arduino.Arduino(port, debug=True)
    chain = Chain(hwport)
    hwport.reset(5)
    raw_input("set length")
    chain.length = length
    raw_input("send config")
    chain.config()
    raw_input("set clear")
    chain.clear()
    idx = 0
    for led in chain:
        prompt = "LED %d" % idx
        raw_input(prompt)
        chain.clear(False)
        led.red = 1023
        chain.draw()

class PartyChain(object):
    def __init__(self, port, length, debug=False):
        self.chain = init(port, length, debug=debug)

    def random_color(self):
        return [random.random() * 1023 for x in range(3)]

    def pop_pop_pop(self):
        self.chain2 = self.chain.copy(False)
        channel = random.choice([0, 1])
        runs = random.randint(10, 20)
        while runs:
            color = random.randint(0, 2)
            ttl = 1
            #self.chain2[channel][color] = 1023
            self.chain2[channel].set_rgb(self.random_color())
            fi = FadeIter(self.chain, self.chain2, ttl)
            fi.run()
            channel = [1, 0][channel]
            self.chain = self.chain2
            self.chain2 = self.chain.copy(True)
            runs -= 1

    def bing_bong(self):
        self.chain2 = self.chain.copy(False)
        runs = random.randint(50, 100)
        while runs:
            color = random.randint(0, 2)
            ttl = 1
            #for led in self.chain2:
                #led[color] = 1023
            for x in range(18):
                self.chain2[x][color] = 1023
            print "chain"
            print self.chain
            print "chain2"
            print self.chain2
            fi = FadeIter(self.chain, self.chain2, ttl)
            fi.run()
            self.chain = self.chain2
            self.chain2 = self.chain.copy(True)
            runs -= 1

    def make_red(self):
        self.chain.draw()
        color = 0
        while 1:
            for x in range(1024):
                self.chain.clear()
                for led in self.chain:
                    led[0] = x
                    #led[1] = x
                    #led[2] = x
                print self.chain
                self.chain.draw()

    def hsv_rotate(self):
        offset = 0
        step = 1.0 / self.chain.length
        sat_step = 1.0 / (self.chain.length / 2.0)
        self.chain2 = self.chain.copy(False)
        runs = random.randint(50, 100)
        while runs:
            for led in range(self.chain.length):
                hue_led_offset = (led + offset) % self.chain.length
                hue = step * (hue_led_offset + 1)
                sat_led_offset = (led + offset) % (self.chain.length / 2.0)
                sat = sat_step * (sat_led_offset + 1)
                self.chain2[led].hsv = (hue, 1, 1)
            print self.chain
            print self.chain2
            ttl = .1
            fi = FadeIter(self.chain, self.chain2, ttl)
            fi.run()
            self.chain = self.chain2
            self.chain2 = self.chain.copy(True)
            offset += 1
            runs -= 1

    def cylon(self):
        self.chain.clear(False)
        #runs = random.randint(50, 100)
        runs = 300
        ledctr = 0
        tail = 4
        direction = 1
        step = 1023.0 / tail
        color = random.choice(range(3))
        ttlstep = 1 / float(runs)
        while runs:
            self.chain2 = self.chain.copy(True)
            for x in range(tail):
                ledstep = tail - x
                ledidx = ledctr + (tail - x) * -direction
                if ledidx < 0 or ledidx >= len(self.chain):
                    continue
                self.chain2[ledidx][color] = ledstep * step
                #self.chain2[ledidx].green = ledstep * step
            print self.chain2
            ttl = runs * ttlstep / 10
            fi = FadeIter(self.chain, self.chain2, ttl)
            fi.run()
            if ((ledctr + tail) < 0) or ((ledctr - tail) >= len(self.chain)):
                direction = -1 * direction
                if direction == -1:
                    ledctr = len(self.chain)
                else:
                    ledctr = -1
                color = random.choice(range(3))
            ledctr = ledctr + direction
            self.chain = self.chain2
            runs -= 1

    def flash_photo(self):
        self.chain.clear(False)
        runs = random.randint(50, 100)
        ledcnt = 0
        while runs:
            self.chain2 = self.chain.copy(True)
            self.chain.clear(False)
            # pick a random led
            led = random.choice(self.chain2)
            #led = self.chain2[ledcnt]
            ledcnt += 1
            ledcnt %= len(self.chain2)
            #led.rgb = (1023, 1000, 1000)
            led.rgb = (1023, 0, 0)
            ttl = .05
            fi = FadeIter(self.chain, self.chain2, ttl)
            fi.run()


if __name__ == '__main__':
    #port = '/dev/ttyUSB0'
    port = '/dev/tty.usbserial-A800eL2U'
    debug = True
    debug = False
    #debug_chain(port, 24)
    mb = PartyChain(port, 24, debug=debug)
    while 1:
        #mb.cylon()
        #mb.bing_bong()
        mb.cylon()

