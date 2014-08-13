"""
Explode Visualisation
"""

import cairo
import visualizer
import animation
import helpers

class ExplodeVisualizer(visualizer.Visualizer):
    
    def setup(self):
        self.freq_min = 200
        self.freq_max = 20000
        self.freq_steps = 200
        self.pixel_height = 7
        self.y_resolution = 1
        self.pixels = [[(0,0.0)] * self.freq_steps] * int((self.h/2)/self.pixel_height*self.y_resolution)
        return
        
    def draw(self):
        
        '''
        powers = [
            self.a.logarithmic_scale(x[1], log_min=1, log_max=90) for x in 
            self.a.list_freq_bin_powers(
                self.a.logarithmic_bins(
                    start=self.freq_min,
                    stop=self.freq_max,
                    num=self.freq_steps,
                    base=2
                )
            )
        ]'''
        
        '''powers = [
            x[1] for x in self.a.list_freq_bin_powers(
                self.a.linear_bins(
                    start=self.freq_min,
                    stop=self.freq_max,
                    num=self.freq_steps
                )
            )
        ]'''
        
        powers = self.a.list_freq_powers()
        '''powers = [
            x[1] for x in self.a.list_freq_powers()
        ]'''       
        if(len(powers)>10):
            #print powers[10]
            self.freq_steps = len(powers)
        
        self.pixels.pop()
        self.pixels.insert(0, powers)
        
        num_rows = (self.h/2)/self.pixel_height # TODO rename this var
        
        start_v = 0.5
        accel = 2 * (1 - start_v)
            
        bg = cairo.SolidPattern(0, 0, 0)
        #self.c.rectangle(0, 0, self.w, self.h)
        self.c.set_source(bg)
        self.c.paint() 
            
        for row_i, row_pixels in enumerate(self.pixels):
            for pixel_i, pixel in enumerate(row_pixels):
                pixel = pixel[1]
                fac = 1-(float(row_i*(1.0/self.y_resolution)) / (float(self.h/2)/self.pixel_height))
                if row_i > 2:
                    fac *= 0.75
                else:
                    fac = 1
                color = cairo.SolidPattern(
                    fac*pixel, fac*pixel, fac*pixel, 1.0
                )
                t = ((float(row_i*(1.0/self.y_resolution)))/num_rows)
                disp = start_v * t + 0.5 * accel * (t**2)
                
                w = self.w/2.0/self.freq_steps
                h = self.pixel_height
                x = pixel_i * w
                y = self.h/2 - disp*(self.h/2)
                self.c.rectangle(x, y, w, h)
                # mirror
                '''self.c.rectangle(x, self.h-y-h, w, h)
                self.c.rectangle(self.w-x-w, y, w, h)
                self.c.rectangle(self.w-x-w, self.h-y-h, w, h)'''
                self.c.set_source(color)
                self.c.fill()
                
        return
        
        