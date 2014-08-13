"""
Simple way of showing a cairo surface on a window using SDL.

It is very easy to show a window with a cairo surface on it using this module,
just by creating a new instance of the class. If you want more control,
initialize the SDL window and SDL renderer yourself and assign them to 
`cairoWindow.sdlWindow` and `cairoWindow.sdlRenderer` respectively. You can 
then still use `cairoWindow.refresh()` to copy the contents of the cairo
surface to the window.
"""

from ctypes import c_byte
import cairo
import sdl2


class CairoWindow:
    
    cairo_surface = None
    sdl_window = None
    sdl_renderer = None
    
    loop_running = False
    loop_iteration = 0
    loop_events = []
    loop_sleep = 1.0/30
    
    
    def open(self, cairo_surface=None, title="Cairo", position=(0,0), flags=0):
        """
        Open a window that shows the given cairo surface. The window is sized
        according to the cairo surface size. To keep the window open, make
        sure to run a loop (possibly with event handling); The window closes
        as the thread dies. For a simple loop, use `CairoWindow.loop()`.
        
        Arguments:
        cairo_surface   A cairo surface to render on the window
        title           Title that shows up in the window decoration
        position        Tuple giving window position `(x,y)`
        flags           SDL window flags OR'd together
        
        Returns:
        0               Success
        """
        
        if not sdl2.SDL_WasInit( sdl2.SDL_INIT_VIDEO ):
            sdl2.SDL_Init( sdl2.SDL_INIT_VIDEO )
        
        if cairo_surface:
            self.cairo_surface = cairo_surface
        self.show_window = True

        if not self.sdl_window:
            self.sdl_window = sdl2.SDL_CreateWindow(
                title,
                position[0],
                position[1],
                self.cairo_surface.get_width(), 
                self.cairo_surface.get_height(),
                flags
            )
            self.sdl_renderer = sdl2.SDL_CreateRenderer(
                self.sdl_window,
                -1,
                sdl2.SDL_RENDERER_ACCELERATED
            )
        
        sdl2.SDL_ShowWindow( self.sdl_window )
        self.refresh()
        
        return 0
    
    
    def close(self):
        """
        Close the window and free memory.
        """
        sdl2.SDL_DestroyWindow( self.sdl_window )
        sdl2.SDL_DestroyRenderer( self.sdl_renderer )
        sdl2.SDL_Quit()
        return 0
    
     
    def refresh(self):
        """
        Copy what is on the cairo surface to the SDL window.
        
        Returns:
        0       Success
        1       No cairo surface given to class
        2       No window or renderer available
        3       Unsupported pixel format on the cairo surface
        """
        if not self.cairo_surface:
            return 1
        if not self.sdl_window or not self.sdl_renderer:
            return 2
        if not self.cairo_surface.get_format() in (cairo.FORMAT_ARGB32, 
                cairo.FORMAT_RGB24):
            return 3
        self.cairo_surface.flush()
        pixel_data = self.cairo_surface.get_data()
        pixel_data_array = (c_byte*len(pixel_data)).from_buffer(pixel_data)
        surface = sdl2.SDL_CreateRGBSurfaceFrom(
            pixel_data_array,
            self.cairo_surface.get_width(),
            self.cairo_surface.get_height(),
            32, # RGB24 leaves upper 8 bits unused
            self.cairo_surface.get_stride(),
            0x00ff0000,
            0x0000ff00,
            0x000000ff,
            0x00000000 # No support for alpha right now!
        )
        texture = sdl2.SDL_CreateTextureFromSurface(self.sdl_renderer, surface)
        sdl2.SDL_FreeSurface(surface)
        sdl2.SDL_RenderClear(self.sdl_renderer)
        sdl2.SDL_RenderCopy(self.sdl_renderer, texture, None, None)
        sdl2.SDL_RenderPresent(self.sdl_renderer)
        sdl2.SDL_DestroyTexture(texture)
        return 0
    
    
    def loop(self, callbacks=[], handle_quit=True):
        """
        A simple main loop that keeps the window open for the time specified
        and executes given callbacks.
        
        Arguments:
        sleep       How long to sleep betweeen frames in seconds.
        callbacks   List of functions to execute every frame. Arguments:
                    1. `i` - The callback has been executed this many times
                    2. `events` - List of new `SDL_Event` structs
        handle_quit Wether to deal with quit events and close the window or do
                    nothing
        
        Returns:
        0           As soon as the loop ends (QUIT event or time over)
        """
        self.loop_running = True
        i = 0
        while self.loop_running:
            self.loop_iteration = i
            self.loop_events = []
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(event): # poll event copies to var event
                self.loop_events.append(event)
                if handle_quit and event.type == sdl2.SDL_QUIT:
                    self.loop_running = False
            for callback in callbacks:
                callback()
            if self.loop_sleep > 0:
                sdl2.SDL_Delay(int(self.loop_sleep*1000))
            self.refresh()
            i += 1
        self.close()
        return 0
    
    
    def __init__(self, *args, **kwargs):
        """
        Open a window that shows the given cairo surface. You can use the
        constructor as a shortcut for `open()`. Arguments are the same.
        """
        self.open( *args, **kwargs )
        