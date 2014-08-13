#!/usr/bin/env python2.7

import time
import struct
import pyaudio
#import cairo
#import sdl2
#import cairowindow

pa = None

class Main:
    stream = None
    samprate = 44100

    prev = 0
    i = 0
    def get_audio_callback(self):
        def callback(in_data, frame_count, time_info, status_flags):
            threshold = 128/4
            for d in in_data:
                v = struct.unpack('B', d)[0]
                if abs(v-self.prev) > threshold:
                    print '{0: > 4d}. TAP'.format(self.i)
                    self.i += 1
                self.prev = v
            return None, pyaudio.paContinue
        return callback
    
    def loop(self):
        self.stream.start_stream()
        i = 0
        while i < 10*(1/0.1):
            time.sleep(0.1)
            i += 1
        return 0
    
    def main(self):
        global pa
        pa = pyaudio.PyAudio()
        self.stream = \
            pa.open(rate=self.samprate,
            format=pyaudio.paUInt8,channels=1,input=True,
            stream_callback=self.get_audio_callback())
        self.loop()
        self.stream.stop_stream()
        self.stream.close()
        pa.terminate()
        return 0
        
main = Main()
main.main()