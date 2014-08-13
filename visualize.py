#!/usr/bin/env python2.7

import argparse
import struct
import ctypes

import sdl2
import pyaudio
import cairo

import audioanalyze
import timemanager
import cairowindow

import equalizer
import circle
import raindrops
import explode
import punchcard

main = None

class Main:
    
    live = True
    
    analyzer = None
    player = None
    surface = None
    window = None
    pa = None
    pa_audio_stream = None
    
    available_visualizers = [
        equalizer.EqualizerVisualizer,
        circle.CircleVisualizer,
        raindrops.RaindropsVisualizer,
        explode.ExplodeVisualizer,
        punchcard.PunchcardVisualizer
    ]
    current_visualizer = 0
    visualizers = []
        
    time = timemanager.TimeManager()
    paused = False
        
    audio_buffer_length = 1024 #2**8 # No. samples
    audio_buffer_pos = 0
    
    args = None
    
        
    def main(self):
        # COMMAND LINE INTERFACE
        arg_parser = argparse.ArgumentParser(
            description='Interactively display or render a music \
            visualization.'
        )
        arg_parser.add_argument('-i', '--wave_file', type=str, default='')
        arg_parser.add_argument('-x', '--width', type=int, default=640)
        arg_parser.add_argument('-y', '--height', type=int, default=360)
        arg_parser.add_argument('-o', '--output', type=str, default='')
        arg_parser.add_argument('-f', '--fps', type=int, default=30)
        arg_parser.add_argument('-v', '--visualizer', type=int, default=0)
        arg_parser.add_argument('-m', '--micin', type=bool, default=False)
        arg_parser.add_argument('-a', '--amplify', type=int, default=1)
        arg_parser.add_argument('-s', '--samprate', type=int, default=22000)
        arg_parser.add_argument('-l', '--fullscreen', type=bool, default=False)
        self.args = arg_parser.parse_args()
        if self.args.output != '':
            self.live = False
            self.time = timemanager.TimeManager(live=False, fps=self.args.fps)
        # TODO normalization
        # TODO only allow certain arguments with each other
        # SET UP AUDIO
        if not self.args.micin:
            self.analyzer = audioanalyze.AudioAnalyze(self.args.wave_file)
        else:
            self.analyzer = audioanalyze.AudioAnalyze()
        
        if self.live and not self.args.micin:
            self.player = audioanalyze.AudioAnalyze(self.args.wave_file)
            self.player.wave_read(frames=256)
            self.pa = pyaudio.PyAudio()
            self.pa_audio_stream = self.pa.open(
                rate=self.player.data_samplerate,
                format=pyaudio.paUInt8,
                channels=1,
                output=True,
                stream_callback=self.get_audio_loop() # yes that's correct
            )
        elif self.live and self.args.micin:
            self.pa = pyaudio.PyAudio()
            self.pa_audio_stream = self.pa.open(
                rate=self.args.samprate,
                format=pyaudio.paUInt8,
                channels=1,
                input=True,
                frames_per_buffer=1024, #int(self.args.samprate*(1.0/self.args.fps)),
                stream_callback=self.get_audio_loop()
            )
            self.analyzer.data_samplerate = self.args.samprate
            self.analyzer.data_framerate = self.args.samprate
            self.analyzer.data_sampwidth = 2**8
            self.analyzer.data_nchannels = 1
            
            
        
        # SET UP VIDEO
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.args.width, self.args.height
        )
        if self.live:
            self.window = cairowindow.CairoWindow(
                self.surface, title='Visualizer'
            )
            self.window.loop_sleep = 0.5/self.args.fps #0 # 1/25.0
        
        # SET UP VISUALIZERS
        self.visualizers = [None] * len(self.available_visualizers)
        if(len(self.available_visualizers) == 0):
            print "No visualizer available."
            return 1
        self.current_visualizer = self.args.visualizer
        if(self.current_visualizer > len(self.available_visualizers)):
            self.current_visualizer = 0
            print "Invalid visualizer: Using first."
        for i, visualizer in enumerate(self.available_visualizers):
            self.visualizers[i] = \
                visualizer(self.analyzer, self.surface, self.time)
            self.visualizers[i].setup()
        
        # SET UP FULLSCREEN
        if self.args.fullscreen:
            sdl2.SDL_SetWindowFullscreen(
                self.window.sdl_window,
                sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
            )
            #_bounds = sdl2.SDL_Rect()
            #sdl2.SDL_GetDisplayBounds(0, ctypes.byref(self._bounds))
        
        # START
        self.start()
        
        return 0
    
    
    def start(self):
        """Start up Video and Audio that was initialized"""
        if self.live:
            self.list_properties()
            self.pa_audio_stream.start_stream()
            self.time.start()
            self.window.loop(callbacks=[self.window_loop])
            self.stop()
        else:
            self.render()
        return 0
    
    
    def stop(self):
        if not self.live:
            return 1
        self.window.close()
        self.pa_audio_stream.stop_stream()
        self.pa_audio_stream.close()
        self.pa.terminate()
        self.window.loop_running = False
        return 0
    
        
    def pause(self):
        """Pause audio and video playback"""
        self.paused = True
        self.pa_audio_stream.stop_stream()
        self.time.pause()
        return 0
    
    def unpause(self):
        """Unpause audio and video playback"""
        self.paused = False
        self.pa_audio_stream.start_stream()
        self.time.unpause()
        return 0
    
    
    def seek(self, seekto=0.0):
        """Seek to the given time in seconds in the audio and video"""
        if seekto <= 0:
            seekto = 0
        elif seekto >= self.analyzer.wave_duration():
            return 1
        self.time.set(seekto)
        self.player.wave_seek(seekto)
        self.analyzer.wave_seek(seekto)
        return 0
    
    
    def update_property(self, keysym):
        key = keysym.sym
        inc = 1
        if keysym.mod & sdl2.KMOD_CTRL:
            inc *= 10
        elif keysym.mod & sdl2.KMOD_SHIFT:
            inc *= 0.1
        keymap = {
            sdl2.SDLK_q : (0, +inc),
            sdl2.SDLK_y : (0, -inc),
            sdl2.SDLK_w : (1, +inc),
            sdl2.SDLK_x : (1, -inc),
            sdl2.SDLK_e : (2, +inc),
            sdl2.SDLK_c : (2, -inc),
            sdl2.SDLK_r : (3, +inc),
            sdl2.SDLK_v : (3, -inc),
            sdl2.SDLK_t : (4, +inc),
            sdl2.SDLK_b : (4, -inc),
            sdl2.SDLK_z : (5, +inc),
            sdl2.SDLK_n : (5, -inc),
            sdl2.SDLK_u : (6, +inc),
            sdl2.SDLK_m : (6, -inc),
            sdl2.SDLK_i : (7, +inc),
            sdl2.SDLK_COMMA : (7, -inc),
            sdl2.SDLK_o : (8, +inc),
            sdl2.SDLK_PERIOD : (8, -inc),
            sdl2.SDLK_p : (9, +inc),
            sdl2.SDLK_MINUS : (9, -inc),
        }
        if not key in keymap or not keymap[key][0] \
                in self.visualizers[self.current_visualizer].properties:
            return 1
        prop = self.visualizers[self.current_visualizer]\
            .properties[keymap[key][0]]
        change = keymap[key][1]
        if len(prop) < 2:
            return 2
        if len(prop) > 2:
            change *= prop[2]
        prop[1] += change
        self.visualizers[self.current_visualizer].update_property(
            keymap[key][0],
            change
        )
        print(" * Updated Property '{0:s}' ({1:+.3f}): {2:-.3f}".format(
            prop[0],
            change,
            prop[1]
        ))
        return 0
    
    
    def list_properties(self):
        properties = self.visualizers[self.current_visualizer].properties
        print(' * Available Properties: ')
        for prop_i in properties:
            prop = properties[prop_i]
            print("   '{0:s}': {1:-.3f}".format(prop[0], prop[1]))
        return 0
        

    def window_loop(self):
        """Main window loop"""
        self.time.frame()
        self._key_listener()
        # Sync Player and Analyzer, then analyze
        if not self.args.micin:
            self.analyzer.file_.setpos(self.player.file_.tell())
            try:
                self.analyzer.wave_read(1.0/self.args.fps)
                self.analyzer.analyze(A_weighting=False)
                self.analyzer.normalize()
            except audioanalyze.AudioAnalyzeError:
                self.stop()
                return 1
        self.visualizers[self.current_visualizer].draw()
        return 0
    
    
    def get_audio_loop(self):
        """PyAudio can't handle callbacks that are an instance of a class;
        Because of this, this function returns a copy of a callback that will
        use this specific class."""
        
        if not self.args.micin:
            def callback(in_data, frame_count, time_info, status):
                """Audio playback/recording loop"""
                buf = [struct.pack('B', 128)] * frame_count
                if self.paused:
                    return ''.join(buf), pyaudio.paContinue
                try:
                    self.player.wave_read(frames=frame_count)
                    for i, frame in enumerate(self.player.data):
                        buf[i] = struct.pack('B', int((frame+1)/2.0*255))
                    return ''.join(buf), pyaudio.paContinue
                except audioanalyze.AudioAnalyzeError:
                    return None, pyaudio.paComplete
        else:
            def callback(in_data, frame_count, time_info, status):
                self.analyzer.data_nframes = frame_count
                self.analyzer.wave_parse(
                    raw_data=in_data,
                    sampwidth=1,
                    nchannels=1
                )
                self.analyzer.analyze(A_weighting=True)
                self.analyzer.normalize()
                return None, pyaudio.paContinue
        
        return callback
    
    
    def render(self):
        """Render PNGs to a directory"""
        while self.time.tell() < self.analyzer.wave_duration():
            self.time.frame()
            self.analyzer.wave_seek(self.time.tell())
            self.analyzer.wave_read(1/float(self.args.fps))
            self.analyzer.analyze(A_weighting=True)
            print(" * Drawing frame {0: 3d} ({1:.2f}s)".format(
                self.time.iteration, self.time.tell()
            ))
            self.visualizers[self.current_visualizer].draw()
            filename = "{0:s}/{1:05d}.png".format(
                self.args.output,
                self.time.iteration
            )
            print(" * Writing to {0:s}".format(filename))
            self.visualizers[self.current_visualizer].s.write_to_png(filename)
        print(" * Done")
        return 0
    
    
    def _key_listener(self):
        """Handles key presses, e.g. space for pause, or arrow keys to seek."""
        for event in self.window.loop_events:
            if event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE: # quit
                    print( " * Escape" )
                    self.stop()
                elif event.key.keysym.sym == sdl2.SDLK_SPACE: # pause
                    if not self.paused:
                        self.pause()
                        print( " * Pause" )
                    else:
                        self.unpause()
                        print( " * Unpause" )
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE: # restart
                    self.seek(0)
                    print( " * Restart" )
                elif event.key.keysym.sym == sdl2.SDLK_LEFT: # rewind
                    self.seek(self.time.tell()-10)
                    print( " * Rewind" )
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT: # fast forward
                    self.seek(self.time.tell()+10)
                    print( " * Fast Forward" )
                elif event.key.keysym.sym == sdl2.SDLK_UP: # prev visualizer
                    if(self.current_visualizer > 0):
                        self.current_visualizer -= 1
                    else:
                        self.current_visualizer = len(self.visualizers)-1
                    self.list_properties()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN: # next visualizer
                    if(self.current_visualizer < len(self.visualizers)-1):
                        self.current_visualizer += 1
                    else:
                        self.current_visualizer = 0
                    print self.visualizers[self.current_visualizer].properties
                    self.list_properties()
                else:
                    self.update_property(event.key.keysym)
                    
        return 0    
    
if __name__ == '__main__':
    main = Main()
    main.main()