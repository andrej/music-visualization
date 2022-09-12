# Live Music Visualization in Python

This repository contains the code I wrote as a High Schooler for my graduation project on live music visualization. This application performs a fast fourier transform (as provided by NumPy) on the microphone input (from SDL) and uses the gained frequency information to render one of the provided visualizations using the Cairo graphics library. To generate visualizations for an audio file, a tool like "Soundflower" can be used on MacOS to simulate a microphone input using the audio from a file.

An example visualization output by this program, as well as my project report PDF can be [found on my website][1].

## Requirements

- NumPy
- Cairo library
- SDL2 library and Python bindings 

[1]: https://andreroesti.com/projects/maturaarbeit.html
