import random
import time
import colorsys
from allegro import FadeIter

class Effect(object):
    def __init__(self, wall, **kw):
        self.wall = wall
        self._init(kw)

    def _init(self, kw): pass
    def run(self): pass

class TestEffect(Effect):
    def _init(self, kw):
        self.start_time = time.time()

    def run(self):
        while (time.time() - self.start_time) < 10:
            hue = random.random()
            for i in range(self.wall.width):
                for j in range(self.wall.height):
                    pixel = self.wall.pixel(i, j)
                    pixel.hsv = (hue, 1, 1)
            self.wall.draw()
            time.sleep(1)
            self.wall.clear()
            hue = random.random()
            for i in range(self.wall.height):
                for j in range(self.wall.width):
                    pixel = self.wall.pixel(j, i)
                    pixel.hsv = (hue, 1, 1)
                    self.wall.draw()
                    time.sleep(.1)
                    self.wall.clear()

class MatrixEffect(Effect):
    """
    Visualize the classic green trickle down Matrix effect.

    TODO: generalize to any direction.
    """
    class Column(object):
        def __init__(self, wall):
            self.wall = wall
            self.cache = []
            # Tail must be at least 1 pixel long
            self.tail = max(1, random.randint(
                    self.wall.height / 2, self.wall.height * 2))
            # Get a position somewhere above the wall (so it can trickle down
            # onto the wall)
            self.pos = (random.randint(0, self.wall.width - 1),
                        random.randint(-(self.wall.height * 2), 0))
            self.green = random.randint(900, 1023)

        def step(self):
            """
            Advance the location of the head of the column and all pixels in the
            tail.
            """
            self.cache.append(self.pos)
            self.cache = self.cache[-self.tail:]
            self.pos = [self.pos[0], self.pos[1] + 1]

        def draw(self, wall):
            """
            Set the pixel colors in this column for this step.

            Returns the number of pixels making up this column that were
            actually within the scope of the wall.
            """
            draw_cnt = 0
            # Prepare the tail colors
            for idx, pos in enumerate(self.cache):
                pixel = wall.pixel(*pos)
                if pixel:
                    green = float(self.green) * (float(idx) / self.tail)
                    pixel.rgb = (0, green, 0)
                    draw_cnt += 1
            # Prepare the head color
            pixel = wall.pixel(*self.pos)
            if pixel:
                draw_cnt += 1
                pixel.pixel = (0, self.green, 0)
            return draw_cnt

    def _init(self, kw):
        self.speed = kw.get('speed', random.random())

    def run(self):
        # pick how many Matrix columns we'll draw
        col_cnt = random.randint(15, 30)
        cols = []
        for col_idx in range(col_cnt):
            col = self.Column(self.wall)
            cols.append(col)
        self.draw(cols)

    def draw(self, cols):
        """
        Draw the advancing columns until no parts of any columns are left on the
        wall.
        """
        timeout = 4
        drawing = 0
        while drawing or timeout:
            self.wall.clear()
            for col in cols:
                col.step()
                drawing += col.draw(self.wall)
            self.wall.draw()
            time.sleep(self.speed)
            if not drawing:
                timeout -= 1
            drawing = 0

class WindEffect(Effect):
    class Wisp(object):
        def __init__(self, wall, direction, on=False, **kw):
            self.wall = wall
            self.cache = []
            # Tail must be at least 1 pixel
            self.tail = kw.get('tail',
                               max(1, random.randint(int(self.wall.width * .5),
                                                     self.wall.width * 3)))
            if on:
                if direction == -1:
                    x = self.wall.width - 1
                else:
                    x = 0
                y = random.randint(0, self.wall.height - 1)
            else:
                if direction == -1:
                    x = random.randint(self.wall.width, self.wall.width * 2)
                else:
                    x = random.randint(-self.wall.width, 0)
                y = random.randint(-1, self.wall.height)

            self.pos = kw.get('pos', [x, y])
            self.vector = kw.get('vector', (direction, 0))

            self.hue = kw.get('hue', None)
            if not self.hue:
                if random.random() > .8:
                    rgb = random.choice(([0,0,1], [0,1,0], [0,1,1], [1,0,0], [1,0,1], [1,1,0], [1,1,1]))
                    hsv = colorsys.rgb_to_hsv(*rgb)
                    self.hue = hsv[0]
                else:
                    self.hue = random.random()

        def __str__(self):
            ret = [self.pos, self.vector, self.tail, self.hue]
            ret = str.join(', ', map(str, ret))
            return ret

        def step(self):
            """
            Advance the location of the head of the wisp and all pixels in the
            tail.
            """
            self.cache.append(map(int, self.pos))
            self.cache = self.cache[-self.tail:]
            if random.random() > .75:
                offset = random.choice((1, -1))
                if self.vector[1]:
                    self.pos[0] += offset
                else:
                    self.pos[1] += offset
            else:
                self.pos = [self.pos[axis] + self.vector[axis] for axis in range(2)]

        def draw(self, wall):
            """
            Set the pixel colors in this wisp for this step.

            Returns the number of pixels making up this wisp that were actually
            within the scope of the wall.
            """
            draw_cnt = 0
            for idx, pos in enumerate(self.cache):
                pixel = wall.pixel(*pos)
                if pixel:
                    val = (idx) / float(self.tail)
                    pixel.hsv = (self.hue, 1, val)
                    draw_cnt += 1
            pixel = wall.pixel(*self.pos)
            if pixel:
                draw_cnt += 1
                pixel.hsv = (self.hue, 1, 1)
            return draw_cnt

    def _init(self, kw):
        self.direction = kw.get('direction', random.choice([-1, 1]))
        self.speed = kw.get('speed', random.random())

    def run(self):
        self.speed = max(.01, min(.125, self.speed))
        wisp_cnt = random.randint(3, 8)
        wisps = []
        for wisp_idx in range(wisp_cnt):
            if wisp_idx == wisp_cnt - 1:
                wisp = self.Wisp(self.wall, self.direction, on=True)
            else:
                wisp = self.Wisp(self.wall, self.direction)
            wisps.append(wisp)
        self.draw(wisps)

    def draw(self, wisps):
        """
        Draw the advancing wisps until no parts of any wisps are left on the
        wall.
        """
        timeout = 4
        drawing = 0
        while drawing or timeout:
            self.wall.clear()
            for wisp in wisps:
                wisp.step()
                drawing += wisp.draw(self.wall)
            self.wall.draw()
            time.sleep(self.speed)
            if not drawing:
                timeout -= 1
            drawing = 0

class RotateEffect(Effect):
    Left = (-1, 0)
    Right = (1, 0)
    Down = (0, 1)
    Up = (0, -1)
    Horz = (Left, Right)
    Vert = (Up, Down)
    Axis = [Horz, Vert]

    def _init(self, kw):
        self.cursor = (random.randint(0, self.wall.width - 1),
                       random.randint(0, self.wall.height - 1))
        self.seed_dir_map()
        self.map_rotate()

    def seed_dir_map(self):
        # pick the first axis
        first_axis = random.randint(0, 1)
        second_axis = [1, 0][first_axis]
        first_dir = random.randint(0, 1)
        second_dir = random.randint(0, 1)
        third_dir = [1, 0][first_dir]
        fourth_dir = [1, 0][second_dir]
        self.dir_map = (self.Axis[first_axis][first_dir], self.Axis[second_axis][second_dir],
                        self.Axis[first_axis][third_dir], self.Axis[second_axis][fourth_dir])

    def add_vector(self, vector, step):
        next_vector = []
        for x in range(len(vector)):
            next_vector.append(vector[x] + step[x])
        return next_vector

    def clip_vector(self, vector):
        if vector[0] < 0 or vector[0] > self.wall.width - 1:
            return True
        if vector[1] < 0 or vector[1] > self.wall.height - 1:
            return True
        return False

    def debug_draw(self):
        canvas = []
        for y in range(self.wall.height):
            row = ['.'] * self.wall.width
            canvas.append(row)
        for pixel in self.draw_list:
            canvas[pixel[1]][pixel[0]] = '#'
            for row in canvas:
                print str.join('', row)
            print
            time.sleep(.03)

    def run(self):
        hue_step = 1 / float(self.wall.width * self.wall.height)
        offset = random.random()
        cnt = 0
        cache = []
        for pixel in self.draw_list:
            x = pixel[0]
            y = pixel[1]
            hue = ((hue_step * cnt) + offset) % 1.0
            cache.append((x, y, hue))
            self.wall.pixel(x, y).hsv = (hue, 1, 1)
            self.wall.draw()
            time.sleep(.02)
            cnt += 1
        wall = self.wall
        for pixel in cache:
            wall2 = wall.copy()
            wall2.pixel(pixel[0], pixel[1]).rgb = (0, 0, 0)
            fi = FadeIter(wall, wall2, .001)
            wall = wall2
            fi.run()

    def map_rotate(self):
        self.movement = []
        # how many times to step in a direction
        dir_step = 1
        # how many times we've stepped with this dir_step value
        dir_step_count = 1
        # current direction
        cur_dir = 1
        # seed the first two steps
        self.draw_list = []
        if not self.clip_vector(self.cursor):
            self.draw_list.append(self.cursor)
        self.cursor = self.add_vector(self.cursor, self.dir_map[0])
        if not self.clip_vector(self.cursor):
            self.draw_list.append(self.cursor)
        while 1:
            clip_count = 0
            # apply step
            for step in range(dir_step):
                self.cursor = self.add_vector(self.cursor, self.dir_map[cur_dir])
                if not self.clip_vector(self.cursor):
                    self.draw_list.append(self.cursor)
                else:
                    clip_count += 1
            # set the next direction
            cur_dir = (cur_dir + 1) % 4
            # increment the directional step counter
            dir_step_count = (dir_step_count + 1) % 2
            # if the counter is two, inc the step count
            if dir_step_count == 0:
                dir_step += 1
            if clip_count >= 16:
                break

class FadeRotateEffect(RotateEffect):
    def run(self):
        hue_step = 1 / float(self.wall.width * self.wall.height)
        cache_list = []
        cache_cnt = random.randint(5,15)
        offset_step = 1.0 / cache_cnt
        ttl = max(1.5, random.random() * 3) / cache_cnt
        offset = random.random()
        # prepare
        for cache_idx in range(cache_cnt):
            cache = []
            for cnt, pixel in enumerate(self.draw_list):
                x = pixel[0]
                y = pixel[1]
                hue = ((hue_step * cnt) + offset) % 1.0
                cache.append((x, y, hue))
                self.wall.pixel(x, y).hsv = (hue, 1, 1)
            cache_list.append(cache)
            offset += offset_step
        # draw
        wall = self.wall
        for cache in cache_list:
            wall2 = wall.copy()
            for pixel in cache:
                wall2.pixel(pixel[0], pixel[1]).hsv = (pixel[2], 1, 1)
            fi = FadeIter(wall, wall2, ttl)
            fi.run()
            wall = wall2
        wall2 = wall.copy(True)
        fi = FadeIter(wall, wall2, ttl)
        fi.run()

Effects = [MatrixEffect, WindEffect, RotateEffect, FadeRotateEffect]
import jesstess
Effects.extend(jesstess.effects())
