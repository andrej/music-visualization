"""
Helper functions to map values to functions.

Input values should be between 0 and 1. After being mapped to the portion of a
function described by x1 and x2 the return value will be between y1 and y2.

y1 and y2 are the minimum and maximum output values.
"""

import math

def linear(x, y1=0, y2=1):
    # y = ax+b
    return ((y2-y1))*x+y1
    

def exponential(x, y1=0, y2=1, base=2):
    return (
        (y2-y1)/float(base-1)
        *(base**x-1)
        +y1
    )


def logarithmic(x, y1=0, y2=1, base=2):
    return (
        (y2-y1)
        *math.log((base-1)*x+1, base)
        +y1
    )


def power(x, y1=0, y2=1, exponent=2):
    return(
        (y2-y1)*x**exponent+y1
    )


def scale_base(x1, x2, base):
    return (base*(x2-x1))
    
    
# Animation (Multiply return values of these functions with values to animate)

def constant_velocity(t=0, duration=1):
    return (1.0/float(duration)*t)


def constant_acceleration(t=0, duration=1, initial_velocity=0):
    a = 2/float(duration**2)
    return (initial_velocity*t + 0.5*a*t**2)


def accel_decel(t=0, duration=1, initial_velocity=0):
    a = 4/float(duration**2)
    # (double acceleration because we'll decelerate again!)
    if t <= duration/2.0: # first half accelerates
        return (initial_velocity*t + 0.5*a*t**2)
    if t > duration/2.0: # second half decelerates
        t0 = duration/2.0 # starting off with x0 and v0 of middle
        return (
            initial_velocity*t0 + 0.5*a*t0**2
            + (initial_velocity+a*t0)*(t-t0)
            + 0.5*-a*(t-t0)**2
        )