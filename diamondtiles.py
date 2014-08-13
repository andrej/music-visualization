"""
Diamond-shaped Tile Animation With Blob Expanding From Center
"""

import cairo
import math
import colorsys
import numpy
import visualization

class DiamondTiles(visualization.Visualization):
    
    # General Options
    log_base = 10
    log_min = 10**-2
    log_max = 10**3
    
    # Colors
    empty_color = cairo.SolidPattern(0,0,0,1)
    #bg_sprite_surface = cairo.ImageSurface.create_from_png(
    #    '../Footage/sunset-sprite.png'
    #)
    #bg_sprite_size = (640, 360, 1, 69)
    bg_imgs = (0, 139)
    
    # Tile Options
    tiles = []
    num_x_tiles = 20
    num_y_tiles = 11
    tile_shape = 'rectangle' # rectangle, diamond or circle
    
    # Moving backgorund options
    mbg_min = 0
    mbg_max = 139
    mbg_num = 10
    mbg_freq_range = (200, 20000)
    mbg_source_file = '../Footage/sunset-{0:d}.png'
    mbg_vals = [0] * 11

    
    # Blob options
    freq_ray_range = (400, 10000)
    num_freq_rays = 4
    min_blob_radius = 1
    max_blob_radius = 5
    min_blob_hue = 1.0
    max_blob_hue = 0.625
    mirror = True
    offset_angle = math.pi
      
    
    def draw(self):
        self.a.analyze(A_weighting=True)
        self.empty_tiles()
        self.moving_background()
        #self.blob()
        self.draw_tiles()
    
    
    def empty_tiles(self):
        self.tiles = [self.empty_color]*self.num_x_tiles*self.num_y_tiles
        return 0
    
    
    def set_tile(self, x, y, pattern=None):
        if (y*self.num_x_tiles+x) >= len(self.tiles) or x+y < 0:
            return 1
        self.tiles[int(y*self.num_x_tiles+x)] = pattern
        return 0
    
    
    def draw_tiles(self):
        w = self.image_width / self.num_x_tiles
        h = self.image_height / self.num_y_tiles
        x = 0
        while x < self.num_x_tiles:
            y = 0
            while y < self.num_y_tiles:
                if self.tile_shape == 'rectangle':
                    self.c.rectangle(x*w, y*h, w, h)
                elif self.tile_shape == 'diamond':
                    self.c.move_to(x*w-0.5*w, y*h+0.5*h)
                    self.c.line_to(x*w+0.5*w, y*h-0.5*h)
                    self.c.line_to(x*w+1.5*w, y*h+0.5*h)
                    self.c.line_to(x*w+0.5*w, y*h+1.5*h)
                elif self.tile_shape == 'circle':
                    self.c.arc(x*w+(w/2.0), y*h+(h/2.0), h/2.0-2, 0, 2*math.pi)
                    pass
                pattern = self.tiles[y*self.num_x_tiles+x]
                self.c.set_source(pattern)
                self.c.fill()
                y += 1
            x += 1
        return 0
    
    
    def rectangle(self, pattern, x, y, w=1, h=1):
        print (x, y, w, h)
        for iy in range(0, int(h)):
            for ix in range(0, int(w)):
                self.tiles[int((iy+y)*self.num_x_tiles+ix+x)] = pattern
        return 0
    
    
    def arc(self, pattern, x, y, r, a1, a2):
        pass
    
    
    def diamond(self, pattern, x, y, s):
        for y in range(0, s):
            for x in range(0, s):
                pass
        pass
    
    
    def moving_background(self):
        self.mbg_vals.append(
            self.a.logarithmic_scale(
                val=self.a.dominant_freq(
                    self.mbg_freq_range[0],
                    self.mbg_freq_range[1]
                )[0],
                in_min=self.mbg_freq_range[0],
                in_max=self.mbg_freq_range[1],
                out_min=self.mbg_min,
                out_max=self.mbg_max,
                base=2,
                log_min=10**-2,
                log_max=10**1
            )
        )
        #i=0
        for i in range(0, self.mbg_num):
            pattern_n = int(self.mbg_vals[len(self.mbg_vals)-i-1])
            print pattern_n
            pattern_surface = cairo.ImageSurface.create_from_png(
                self.mbg_source_file.format(pattern_n)
            )
            #pattern_context = cairo.Context(pattern_surface)
            #pattern_context.scale(1.0/)
            #pattern_context.flush()
            pattern = cairo.SurfacePattern(pattern_surface)
            self.rectangle(
                pattern,
                i*(self.num_x_tiles/self.mbg_num),
                0,
                self.num_x_tiles/self.mbg_num,
                self.num_y_tiles
            )
        return 0
    
    
    def random_sparkles(self):
        pass
    
    
    def blob(self, x, y, max_radius, min_radius=0, freqs=()):
        # parametric circle equations:
        # x = a + r*cos(angle)
        # y = b + r*sin(angle)
        # (a, b): center point
        # t: angle from 0 to 2*pi
        return
        powers = self.a.list_freq_bin_powers(
            bins=self.a.logarithmic_bins(
                start=self.freq_ray_range[0],
                stop=self.freq_ray_range[1],
                num=self.num_freq_rays,
                base=2
            )
        )
        rays = []
        i = 0
        for freqs, power in powers:
            radius = self.a.logarithmic_scale(
                power,
                out_min=self.min_blob_radius,
                out_max=self.max_blob_radius,
                base=self.log_base,
                log_min=self.log_min,
                log_max=self.log_max
            )
            color = colorsys.hsv_to_rgb(
                self.a.logarithmic_scale(
                    power, 
                    out_min=self.min_blob_hue,
                    out_max=self.max_blob_hue,
                    base=self.log_base,
                    log_min=self.log_min,
                    log_max=self.log_max
                ),
                1.0,
                0.8
            )
            rays.append((i, radius, color))
            i += 1
        a = self.num_x_tiles/2
        b = self.num_y_tiles/2
        if not self.mirror:
            ray_angle_inc = 2*math.pi / float(len(rays))
        else:
            ray_angle_inc = math.pi / float(len(rays))
        ray_angle = self.offset_angle
        for i, radius, color in rays:
            r = 1
            while r < radius:
                angle_inc = 1.0/(r*2) # just a small enough (too small)
                                      # angle increment to fill everything
                t = 0
                while t <= ray_angle_inc:
                    x = int(a + r*math.cos(t+ray_angle))
                    y = int(b + r*math.sin(t+ray_angle))
                    self.set_tile(x, y, color)
                    if self.mirror:
                        self.set_tile(
                            (self.num_x_tiles)-x-1,
                            (self.num_y_tiles)-y-1, 
                            color
                        )
                    t += angle_inc
                r += 1
            ray_angle += ray_angle_inc
        return 0