import serial
import time

class DummyPort(object):
    def __init__(self, debug=False):
        self.debug = debug

    def close(self):
        if self.debug:
            print "Closing DummyPort"
        
    def send(self, msg):
        if self.debug:
            print "send => %s" % msg.strip()

    def recv(self):
        if self.debug:
            print "recv => NULL (DummyPort)"
        return ''
    
    def reset(self, pause=2):
        if self.debug:
            print "Resetting DummyPort"

    def in_waiting(self):
        if self.debug:
            print "in_waiting() returning 0 (DummyPort)"
        return 0

    def poll(self):
        if self.debug:
            print "poll() (DummyPort)"

    def wait_for_ack(self, ack='K', timeout=20):
        return

class Arduino:
    def __init__(self, port, baud=115200, debug=False):
        self.debug = debug
        self.port = serial.Serial(port, baud)
        
    def send(self, msg):
        if self.port:
            self.port.write(msg)
        if self.debug:
            msg = [hex(ord(x)) for x in msg]
            msg = str.join(', ', msg)
            print "send => %s" % msg.strip()

    def recv(self):
        msg = ''
        while self.port.inWaiting():
            msg += self.port.read()
        msg = msg.strip()
        if not msg:
            return ''
        if self.debug:
            print "recv <= %s" % msg.strip()
        return msg
    
    def reset(self, timeout=2):
        self.port.setDTR(1)
        time.sleep(.3)
        self.port.setDTR(0)
        time.sleep(.3)
        self.wait_for_ack("R")

    def wait_for_ack(self, ack='K', timeout=20):
        ts = time.time()
        while 1:
            msg = self.recv()
            if msg == ack:
                break
            now = time.time()
            if (now - ts) > timeout:
                raise ValueError, "Timeout waiting for ack!"

    def in_waiting(self):
        return self.port.inWaiting()

    def poll(self):
        while (not self.in_waiting()):
            pass
