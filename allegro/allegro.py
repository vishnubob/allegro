import arduino
from struct import pack
import time
import colorsys

class Pixel(object):
    MIN_RED     =   0x0
    MIN_GREEN   =   0x0
    MIN_BLUE    =   0x0

    MAX_RED     =   0xff
    MAX_GREEN   =   0xff
    MAX_BLUE    =   0xff

    def __init__(self, red=None, green=None, blue=None):
        if red == None:
            self.red = self.MIN_RED
        else:
            self.red = red
        if green == None:
            self.green = self.MIN_GREEN
        else:
            self.green = green
        if blue == None:
            self.blue = self.MIN_BLUE
        else:
            self.blue = blue

    def copy(self):
        return self.__class__(self.red, self.green, self.blue)

    def __getitem__(self, color):
        if color == 0: return self.red
        if color == 1: return self.green
        if color == 2: return self.blue
        raise ValueError, color

    def __setitem__(self, color, value):
        if color == 0: self.red = value
        elif color == 1: self.green = value
        elif color == 2: self.blue = value
        else: raise ValueError, color

    def ascii(self):
        chars = [chr(ord('0') + x) for x in range(10)]
        val = self.red + self.green + self.blue
        if val == 0:
            return '-'
        return chars[val % len(chars)]

    def __repr__(self):
        return "<Pixel %d,%d,%d>" % (self.red, self.green, self.blue)

    def get_red(self): 
        return self._red
    def set_red(self, val):
        self._red = max(self.MIN_RED, min(self.MAX_RED, int(val)))
    red = property(get_red, set_red)

    def get_green(self): 
        return self._green
    def set_green(self, val):
        self._green = max(self.MIN_GREEN, min(self.MAX_GREEN, int(val)))
    green = property(get_green, set_green)
    grn = property(get_green, set_green)

    def get_blue(self): 
        return self._blue
    def set_blue(self, val):
        self._blue = max(self.MIN_BLUE, min(self.MAX_BLUE, int(val)))
    blue = property(get_blue, set_blue)
    blu = property(get_blue, set_blue)

    def get_rgb(self):
        return (self.red, self.green, self.blue)
    def set_rgb(self, rgb):
        self.red = rgb[0]
        self.green = rgb[1]
        self.blue = rgb[2]
    rgb = property(get_rgb, set_rgb)

    def get_rgb_8bit(self):
        red = int(float(self.red) / (self.MAX_RED - self.MIN_RED) * 0xFF)
        green = int(float(self.green) / (self.MAX_GREEN - self.MIN_GREEN) * 0xFF)
        blue = int(float(self.blue) / (self.MAX_BLUE - self.MIN_BLUE) * 0xFF)
        return (red, green, blue)
    rgb_8bit = property(get_rgb_8bit)

    def get_hsv(self):
        red = self.red / float(self.MAX_RED) 
        green = self.green / float(self.MAX_RED) 
        blue = self.blue / float(self.MAX_BLUE) 
        rgb = (red, green, blue)
        hsv = colorsys.rgb_to_hsv(*rgb)
        return hsv
    def set_hsv(self, hsv):
        rgb = colorsys.hsv_to_rgb(*hsv)
        self.red = self.MAX_RED * rgb[0]
        self.green = self.MAX_GREEN * rgb[1]
        self.blue = self.MAX_BLUE * rgb[2]
    hsv = property(get_hsv, set_hsv)

    def clear(self):
        self.rgb = (0, 0, 0)

class A6281(Pixel):
    MAX_RED     =   0x3ff
    MAX_GREEN   =   0x3ff
    MAX_BLUE    =   0x3ff
    FactoryReset = [0, 0, 0]

    def __repr__(self):
        return "<led %d,%d,%d>" % (self.red, self.green, self.blue)

    def encode_pwm(self):
        cmd = 0
        b1 = (cmd << 6 | self.blue >> 4) & 0xFF
        b2 = (self.blue << 4 | self.red >> 6) & 0xFF
        b3 = (self.red << 2 | self.green >> 8) & 0xFF
        b4 = (self.green) & 0xFF
        return pack("BBBB", b1, b2, b3, b4)

    def encode_cfg(self):
        cmd = 1
        b1 = (cmd << 6 | self.FactoryReset[0] >> 4) & 0xFF
        b2 = (self.FactoryReset[0] << 4 | self.FactoryReset[1] >> 6) & 0xFF
        b3 = (self.FactoryReset[1] << 2 | self.FactoryReset[2] >> 8) & 0xFF
        b4 = (self.FactoryReset[2]) & 0xFF
        return pack("BBBB", b1, b2, b3, b4)

class ShiftBrite(A6281):
    FactoryReset = [120, 100, 100]

class Chain(object):
    ChainOperation = 3
    ChainLength = 1
    ChainLatch = 2
    ChainDisable = 3
    ChainEnable = 4
    ChainConfig = 5

    def __init__(self, arduino, ack_flag=True):
        self.arduino = arduino
        self.ack_flag = ack_flag
        self.lights = []

    def disable_ack(self):
        self.ack_flag = False

    def enable_ack(self):
        self.ack_flag = True

    def copy(self, clear=False):
        chain = self.__class__(self.arduino, self.ack_flag)
        for led in self.lights:
            chain.lights.append(led.copy())
        chain._length = self._length
        if clear:
            chain.clear(False)
        return chain

    def __len__(self):
        return self._length

    def __str__(self):
        _str = ''
        for led in self.lights:
            _str += str(led) + '\n'
        return _str

    def close(self):
        self.arduino.close()

    def reset(self, delay):
        self.arduino.reset(delay)
        self.length = 0

    def __iter__(self):
        return iter(self.lights)

    def __getitem__(self, key):
        return self.lights[key]

    def clear(self, draw=True):
        for led in self.lights:
            led.clear()
        if draw:
            self.draw()

    def draw(self):
        buf = ''
        for led in self.lights:
            buf += led.encode_pwm()
        self.arduino.send(buf)
        self.latch()
        self.config()
    
    def config(self):
        op = (self.ChainOperation << 6) | self.ChainConfig
        data = pack("B", op)
        self.arduino.send(data)
        if self.ack_flag:
            self.arduino.wait_for_ack()

    def disable(self):
        op = (self.ChainOperation << 6) | self.ChainDisable
        data = pack("B", op)
        self.arduino.send(data)
        if self.ack_flag:
            self.arduino.wait_for_ack()
        
    def enable(self):
        op = (self.ChainOperation << 6) | self.ChainEnable
        data = pack("B", op)
        self.arduino.send(data)
        if self.ack_flag:
            self.arduino.wait_for_ack()
        
    def latch(self):
        op = (self.ChainOperation << 6) | self.ChainLatch
        data = pack("B", op)
        self.arduino.send(data)
        if self.ack_flag:
            self.arduino.wait_for_ack()

    def set_length(self, length):
        self._length = length
        self.lights = []
        for idx in range(self._length):
            led = ShiftBrite()
            self.lights.append(led)
        op = (self.ChainOperation << 6) | self.ChainLength
        data = pack("BB", op, length)
        self.arduino.send(data)
        if self.ack_flag:
            self.arduino.wait_for_ack()
        self.config()

    def get_length(self):
        return self._length
    length = property(get_length, set_length)

class FadeIter(object):
    def __init__(self, old_chain, new_chain, ttl):
        self.old_chain = old_chain
        self.new_chain = new_chain
        self.slopes = []
        self.ttl = ttl
        self.setup_increments()

    def setup_increments(self):
        for led in range(len(self.old_chain)):
            color_slopes = []
            for clr in range(3):
                distance = self.new_chain[led][clr] - self.old_chain[led][clr]
                color_slopes.append(distance / float(self.ttl))
            self.slopes.append(color_slopes)

    def __iter__(self):
        return self.FadeIterCore(self.old_chain, self.slopes, self.ttl)

    def run(self):
        for nothing in self:
            pass

    class FadeIterCore(object):
        def __init__(self, old_chain, slopes, ttl):
            self.old_chain = old_chain
            self.cur_chain = old_chain.copy()
            self.cur_chain.clear(False)
            self.slopes = slopes
            self.ttl = ttl
            self.ts = time.time()

        def next(self):
            now = time.time()
            delta = now - self.ts
            if delta > self.ttl:
                delta = self.ttl
            for led in range(len(self.cur_chain)):
                for clr in range(3):
                    self.cur_chain[led][clr] = self.slopes[led][clr] * delta + \
                        self.old_chain[led][clr]
            self.cur_chain.draw()
            if delta >= self.ttl:
                raise StopIteration

if __name__ == '__main__':
    #port = "/dev/tty.usbserial-A800ewuP"
    port = "/dev/ttyUSB0"
    debug = True
    debug = False
    hwport = arduino.Arduino(port, debug=debug)
    hwport.reset(5)
    chain = Chain(hwport)
    chain.length = 2
    chain.clear()
    HSV = 1000
    while 1:
        for hue in range(HSV):
            hue = hue / float(HSV)
            for led in range(chain.length):
                chain.lights[led].hsv = (hue, 1, 1)
            chain.draw()
            #time.sleep(.1)

    """
    while 1:
        for x in range(1023):
            for led in range(chain.length):
                chain.lights[led].red = x
            chain.draw()
        chain.clear()
        for x in range(1023):
            for led in range(chain.length):
                chain.lights[led].green = x
            chain.draw()
        chain.clear()
        for x in range(1023):
            for led in range(chain.length):
                chain.lights[led].blue = x
            chain.draw()
        chain.clear()
        import random
        for x in range(1023):
            for led in range(chain.length):
                chain.lights[led].blue = random.randint(0, 1023)
            chain.draw()
        chain.clear()
    """

