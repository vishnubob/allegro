import random
import time
import colorsys
from allegro import FadeIter

from effects import Effect

class Pong(Effect):

    def moveBall(self, ballLoc):
        ball = ballLoc
        ball[0] = ball[0] + ball[2]
        ball[1] = ball[1] + ball[3]

        if (ball[0] + ball[2]) < 0:
            # bounced off the left wall
            ball[0] = 0
            # the velocity was negative, so make it positive
            ball[2] = random.choice((1, 2))
            ball[4] = random.random()

        if (ball[0] + ball[2]) > 7:
            # bounced off the right wall
            ball[0] = 7
            # the velocity was positive, so make it negatve
            ball[2] =  random.choice((-1,-2))
            ball[4] = random.random()

        if (ball[1] + ball[3]) < 0:
            # bounced off the top wall
            ball[1] = 0
            # the velocity was negative, so make it positive
            ball[3] = random.choice((1, 2))
            ball[4] = random.random()

        if (ball[1] + ball[3]) > 7:
            # bounced off the bottom wall
            ball[1] = 7
            # the velocity was positive, so make it negatve
            ball[3] = random.choice((-1,-2))
            ball[4] = random.random()

        return ball

    def run(self):
        # ball has a current position, and direction, color
        self.ball = [random.randint(0, 8), random.randint(0,8), random.choice((-2,-1,1,2)), random.choice((-2,-1,1,2)), random.random()]
        i = 0
        while i < 1000:
            self.ball = self.moveBall(self.ball)
            i = i + 1
            pixel = self.wall.pixel(self.ball[0],self.ball[1])
            pixel.hsv = (self.ball[4], 1, 1)
            time.sleep(0.5)
            self.wall.draw()
            self.wall.clear()


def effects():
    return [Pong]
