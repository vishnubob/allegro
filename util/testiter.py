from allegro import *
from arduino import *

def init(port, length, debug=False):
    port = "/dev/ttyUSB0"
    hwport = arduino.Arduino(port, debug=debug)
    chain = Chain(hwport)
    hwport.reset(2)
    chain.length = length
    chain.clear()
    return chain

port = '/dev/ttyUSB0'
chain = init(port, 2)
chain2 = chain.copy()
while 1:
    for clr in range(3):
        chain2.clear(False)
        chain2[0][clr] = 1023
        chain2[1][(clr+2) % 3] = 1023
        for val in FadeIter(chain, chain2, 5):
            pass
        swap = chain2
        chain2 = chain
        chain = swap

