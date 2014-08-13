"""
Raindrops Visualizer
"""

import math
import colorsys

import numpy
import cairo
import visualizer
import timemanager
import helpers

import random

class RaindropsVisualizer(visualizer.Visualizer):
    
    
    def setup(self):
        self.rt = timemanager.TimeManager(main=self.t)
        self.min_freq = 800
        self.max_freq = 8000
        self.hue = 0
        #self.bg_pattern = cairo.LinearGradient(0, 0, 0, self.h)
        #self.bg_color_stops = [(1, self.t.tell())]
        self.vignette_pattern = cairo.LinearGradient(0, 0, 0, self.h)
        self.vignette_pattern.add_color_stop_rgba(0, 0, 0, 0, 0.0)
        self.vignette_pattern.add_color_stop_rgba(0.5, 0, 0, 0, 0.0)
        self.vignette_pattern.add_color_stop_rgba(1, 0, 0, 0, 0.8)
        self.offset_top = self.h*0.05
        self.spacing = 5
        self.stroke_pattern = cairo.SolidPattern(0, 0, 0, 0.01)
        self.layers = [
            {
                'raindrops' : [],
                'cols' : 40,
                'threshold' : 0.01,
                'log_base' : 80,
                'freq_crop_bottom' : 0,
                'duration' : 3,
                'velocity' : 0.2,
                'hue_offset' : 0,
                'saturation' : 0,
                'value' : 1,
                'opacity' : 0.7
            },
            {
                'raindrops' : [],
                'cols' : 20,
                'threshold' : 0.25,
                'log_base' : 400,
                'freq_crop_bottom' : 0,
                'duration' : 1.5,
                'velocity' : 0.4,
                'hue_offset' : +0.1,
                'saturation' : 0.5,
                'value' : 1,
                'opacity' : 0.8
            },
            {
                'raindrops' : [],
                'cols' : 10,
                'freq_crop_bottom' : 0,
                'threshold' : 0.4,
                'log_base' : 400,
                'duration' : 1,
                'velocity' : 0.8,
                'hue_offset' : +0.2,
                'saturation' : 0.8,
                'value' : 1,
                'opacity' : 0.9
            }
        ]
        self.bg_history_len = 100
        self.bg_powers = [0] * self.bg_history_len
        self.r = 0.1*math.pi
        return 0
    
    
    def draw(self):
        self.hue = self.t.tell()/60.0
        self.generate_background()
        self.c.set_source(self.bg_pattern)
        self.c.paint()
        if self.t.interval(0.1):
            for layer in self.layers:
                self.add_raindrops(
                    layer['raindrops'], layer['cols'], layer['threshold'],
                    layer['freq_crop_bottom'], layer['log_base']
                )
        for layer in self.layers:
            self.draw_raindrops(
                layer['raindrops'], (self.w/float(layer['cols'])),
                layer['cols'], layer['duration'], layer['velocity'],
                layer['hue_offset'], layer['saturation'],
                layer['value'], layer['opacity'], layer['threshold']
            )
        self.draw_vignette()
        return 0
    
    
    def generate_background(self):
        current_power = self.a.freq_range_power(average=True)
        self.bg_powers.append(current_power)
        del self.bg_powers[0]
        val = numpy.average(
            self.bg_powers,
            weights=numpy.linspace(
                start=1.0/self.bg_history_len,
                stop=1.0,
                num=self.bg_history_len
            )
        )
        v = 0.2*helpers.logarithmic(val, base=10)
        self.bg_pattern = cairo.SolidPattern(v, v, v, 1.0)
        """
        if self.t.interval(0.3):
            current_power = self.a.freq_range_power()
            val = helpers.logarithmic(current_power, base=400)
            self.bg_color_stops.append((val, self.t.tell()))
        self.bg_pattern = cairo.LinearGradient(0, 0, 0, 1.5*self.h)
        i = 0
        while i < len(self.bg_color_stops):
            stop = self.bg_color_stops[i]
            t = self.t.tell()-stop[1]
            if t < 0 or t > 6:
                del self.bg_color_stops[i]
                continue
            y = helpers.constant_acceleration(t, 3)
            color_val = colorsys.hsv_to_rgb(
                self.hue,
                0.3,
                0.1*stop[0]+0.2
            )
            self.bg_pattern.add_color_stop_rgb(
                y, color_val[0], color_val[1], color_val[2]
            )
            i += 1
        """
        return 0
    
    
    def add_raindrops(self, addto, cols, threshold, freq_crop_bottom=30, 
            log_base=600):
        powers = self.a.list_freq_bin_powers(
            bins = self.a.logarithmic_bins(
                start=self.min_freq, stop=self.max_freq, 
                num=cols+freq_crop_bottom+1
            )
        )[freq_crop_bottom:]
        for i, freq in enumerate(powers):
            val = helpers.logarithmic(freq[1], base=log_base)
            if val > threshold:
                addto.append((val, i, self.rt.tell()))
        return 0
    
    
    def draw_raindrops(self, raindrops, s, cols, duration, velocity,
            hue_offset, saturation, value, opacity, threshold):
        i = 0
        s -= 2*self.spacing
        while i<len(raindrops):
            raindrop = raindrops[i]
            t = self.rt.tell()-raindrop[2]
            if t < 0 or t > duration:
                del raindrops[i]
                continue
            if raindrop[0]-threshold > 0:
                op = helpers.logarithmic(
                    (raindrop[0]-threshold)/(1.0-threshold),
                    base=100
                )*opacity
            color_val = colorsys.hsv_to_rgb(
                self.hue + hue_offset, saturation, value
            )
            color = cairo.SolidPattern(
                color_val[0], color_val[1], color_val[2], op
            )
            x = raindrop[1]/float(cols)*self.w+self.spacing
            y = (self.h+s)*helpers.constant_acceleration(t, duration, velocity)\
                + self.offset_top
            self.raindrop(x, y, s, color)
            i += 1
        return 0
        
    
    def raindrop(self, x, y, s, color):
        self.c.arc(x, y, s, 0, 2*math.pi)
        self.c.set_source(color)
        self.c.fill_preserve()
        self.c.set_source(self.stroke_pattern)
        self.c.stroke()
        return 0
    
    
    def draw_vignette(self):
        self.c.set_source(self.vignette_pattern)
        self.c.rectangle(0, 0, self.w, self.h)
        self.c.fill()
        return 0