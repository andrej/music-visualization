"""
Tells the time in the context of the current visualization
"""

import time


class TimeManager:
    
    main = None # set a main time manager that manages the "now" time
    
    time = 0
    iteration = 0
    
    start_time = 0
    pause_time = None
    
    intervals = {} # contains info on how many times an interval has been repeated
    live = True
    fps = 30.0
    
    
    def __init__(self, main=None, live=True, fps=30.0):
        self.main = main
        self.live = live
        self.fps = fps
        self.start()
    
    
    def now(self):
        if self.main:
            return self.main.tell()
        else:
            if self.live:
                return time.time()
            else:
                return (1.0/self.fps)*self.iteration
    
    
    def tell(self, start_time=None):
        if not self.pause_time:
            return self.now()-self.start_time
        else:
            return self.pause_time-self.start_time
    
    
    def set(self, t=0):
        self.start_time += self.tell()-t
        return 0
    
    
    def frame(self):
        self.iteration += 1
        self.time = self.now()
        for interval in self.intervals:
            if self.intervals[interval][1]:
                self.intervals[interval][0] += 1
                self.intervals[interval][1] = False
        return 0
    
    
    def start(self):
        self.start_time = self.now()
        return 0
    
    
    def pause(self):
        self.pause_time = self.now()
        return 0
    
        
    def unpause(self):
        if not self.pause_time:
            return 1
        pause_length = self.now()-self.pause_time
        self.pause_time = None
        self.start_time += pause_length
        return pause_length
    
    
    def interval(self, interval=1):
        interval = float(interval)
        if not interval in self.intervals:
            self.intervals[interval] = [0, False]
        if self.tell()/interval > self.intervals[interval][0]:
            self.intervals[interval][1] = True
            return True
        return False