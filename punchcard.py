"""
Explode Visualisation
"""

import cairo
import visualizer
import animation
import helpers
import math

class PunchcardVisualizer(visualizer.Visualizer):
    
    
    def setup(self):
        
        self.freq_bins = \
            self.properties[0] = ['Log / Lin / All', 0, 1]
        self.freq_min = \
            self.properties[1] = ['Min. Frequency',   200,   100]
        self.freq_max = \
            self.properties[2] = ['Max. Frequency', 20000, 10000]
        self.freq_steps = \
            300
        self.log_scale_min = \
            self.properties[3] = ['Log Power Min',   1.001] # so that you can't set it to 0
        self.log_scale_max = \
            self.properties[4] = ['Log Power Max',  10]
        self.power_avg = \
            self.properties[5] = ['Add / Avg', 0, 1]
        self.history_len = \
            8 #40
                
        self.pixels = [[(0,0.0)] * self.freq_steps] * self.history_len
        self.col_bg = cairo.SolidPattern(0, 0, 0)
        self.col_power_curve = cairo.SolidPattern(0.5, 0.6, 1, 0.2)
        self.col_power_total = cairo.SolidPattern(0.5, 0.8, 1, 0.3)
        
        return
    
    
    def draw(self):
        
        power_avg = False
        if(self.power_avg[1] == 1):
            power_avg = True
        
        if(self.freq_bins[1] == 0):
            powers = self.a.list_freq_bin_powers(
                self.a.logarithmic_bins(
                    self.freq_min[1], self.freq_max[1], self.freq_steps, 2
                ),
                power_avg
            )
            self.freq_steps = 100
        elif(self.freq_bins[1] == 1):
            powers = self.a.list_freq_bin_powers(
                self.a.linear_bins(
                    self.freq_min[1], self.freq_max[1], self.freq_steps
                ),
                power_avg
            )
            self.freq_steps = 100
        else:
            powers = self.a.list_freq_powers()
            self.freq_steps = len(powers)
        
        self.pixels.pop()
        self.pixels.insert(0, powers)
        
        self.c.set_source(self.col_bg)
        self.c.paint()
             
        for row_i, row_pixels in enumerate(self.pixels):
            for pixel_i, pixel in enumerate(row_pixels):
                pixel = self.a.logarithmic_scale(
                    val=pixel[1],
                    log_min=self.log_scale_min[1],
                    log_max=self.log_scale_max[1]
                )
                fac = 1-(float(row_i)/self.history_len)
                color = cairo.SolidPattern(fac*pixel, fac*pixel, fac*pixel, 1.0)
                w = self.w/self.freq_steps
                h = self.h/self.history_len
                x = pixel_i * w
                y = (self.h/self.history_len)*row_i
                self.c.rectangle(x, y, w, h)
                self.c.set_source(color)
                self.c.fill()
            #
        
        self.draw_scale()
        
        N = len(self.a.freq_powers[1:-1])+1
        powers = [x*N for x in self.a.freq_powers[1:-1]]
        total_power = (1.0/N)*math.sqrt(sum(powers)) # rms        
        x = self.w*total_power
        y = self.a.logarithmic_scale(
            val=total_power,
            in_min=0,
            in_max=1.0,
            out_min=self.h-1,
            out_max=0,
            log_min=self.log_scale_min[1],
            log_max=self.log_scale_max[1]
        )
        self.c.rectangle(x-3, y-3, 6, 6)
        self.c.set_source(self.col_power_total)
        self.c.fill()
        
        return
    
    
    def draw_scale(self):
        
        for x in range(0, self.w-1):
            y = self.a.logarithmic_scale(
                val=x,
                in_min=0,
                in_max=self.w-1,
                out_min=self.h-1,
                out_max=0,
                log_min=self.log_scale_min[1],
                log_max=self.log_scale_max[1]
            )
            self.c.rectangle(x-1, y-1, 2, 2)
        
        self.c.set_source(self.col_power_curve)
        self.c.fill()
        
        return