"""
Time-based animation of values
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
    
    
    def tell(self):
        if not self.pause_time:
            return self.now()-self.start_time
        else:
            return self.pause_time-self.start_time
    
    
    def set(self, time=0):
        self.unpause()
        self.start_time = self.time-time
    
    
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
    

class AnimatedValue:
    
    start_value = 0
    end_value = 1
    duration = 1

    def __init__(self, start=0, end=1, duration=1):
        self.start_value = start
        self.end_value = end
        self.duration = duration
    
    
    def constant_velocity(self, t=0):
        return (
            self.start_value +
            (self.end_value-self.start_value)/float(self.duration)*t
        )
    
    
    def constant_acceleration(self, t=0, initial_velocity=0):
        a = 2*(self.end_value-self.start_value)/float(self.duration**2)
        return (
            self.start_value + initial_velocity*t + 0.5*a*t**2
        )
    
    
    def accel_decel(self, t=0, initial_velocity=0):
        a = 4*(self.end_value-self.start_value)/float(self.duration**2)
        # (double acceleration because we'll decelerate again!)
        if t <= self.duration/2.0: # first half accelerates
            return (
                self.start_value + initial_velocity*t + 0.5*a*t**2
            )
        if t > self.duration/2.0: # second half decelerates
            t0 = self.duration/2.0 # starting off with x0 and v0 of middle
            return (
                self.start_value + initial_velocity*t0 + 0.5*a*t0**2
                + (initial_velocity+a*t0)*(t-t0)
                + 0.5*-a*(t-t0)**2
            )