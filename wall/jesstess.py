import random
import time
import colorsys
from effects import Effect
import ascii8x8
import itertools

class Mondrian(Effect):
    def _init(self, kw):
        red = (0, 1, 1)
        blue = (.6, 1, .7)
        yellow = (.2, 1, 1)
        black = (0, 0, 0)
        self.colors = [red, blue, yellow, black]

    def drawLine(self, color):
        """
        Draw a line of a given color that is randomly vertical or horizontal and
        takes up the full width or height of the wall.

        color: a 3-element tuple of hsv values
        """
        x_max = self.wall.width - 1
        y_max = self.wall.height - 1

        vert = random.choice((0, 1))
        if vert:
            # The line starts at either the top or bottom of the wall.
            x = random.randint(0, x_max)
            y = random.choice((0, y_max))
        else:
            # The line starts at either the left or right side of the wall.
            x = random.choice((0, x_max))
            y = random.randint(0, y_max)

        if vert and y:
            # Vertical line drawn up
            self.vert_line(color, x, y, -1)
        elif vert:
            # Vertical line drawn down
            self.vert_line(color, x, y, 1)
        elif x:
            # Horizontal line drawn left
            self.horiz_line(color, x, y, -1)
        else:
            # Horizontal line drwan right
            self.horiz_line(color, x, y, 1)

    def vert_line(self, color, x, y, direction):
        """
        Draw a vertical line in the specified direction and color.

        color: a three-element tuple of hsv values
        x: integer
        y: integer
        direction: integer, either -1 or 1. -1 means draw up, 1 means draw
        down.
        """
        for i in range(self.wall.height):
            pixel = self.wall.pixel(x, y + i * direction)
            pixel.hsv = color
            self.wall.draw()

    def horiz_line(self, color, x, y, direction):
        """
        Draw a horizontal line in the specified direction and color.

        color: a three-element tuple of hsv values
        x: integer
        y: integer
        direction: integer, either -1 or 1. -1 means draw left, 1 means draw
        right.
        """
        for i in range(self.wall.width):
            pixel = self.wall.pixel(x + i * direction, y)
            pixel.hsv = color
            self.wall.draw()

    def drawSquare(self, color):
        """
        Draw a square of the specified color. Some of the square may end up off
        the wall. The size is random within limits based on the wall size.
        """
        # The square is at least 2 x 2
        max_size = max(3, int(max(self.wall.width, self.wall.height) *.75))
        size = random.choice(tuple(range(2, max_size)))

        # The upper-left corner of the square is somewhere outside the lower
        # right corner, to make it more likely that most of the square is on the
        # wall.
        corner_x = random.randint(0, int(self.wall.width * .75))
        corner_y = random.randint(0, int(self.wall.height * .75))

        for x in range(corner_x, corner_x + size + 1):
            for y in range(corner_y, corner_y + size + 1):
                if x < self.wall.width and y < self.wall.height:
                    pixel = self.wall.pixel(x, y)
                    pixel.hsv = color
        self.wall.draw()

    def run(self):
        """
        Draw several lines and squares in the range of allowed colors.
        """
        for i in range(5 * len(self.colors)):
            shape = random.random()
            if shape < .75:
                self.drawLine(self.colors[i % len(self.colors)])
            else:
                self.drawSquare(self.colors[i % len(self.colors)])
            time.sleep(.2)
        time.sleep(1)

class Pinwheel(Effect):
    """
    Mimics a rotating pinwheel.

    Makes the largest square possible with an even-number length side
    on the wall.

    Minimum wall size: 2 x 2.
    """
    class Triangle(object):
        def __init__(self, dot_list, wall):
            self.dot_list = dot_list
            self.wall = wall

        def colorize(self):
            for dot in self.dot_list:
                pixel = self.wall.pixel(dot[0], dot[1])
                pixel.hsv = (self.hue, 1, 1)

    def _init(self, kw):
        width = length = min(self.wall.width, self.wall.height)

        if width % 2:
            # requires an even-number length side
            width = width - 1
            length = length - 1

        # Assign pixels to different triangles.
        # 1 1 1 1 2 2 2 2
        # 8 1 1 1 2 2 2 3
        # 8 8 1 1 2 2 3 3
        # 8 8 8 1 2 3 3 3
        # 7 7 7 6 5 4 4 4
        # 7 7 6 6 5 5 4 4
        # 7 6 6 6 5 5 5 4
        # 6 6 6 6 5 5 5 5

        # Triangle 1
        self.tri1 = []
        for i in range(0, width/2):
            self.tri1.extend([(x, i) for x in range(i, width/2)])

        # Triangle 2
        self.tri2 = []
        for i in range(width/2):
            self.tri2.extend([(x, i) for x in range(width/2, width - i)])

        # Triangle 3
        self.s1 = []
        for i in range(width/2 - 1, 0, -1):
            self.s1.extend([(x, i) for x in range(width - i, width)])

        # Triangle 4
        self.s2 = []
        for i in range(width/2 + 1, width):
            self.s2.extend([(x, i - 1) for x in range(i, width)])

        # Triangle 5
        self.tri3 = []
        for i in range(width, width/2, -1):
            self.tri3.extend([(x, i - 1) for x in range(width/2, i)])

        # Triangle 6
        self.tri4 = []
        for i in range(0, width/2):
            self.tri4.extend([(x, width - 1 - i) for x in range(i, width/2)])

        # Triangle 7
        self.s3 = []
        for i in range(width/2 - 1, 0, -1):
            self.s3.extend([(x, width/2 + (width/2 - 1 - i)) for x in range(0, i)])

        # Triangle 8
        self.s4 = []
        for i in range(width/2 - 1, 0, -1):
            self.s4.extend([(x, i) for x in range(0, i)])

        self.triangles = []
        for triangle in [self.tri1, self.tri2, self.s1, self.s2,
                         self.tri3, self.tri4, self.s3, self.s4]:
            self.triangles.append(self.Triangle(triangle, self.wall))

        hue = random.random()
        # diagonal triangles have the same color
        self.colors = [hue + i * .06 for i in range(4)]
        self.colors.extend(self.colors)

    def shift(self):
        first = self.colors.pop(0)
        self.colors.append(first)

        counter = 0
        for triangle in self.triangles:
            triangle.hue = self.colors[counter]
            triangle.colorize()
            counter = counter + 1
        self.wall.draw()
        time.sleep(.1)

    def run(self):
        for i in range(50):
            self.shift()

    @classmethod
    def run_on_wall(cls, width, height):
        if width < 2 or height < 2:
            return False
        return True

class Letters(Effect):
    """
    Cycle through the letters of the alphabet.

    Minimum wall size: 8 x 8.
    """
    def run(self):
        color = random.random()
        foreground = (color, 1, 1)
        background = ((color + .5) % 1, 1, 1)

        # Center the letters on the wall
        x_offset = int((self.wall.width - 8) / 2)
        y_offset = int((self.wall.height - 8) / 2)

        for ord in range(65, 123):
            self.wall.clear()

            # Color everything with the background color
            for i in range(self.wall.width):
                for j in range(self.wall.height):
                    self.wall.pixel(i, j).hsv = background

            # Color the foreground letter
            ascii8x8.draw_chr(chr(ord), self.wall, foreground, background,
                              x_offset=x_offset, y_offset=y_offset)
            self.wall.draw()
            time.sleep(.2)

    @classmethod
    def run_on_wall(cls, width, height):
        """
        The ascii8x8 library requires at least an 8 x 8 wall.
        """
        if width < 8 or height < 8:
            return False
        return True

class Bounce(Effect):
    """
    3 balls bounce around.

    Minimum wall size: 4 x 4.
    """
    class Ball(object):
        def __init__(self, wall, hue):
            self.wall = wall
            self.hue = hue
            self.x = random.choice((0, self.wall.width - 1))

            if self.x:
                self.horiz = 0 # left
            else:
                self.horiz = 1 # right

            self.vert = random.choice((0, 1)) # 1 = up
            self.y = random.randint(0, self.wall.height - 1)
            self.tail = []

        def display_ball(self):
            """
            Draw the ball and its tail.
            """
            pixel = self.wall.pixel(self.x, self.y)
            pixel.hsv = (self.hue, 1, 1)

            # To avoid flicker, the wall is never cleared, and instead the last
            # pixel in the tail is always black, so as the ball moves the tail
            # erases itself.
            intensities = [.75, .5, .25, 0]
            for i in range(len(self.tail)):
                elt = self.tail[i]
                pixel = self.wall.pixel(elt[0], elt[1])
                pixel.hsv = (self.hue, 1, intensities[i])
            self.wall.draw()

        def move_ball(self):
            """
            Move the ball and its tail along its line of motion (always of slope
            +- 1).
            """
            # Update the tail.
            self.tail.insert(0, (self.x, self.y))
            if len(self.tail) > 4:
                self.tail.pop()

            # If it's in the middle of the wall, keep heading in the current
            # direction.
            if self.horiz:
                self.x = self.x + 1
            else:
                self.x = self.x - 1
            if self.vert:
                self.y = self.y + 1
            else:
                self.y = self.y - 1

            x_max = self.wall.width - 1
            y_max = self.wall.height - 1

            # If it has hit a wall, bounce off the wall.
            if self.x > x_max:
                self.horiz = 0
                self.x = x_max - 1
            if self.x < 0:
                self.x = 1
                self.horiz = 1
            if self.y > y_max:
                self.y = y_max - 1
                self.vert = 0
            if self.y < 0:
                self.y = 1
                self.vert = 1

        def move(self):
            self.display_ball()
            self.move_ball()

    def run(self):
        master_hue = random.random()
        pixels = []
        counter = 0
        start_time = time.time()
        while time.time() - start_time < 10:
            for pixel in pixels:
                pixel.move()
            time.sleep(.1)

            # Space out when the balls appear.
            if counter % 4 == 0 and len(pixels) < 3:
                # The balls' colors rotate around the color wheel.
                pixels.append(
                    self.Ball(self.wall, master_hue + .15 * len(pixels)))
            counter = counter + 1

    @classmethod
    def run_on_wall(cls, width, height):
        if width < 4 or height < 4:
            return False
        return True

class Twinkle(Effect):
    class Star(object):
        """
        The life of a Star:

        1. Try to turn on.
        2. If you're on, shine with an intensity that decays over time.
        """
        def __init__(self, wall, x, y):
            self.wall = wall
            self.x = x
            self.y = y
            self.decay = 0
            self.on = False
            # Stick to blueish colors.
            self.hue = .65 + random.uniform(-1, 1) * .15

        def twinkle(self):
            self.try_on()
            if self.on:
                pixel = self.wall.pixel(self.x, self.y)
                pixel.hsv = (self.hue, 1, self.decay*.1)
            self.decay_light()

        def try_on(self):
            if random.random() > .95:
                self.on = True
                self.decay = 10

        def decay_light(self):
            if self.on:
                self.decay = self.decay - 1

            if self.decay == 0:
                self.on = False

    def _init(self, kw):
        """
        Every pixel is a star.
        """
        self.stars = []
        for x in range(0, self.wall.width):
            for y in range(0, self.wall.height):
                self.stars.append(self.Star(self.wall, x, y))

    def run(self):
        start_time = time.time()
        while time.time() - start_time < 10:
            for star in self.stars:
                star.twinkle()
            self.wall.draw()
            time.sleep(.1)
            self.wall.clear()

class Rain(Effect):
    class Droplet(object):
        def __init__(self, wall, droplets):
            self.wall = wall
            self.droplets = droplets
            self.x = 0
            self.y = 0
            self.decay = 0
            self.decaying = False
            self.on = False
            self.hue = random.random()

        def splash(self, decay, hue):
            if not self.on:
                self.on = True
                self.decay = decay
                self.hue = hue

        def drop(self):
            self.try_on()
            if self.on:
                pixel = self.wall.pixel(self.x, self.y)
                pixel.hsv = (self.hue, 1, self.decay * .1)
                self.spread()
            self.decay_light()

        def try_on(self):
            if random.random() > .995:
                self.on = True
                self.decay = 10
        
        def decay_light(self):
            if self.on:
                self.decay = self.decay - 1

            if self.decay == 0:
                self.on = False

        def spread(self):
            below = above = left = right = None
            if self.x != 0:
                left = self.droplets[self.x - 1][self.y]
            if self.x != len(self.droplets) - 1:
                right = self.droplets[self.x + 1][self.y]
            if self.y != 0:
                above = self.droplets[self.x][self.y - 1]
            if self.y != len(self.droplets[0]) - 1:
                below = self.droplets[self.x][self.y + 1]

            changers = filter(lambda x: x != None, [below, above, left, right])
            for star in changers:
                star.splash(self.decay, self.hue + .01)

    def _init(self, kw):
        self.droplets = []
        for x in range(0, self.wall.width):
            col = [self.Droplet(self.wall, self.droplets) for x in range(0, self.wall.height)]
            self.droplets.append(col)

        for x in range(len(self.droplets)):
            for y in range(len(self.droplets[0])):
                self.droplets[x][y].x = x
                self.droplets[x][y].y = y

    def run(self):
        start_time = time.time()
        while time.time() - start_time < 10:
            for i in range(0, self.wall.width):
                for j in range(0, self.wall.height):
                    self.droplets[i][j].drop()
            self.wall.draw()
            time.sleep(.1)
            self.wall.clear()


class Rings(Effect):
    class RingElement(object):
        def __init__(self, location):
            self.location = location
            self.hue = 0

        def setHue(self, hue):
            self.hue = hue

        def getHue(self):
            return self.hue

        def x(self):
            return self.location[0]
        
        def y(self):
            return self.location[1]

    def _init(self, kw):
        x_min = 0
        x_max = 7
        y_min = 0
        y_max = 7

        self.rings = [[], [], [], []]
        for ring in self.rings:
            for x in range(x_min, x_max + 1):
                ring.append(self.RingElement((x, y_min)))
            for y in range(y_min, y_max + 1):
                ring.append(self.RingElement((x_max, y)))
            for x in range(x_max, x_min - 1, -1):
                ring.append(self.RingElement((x, y_max)))
            for y in range(y_max, y_min, -1):
                ring.append(self.RingElement((x_min, y)))

            x_min = x_min + 1
            x_max = x_max - 1
            y_min = y_min + 1
            y_max = y_max - 1
        
    def run(self):
        self.wall.clear()
        hue = random.random()
        for i in range(10):
            for ring in self.rings:
                for elt in ring:
                    elt.setHue(hue)
                    pixel = self.wall.pixel(elt.x(), elt.y())
                    pixel.hsv = (elt.getHue(), 1, 1)
                self.wall.draw()
                time.sleep(.2)
                hue = hue + .1

class Spiral(Effect):
    def _init(self, kw):
        self.hue = random.random()
        self.tail = []

    def draw(self, x, y):

        self.tail.insert(0, (x, y))
        if len(self.tail) > 4:
            self.tail.pop()

        self.hue = self.hue + .003
        pixel = self.wall.pixel(x, y)
        pixel.hsv = (self.hue, 1, 1)

        intensity = 1.0
        for elt in self.tail:
            intensity = intensity - .2
            pixel = self.wall.pixel(elt[0], elt[1])
            pixel.hsv = (self.hue, 1, intensity)

        self.wall.draw()
        time.sleep(.01)
        self.wall.clear()

    def run(self):
        x_min = 0
        x_max = 7
        y_min = 0
        y_max = 7

        while x_max > x_min:
            for x in range(x_min, x_max + 1):
                self.draw(x, y_min)
            for y in range(y_min, y_max + 1):
                self.draw(x_max, y)
            for x in range(x_max, x_min - 1, -1):
                self.draw(x, y_max)
            for y in range(y_max, y_min, -1):
                self.draw(x_min, y)

            x_min = x_min + 1
            x_max = x_max - 1
            y_min = y_min + 1
            y_max = y_max - 1
    
class Test(Effect):
    def _init(self, kw):
        self.flow = 0
        self.v = [0.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 0.0]
        self.hue = random.random()
        self.start_time = time.time()

    def run(self):
        while (time.time() - self.start_time) < 10:
            for i in range(7, -1, -1):
                for j in range(7, -1, -1):
                    pixel = self.wall.pixel(i, j)
                    pixel.hsv = (self.hue, 1, 1)
                    self.hue += .015
                time.sleep(.15)
                self.wall.draw()

            self.wall.clear()
            
            for i in range(0,8):
                for j in range(0,8):
                    pixel = self.wall.pixel(i, j)
                    pixel.hsv = (self.hue, 1, 1)
                    self.hue -= .015
                time.sleep(.15)
                self.wall.draw()

            self.wall.clear()

def effects():
    return [Mondrian, Pinwheel, Bounce, Twinkle, Rain]
