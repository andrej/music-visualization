"""
Circle visualizer
"""

import math
import colorsys

import cairo
import visualizer
import helpers

class CircleVisualizer(visualizer.Visualizer):
    
    
    def setup(self):
        now = self.t.tell()
        self.num_circles = 3
        self.num_subsections = 3 # mirrored, so twice as many
        self.circle_max_vals=[
                [(0, self.t.tell())]*(self.num_subsections**(i+1))
            for i in range(0, self.num_circles)]
        self.max_radius = 0.5*self.w
        self.min_radius = 0.05*self.h
        self.hue = 0
        self.bg_pattern = cairo.SolidPattern(1, 1, 1)
        self.angle_offset = -math.pi
        self.duration = 0.5
        self.min_freq = 800
        self.max_freq = 8000
        self.freq_base = 10000
        self.mirrored = True
        return 0
    
    
    def draw(self):
        self.hue = self.t.tell()/10.0
        self.c.set_source(self.bg_pattern)
        self.c.paint()
        for circle_i in range(0, self.num_circles):
            circle_i = self.num_circles-1-circle_i
            num_subsections = self.num_subsections**(circle_i+1)
            powers = self.a.list_freq_bin_powers(
                bins=self.a.logarithmic_bins(
                    start=self.min_freq, stop=self.max_freq,
                    num=num_subsections
                )
            )
            for subsection_i in range(0, num_subsections):
                val = helpers.logarithmic(
                    powers[subsection_i][1],
                    base=self.freq_base
                )
                max_val_t = self.t.tell()\
                        -self.circle_max_vals[circle_i][subsection_i][1]
                max_val = (1.0-helpers.accel_decel(max_val_t, self.duration))\
                        * self.circle_max_vals[circle_i][subsection_i][0]
                if val > max_val or max_val_t < 0 or max_val_t > self.duration:
                    self.circle_max_vals[circle_i][subsection_i] = (
                        val,
                        self.t.tell()
                    )
                else:
                    val = max_val
                min_r = self.min_radius/float(self.num_circles)*(circle_i)
                max_r = self.max_radius/float(self.num_circles)*(circle_i+1)
                r = (max_r-min_r)*val+min_r
                subsection_angle = (2*math.pi)/num_subsections
                if self.mirrored:
                    subsection_angle /= 2
                angle_1 = subsection_angle*subsection_i\
                    + self.angle_offset
                angle_2 = angle_1+subsection_angle
                color_vals = colorsys.hsv_to_rgb(
                    self.hue+(1.0/num_subsections*subsection_i),
                    1,
                    0.8/(self.num_circles-1)*circle_i,
                )
                color = cairo.SolidPattern(color_vals[0], color_vals[1],
                    color_vals[2])
                self.c.move_to(self.w/2.0, self.h/2.0)
                self.c.arc(self.w/2.0, self.h/2.0, r, angle_1, angle_2)
                if self.mirrored:
                    self.c.move_to(self.w/2.0, self.h/2.0)
                    self.c.arc(self.w/2.0, self.h/2.0, r, math.pi+angle_1, \
                         math.pi+angle_2)
                self.c.set_source(color)
                self.c.fill()
        return 0