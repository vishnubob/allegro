#!/usr/bin/python
import os
import sys
import time
import random
import traceback
from subprocess import *

#capture = 'fswebcam /tmp/1.jpg'
mtrack_cmd = '/home/ghall/bin/motiontrack -s 9 --sectorsize=20 %s %s'
#mtrack_cmd = '/home/ghall/bin/motiontrack %s %s'
capture_cmd = 'uvccapture -d/dev/video%d -o%s'

class DebugWatcher(object):
    def vector(self):
        time.sleep(random.random())
        return (random.choice([1, -1]), random.random())

class Watcher(object):
    def __init__(self):
        if not filter(lambda x: x.find("video") != -1, os.listdir("/dev")):
            print "You have no video devices mounted."
            print "Did you mean to pass -R?"
            sys.exit(1)

    def mtrack(self, cam):
        fn1 = "/tmp/cam-%d_1.jpg" % cam
        fn2 = "/tmp/cam-%d_2.jpg" % cam
        cmd = capture_cmd % (cam, fn1)
        cmd = cmd.split(' ')
        if not os.path.exists(fn1):
            proc = Popen(cmd)
            proc.wait()
        os.rename(fn1, fn2)
        proc = Popen(cmd)
        proc.wait()
        cmd = mtrack_cmd % (fn1, fn2)
        cmd = cmd.split(' ')
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        line = proc.stdout.readline()
        try:
            val = int(line.strip())
        except KeyboardInterrupt:
            raise
        except ValueError:
            val = 0
        return val

    def watch(self):
        return map(bool, (self.mtrack(1), self.mtrack(2)))

    def _vector(self, timeout=0):
        start = time.time()
        ts = start
        while 1:
            try:
                res = self.watch()
            except:
                traceback.print_exc()
                continue
            if sum(map(int, res)):
                return res
            if timeout and ((ts - start) > timeout):
                break
            ts = time.time()
        return (False, False)
    
    def vector(self, attention_span=.7):
        print time.strftime("%c")
        print "Watching..."
        orig_evd = self._vector()
        vector1_ts = time.time()
        orig_evd_cnt = sum(map(int, orig_evd))
        if orig_evd_cnt == 2:
            print "simul trigger"
            return (2, 0)
        elif orig_evd_cnt == 1:
            accept_index = (1, 0)[orig_evd.index(True)]
            loop_ts = time.time()
            time_lapse = loop_ts - vector1_ts
            while True:
                sec_evd = self._vector(attention_span - time_lapse)
                if sec_evd[accept_index]:
                    if orig_evd[0]:
                        print "-->", time_lapse
                        return (1, time_lapse)
                    else:
                        print "<--", time_lapse
                        return (-1, time_lapse)
                if time_lapse > attention_span:
                    print "got bored"
                    return (0, [-1, 1][orig_evd.index(True)])
                else:
                    loop_ts = time.time()
                    time_lapse = loop_ts - vector1_ts

