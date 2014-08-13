"""
Analyze WAV audio files.
"""

import struct
import math
import wave
import numpy
import scipy.signal
import scipy.fftpack

class AudioAnalyze:
    """
    Read WAV audio files and do simple frequency analysis.

    Attributes:
    data            A list of values between -1 and 1 that represent the audio
                    wave over time
    data_samplerate Rate at which `data` was sampled (samples per second)
    data_*          Wave information (nchannels, sampwidth, etc)
    freq_powers     A list containing the power for each frequency
    file_           A wave object that this class can read wave data from
    
    normalization   List of past normalization values (multipliers; 1=unchanged)
    normalization_len How many seconds of past to consider for normalization
    """
    
    data = []
    data_samplerate = 0
    data_nchannels = 0
    data_sampwidth = 0
    data_framerate = 0
    data_nframes = 0
    
    freq_powers = []
    file_ = None
    
    max_powers = []
    max_powers_len = 2**24
    
    # Audio analysis functions
    
    def analyze(self, window_func=scipy.signal.hanning, A_weighting=False):
        """
        Calculate the powers of the frequencies that are in the wave
        `wave_data`.
        
        Arguments:
        window_func A windowing function that returns a list that gets
                    multiplied with the data, or None
        A_weighting Wether to perform A_weighting on the data or not
        """
        window_func = None
        if window_func:
            window = window_func(len(self.data))
        else:
            window = 'boxcar'
        periodogram = scipy.signal.welch(
            self.data, window=window, scaling='density'
        )
        self.freq_powers = periodogram[1] / (len(self.data)/2.0)
        # Power Spectral Density - normalized with 2*N instead of just N 
        # because of FFT implementation optimizations
        if A_weighting:
            for key, power in enumerate(self.freq_powers):
                freq = self.key_to_freq(key)
                self.freq_powers[key] = self.A_weighting(power, freq)
        return 0
    
    
    def freq_power(self, freq):
        """
        Return the power of the given frequency.
        """
        key = self.freq_to_key(freq)
        if not key:
            return None
        return self.freq_powers[key]
        
    
    def freq_range_power(self, min_freq=None, max_freq=None, average=True):
        """
        Return the cumulative power of the given frequency range.
        """
        min_key = self.freq_to_key(min_freq) or 1 # don't include DC offset
        max_key = self.freq_to_key(max_freq) or (len(self.freq_powers)-1)
        if max_key-min_key <= 0:
            return 0
        if not (min_key or max_key):
            return None
        val = sum(self.freq_powers[min_key:max_key])
        if average:
            val /= max_key-min_key+1
        return val
    
    
    def list_freq_powers(self, min_freq=None, max_freq=None, sort=False):
        """
        Return a list of tuples in the format (frequency Hz, power).
        """
        min_key = self.freq_to_key(min_freq) or 0
        max_key = self.freq_to_key(max_freq) or (len(self.freq_powers)-1)
        out = []
        for key, power in enumerate(self.freq_powers[min_key:max_key]):
            out.append((self.key_to_freq(key+min_key), power))
        if sort:
            out.sort(key=lambda x:x[1])
        #print out
        return out
    
    
    def list_freq_bin_powers(self, bins, sort=False, average=True):
        """
        Gives powers for given frequency bins. `bins` is a list of tuples with
        minimum and maximum values of frequency ranges.
        """
        out = []
        for bin_min, bin_max in bins:
            out.append(
                (
                    (bin_min, bin_max),
                    self.freq_range_power(bin_min, bin_max, average)
                )
            )
        if sort:
            out.sort(key=lambda x:x[1])
        return out
    
    
    def dominant_freq(self, min_freq=None, max_freq=None):
        """
        Find the frequency with the most power in the given range; return a
        tuple with it's frequency and power.
        """
        freqs = self.list_freq_powers(min_freq, max_freq, sort=True)
        return freqs[len(freqs)-1]
        
        
    def normalize(self, average=False, history=25*5):
        """
        Normalize the frequency powers, so the all values from 0 - 1 are nicely
        used.
        
        Peak method: The loudest frequency has a value of 1.0
        Average method: The average of all frequencies is 1.0
        
        Arguments:
        average        If false, peak mode is used, otherwise average
        
        """
        if average: # average method
            total_power = sum(self.freq_powers)/len(self.freq_powers)
        else: # peak method
            total_power = max(self.freq_powers)
        self.max_powers.append(total_power)
        if len(self.max_powers) >= self.max_powers_len:
            del self.max_powers[0]
        powers = numpy.array(self.max_powers[-history:])
        max_power = max( powers * numpy.linspace(
                    start=1.0/history,
                    stop=1.0,
                    num=len(powers)
                )
            )
        nv = 1.0/max_power
        for i, freq in enumerate(self.freq_powers):
            self.freq_powers[i] *= nv
        return 0
    
    
    def reset_normalization():
        self.max_powers = []
        return 0
    
    # Helper functions for unit conversions
    
    def freq_to_key(self, freq):
        """
        Given a frequency, returns the key of the item in the `freq_powers` 
        arrays that contains that frequencys value.
        """
        if not freq:
            return None # useful for shorthand use of this function
        key = int(float(freq)/self.data_samplerate*len(self.data))
        if key >= len(self.freq_powers) or key < 0:
            return None
        return key
    
    
    def key_to_freq(self, key):
        """
        Given a key in `freq_power`, return the frequency of that key in Hz.
        """
        return int(key/(len(self.data)*(1.0/self.data_samplerate)))
    
    
    def octave_to_freq(self, base_freq=1, octave=0):
        """
        Return `base_freq`, increased (doubled) by a given amount of octaves.
        """
        return base_freq * 2**octave
    
    
    def power_to_dB(self, power):
        """
        Return a decibel value for the given power value.
        """
        return 10*math.log(power, 10)
    
    
    def linear_bins(self, start=0, stop=1, num=0):
        """
        Generates an array of linearly evenly spaced bins. Every bin is a tuple
        containing two values: The beginning and the end of the bin.
        """
        out = []
        inc = (stop-start)/float(num)
        for i in range(0, num):
            out.append((i*inc+start, (i+1)*inc+start))
        return out
    
    
    def logarithmic_bins(self, start=0, stop=1, num=0, base=2):
        """
        Like `linear_bins()`, but uses logarithmic scale. Base 2 works well for
        frequencies, because human hearing uses octaves.
        """
        out = []
        factor = math.log((stop-start),base)/num
        
        for i in range(0, num):
            out.append(
                (base**(i*factor)+start-1, base**((i+1)*factor)+start)
            )
        return out
    
    
    def linear_scale(self, val, in_min=0, in_max=1, out_min=0, out_max=1):
        """
        Map a value to a different scale linearly.
        """
        return (
            (val-in_min)/float(in_max-in_min)*(out_max-out_min)+out_min
        )
    
    
    def logarithmic_scale(self, val, in_min=0, in_max=1, out_min=0, out_max=1,
        base=10, log_min=1, log_max=2):
        """
        Map a value on a logarithmic function. The input value lies between
        `in_min` and `in_max`. The logarithmic function is described by `base`,
        and a "window" of `log_min` and `log_max` (these are the X values on the
        logarithmic function).
        """
        if not out_min and not out_max:
            out_min = log_min
            out_max = log_max
        val = (val-in_min)/float(in_max-in_min)
        return self.linear_scale(
            math.log(
                (log_max-log_min)*val+log_min, 
                base
            ),
            math.log(log_min, base), math.log(log_max, base), out_min, out_max
        )
    
    
    def A_weighting(self, val, freq):
        """
        Return an A-weighted value of the power of a given frequency.
        Gain function according to Wikipedia.
        """
        gain = (
            (12200**2 * freq**4)
            / (
                (freq**2 + 20.6**2) * 
                math.sqrt( (freq**2 + 107.7**2) * (freq**2 + 737.9**2) ) *
                (freq**2 + 12200**2)
            )
        )
        return val * gain**2
    
    
    # WAV audio file handling
    
    def wave_open(self, wavefile):
        """
        Open any file like object as an instance of `wave` for this class.
        Only unsigned 8-bit and signed 16-bit WAV files are supported.

        Arguments:
        wavefile        File path or file like object
        """
        self.file_ = wave.open( wavefile )
        self.data_nchannels, self.data_sampwidth, self.data_framerate, \
        self.data_nframes, no, no = self.file_.getparams()
        if self.data_sampwidth > 2:
            self.file_.close()
            self.file_ = None
            raise AudioAnalyzeError("Unsupported WAV file")
            return 1
        self.data_samplerate = self.data_framerate
        return 0
    
    
    def wave_seek(self, time=0.0):
        """
        Move in the file to given time position.

        Arguments:
        time        Time in seconds to move to
        """
        if not self.file_:
            return 1
        goto = int(time*self.data_framerate)
        if goto > self.data_nframes:
            raise AudioAnalyzeError("Time is beyond end of data")
            return 2
        self.file_.setpos(goto)
        return 0
    
    
    def wave_tell(self):
        """
        Return playback time.
        """
        if self.file_:
            return self.file_.tell()/float(self.data_framerate)
        else:
            return 0
        
    
    def wave_duration(self):
        """
        Return how long the wave file is in seconds.
        """
        if not self.data_nframes or not self.data_framerate:
            raise AudioAnalyzeError("No data available")
            return 1
        return self.data_nframes/float(self.data_framerate)
    
    
    def wave_read(self, duration=0.0, frames=None):
        """
        Read a chunk of audio frame data.
        
        Arguments:
        duration    How much data to read in seconds...
        frames      or frames (one of both has to be None)
        """
        if frames:
            chunk_size = frames
        else:
            chunk_size = int(duration*self.data_framerate)
        if self.file_.tell()+chunk_size > self.data_nframes:
            raise AudioAnalyzeError("Chunk size goes beyond end of data")
            return 1
        raw_data = self.file_.readframes(chunk_size)
        self.wave_parse(
            raw_data,
            self.data_sampwidth,
            self.data_nchannels
        )
        return 0
    
    
    def wave_parse(self, raw_data=None, sampwidth=1, nchannels=1):
        """
        Parse some raw audio data.
        
        Arguments:
        raw_data    Data to parse
        sampwidth   Sample width of the individual samples;
                    1 -> UInt8
                    2 -> SInt16
        nchannels   Number of channels (Only first one will be parsed)
        """
        if sampwidth == 1:
            fmt = '<B' # little-endian unsigned char
            min_ = 0
            max_ = 2**8
        elif sampwidth == 2:
            fmt = '<h' # little-endian signed short
            min_ = -(2**16)/2
            max_ = (2**16)/2
        self.data = []
        i = 0
        while i<len(raw_data):
            val = struct.unpack(
                fmt, raw_data[i:i+sampwidth]
            )[0]
            self.data.append(2*((val+abs(min_))/float(max_-min_))-1) # -1.0-1.0
            i += sampwidth*nchannels
        if not raw_data:
            return 1
    
    # Initialization
    
    def __init__(self, wavefile=None):
        if wavefile:
            self.wave_open(wavefile)


class AudioAnalyzeError( Exception ):
    pass