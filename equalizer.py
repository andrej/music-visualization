"""
Equalizer Visualisation
"""

import cairo
import visualizer
import animation
import helpers

class EqualizerVisualizer(visualizer.Visualizer):
    
    def setup(self):
        self.color_bg_1 = cairo.SolidPattern(1.0, 1.0, 1.0, 1.0)
        self.color_bg_2 = cairo.SolidPattern(0.9, 0.9, 0.9, 1.0)
        self.color_fg_1 = cairo.SolidPattern(0.0, 0.0, 0.0, 1.0)
        self.color_fg_2 = cairo.SolidPattern(1.0, 0.0, 0.0, 0.5)
        self.color_fg_3 = cairo.SolidPattern(0.0, 0.0, 1.0, 0.5)
        self.freq_min = 200
        self.freq_max = 20000
        self.freq_num = 20
        self.max_powers = [
            (0, self.t.tell())
        ] * self.freq_num
        self.max_decay = 1
        self.duration = 2
    
    def draw(self):
        
        #freq_crop = int(self.p[0]*10)
        freq_crop = 0
        
        self.c.set_source(self.color_bg_1)
        self.c.paint()
        self.c.set_source(self.color_bg_2)
        self.c.rectangle(0, 0, self.w, 100)
        self.c.fill()
        
        powers = self.a.list_freq_bin_powers(
            self.a.logarithmic_bins(
                start=self.freq_min,
                stop=self.freq_max,
                num=self.freq_num,
                base=2
            )
        )[freq_crop:]
        
        average = self.a.freq_range_power(average=True)
        
        # freq bars
        for i, freq in enumerate(powers):
            power = self.a.logarithmic_scale(freq[1], log_min=0.1, log_max=10)
            max_power_t = self.t.tell()-self.max_powers[i][1]
            max_power = (1-helpers.accel_decel(max_power_t, self.duration))\
                *self.max_powers[i][0]
            if power > max_power or max_power_t > self.duration:
                self.max_powers[i] = (
                    power,
                    self.t.tell()
                )
            w = self.w/float(self.freq_num)
            x = i*w
            # black freq bar
            y = self.h-power*(self.h-100)
            h = self.h-y
            self.c.rectangle(x, y, w, h)
            self.c.set_source(self.color_fg_1)
            self.c.fill()
            # red max bar
            y = self.h-max_power*(self.h-100)-10
            h = 10
            self.c.rectangle(x, y, w, h)
            self.c.set_source(self.color_fg_2)
            self.c.fill()

        y = self.h-average*(self.h-100)-10
        h = 10
        self.c.rectangle(0, y, self.w, h)
        self.c.set_source(self.color_fg_3)
        self.c.fill()
        
        return
            