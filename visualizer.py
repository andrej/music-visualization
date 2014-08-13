"""
Visualizer Base Class
"""

import cairo

class Visualizer:
    
    analyzer = None
    surface = None
    context = None
    time = None
    properties = {}
    
    
    def __init__(self, analyzer, surface, time):
        self.analyzer = analyzer
        self.surface = surface
        self.context = cairo.Context(self.surface)
        self.time = time
        self.properties = {}
        # Convenience variables
        self.a = self.analyzer
        self.s = self.surface
        self.c = self.context
        self.t = self.time
        self.p = self.properties
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
    
    
    def draw(self):
        """
        Subclasses should overwrite this drawing function and do work on the
        surface.
        """
        return 0
    
    
    def setup(self):
        """
        Subclasses can use this function to some initialization if needed.
        """
        return 0
    
    
    def update_property(self, property_i, change):
        """
        Subclasses can use this function to trigger code when a property is 
        changed.
        """
        return 0