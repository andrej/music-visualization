#!/usr/bin/env python2.7

"""
Test the helper functions
"""

import cairo
import cairowindow
import helpers

def loop():
    global surface, window
    w = surface.get_width()
    h = surface.get_height()
    ctx = cairo.Context(surface)
    
    bg = cairo.SolidPattern(1.0, 1.0, 1.0, 1)
    fg = cairo.SolidPattern(0, 0, 0, 0.5)
    ctx.set_source(bg)
    ctx.paint()
    
    ctx.move_to(0, h)
    for x in range(0, w):
        y = h-helpers.linear((x/float(w)), 0, h)
        ctx.line_to(x, y)
    
    ctx.move_to(0, h)
    for x in range(0, w):
        y = h-helpers.exponential((x/float(w)), 0, h, base=2)
        ctx.line_to(x, y)
    
    ctx.move_to(0, h)
    for x in range(0, w):
        y = h-helpers.logarithmic((x/float(w)), 0, h, base=2*(20000-20))
        ctx.line_to(x, y)
    
    ctx.move_to(0, h)
    for x in range(0, w):
        y = h-helpers.power((x/float(w)), 0, h, exponent=3)
        ctx.line_to(x, y)
    
    ctx.set_source(fg)
    ctx.set_line_width(2)
    ctx.stroke()
    window.refresh()
    return

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 360)
window = cairowindow.CairoWindow(surface)
window.loop(callbacks=[loop])