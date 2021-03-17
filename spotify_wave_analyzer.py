"""
All code taken from Mark Jay's Audio Spectrum Analyzer Tutorial:
https://github.com/markjay4k/Audio-Spectrum-Analyzer-in-Python

This creates a 3D mesh with perlin noise to simulate
a terrain. The mesh is animated by shifting the noise
to give a "fly-over" effect.
If you don't have pyOpenGL or opensimplex, then:
    - conda install -c anaconda pyopengl
    - pip install opensimplex
"""

# General imports
import numpy as np
import time
import sys
import struct
import threading

# 3D Graphing imports
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from scipy.fftpack import fft

# Music imports
import pyaudio
import musicalbeeps
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred  # Spotify secret credentials
import Harmony  # Custom harmony generator


class Progression:
    def __init__(self, uri):
        self.uri = uri
        self.analysis = sp.audio_analysis(self.uri)

        features = sp.audio_features(self.uri)[0]
        self.song_time_signature = features['time_signature']
        self.song_tempo = features['tempo']
        self.song_key = [features['key']]
        self.song_mode = [features['mode']]

    def song_calculations(self):
        """
        Generates duration and number of measures per section
        """
        section_durations = []
        section_keys = []
        section_modes = []
        section_num_measures = []

        for section in self.analysis['sections']:
            section_durations.append(section['duration'])
            section_keys.append(section['key'])
            section_modes.append(section['mode'])
            section_num_measures.append(section['duration'] * section['tempo'] / 60 / section['time_signature'])

        section_durations = np.array(section_durations)
        section_num_measures = np.array(section_num_measures)
        return section_durations, section_num_measures, section_keys, section_modes

    def change_key(self, list_keys):
        """
        Translates Spotify key encodings into keys
        """
        key = {0: 'C', 1: 'C#', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'Bb', 11: 'B'}
        return [key.get(x, "No_key") for x in list_keys]

    def change_mode(self, list_modes):
        """
        Translates Spotify mode encodings into major/minor
        """
        key = {0: 'Minor', 1: 'Major'}
        return [key.get(x, "No_mode") for x in list_modes]

    def player_thread(self, progression, chord, note, time_per_measure):
        """
        Plays a single note given a chord, note, and duration
        """
        musicalbeeps.Player(volume=0.3, mute_output=False).play_note(progression[chord][note], time_per_measure)

    def play(self, print_notes=False, use_sections=False):
        """
        Plays the Spotify song + harmonies
        """
        # Play song on Spotify Desktop
        sp.start_playback(uris=[self.uri])

        # Play harmony using musicalbeeps
        section_durations, section_num_measures, section_keys, section_modes = self.song_calculations()
        for i in range(len(section_durations)):  # If use_sections is true then loop by section, else one loop for song
            if use_sections:
                key = self.change_key(section_keys)[i]
                mode = self.change_mode(section_modes)[i]
                time_per_measure = section_durations[i] / section_num_measures[i]
            else:
                key = self.change_key(self.song_key)[0]
                mode = self.change_mode(self.song_mode)[0]
                time_per_measure = self.song_time_signature / self.song_tempo * 60 * 2

            harmony = Harmony.Harmony(key, mode)
            tonic_chord = harmony.triad_harmony(key)
            IV_chord = harmony.triad_harmony(harmony.scale[3])
            major_dom_chord = harmony.triad_harmony(harmony.scale[4])
            VI_chord = harmony.triad_harmony(harmony.scale[5])
            progression = [tonic_chord, major_dom_chord, VI_chord, IV_chord]

            for j in range(int(section_num_measures[i])):
                k = j
                if k > len(progression) - 1:  # Restart
                    k = j % len(progression)

                threads = []
                for note in range(len(progression[k])):
                    player = threading.Thread(target=self.player_thread, args=(progression, k, note, time_per_measure))
                    threads.append(player)
                    player.start()
                for thread in threads:
                    thread.join()
                if print_notes:
                    print(progression[k])


class Terrain(object):
    def __init__(self, uri):
        """
        Initialize the graphics window and mesh surface
        """
        # setup the view window
        # pyqtgraph stuff
        pg.setConfigOptions(antialias=True)
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1910, 1070)

        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(0, '0'), (127, '128'), (255, '255')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        sp_xlabels = [
            (np.log10(10), '10'), (np.log10(100), '100'),
            (np.log10(1000), '1000'), (np.log10(22050), '22050')
        ]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        self.waveform = self.win.addPlot(
            title='WAVEFORM', row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )
        self.spectrum = self.win.addPlot(
            title='SPECTRUM', row=2, col=1, axisItems={'bottom': sp_xaxis},
        )

        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        # waveform and spectrum x points
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.f = np.linspace(0, self.RATE / 2, int(self.CHUNK / 2))

        self.start_time = time.time()
        self.frames = 0

        self.uri = uri

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'waveform':
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setYRange(0, 255, padding=0)
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='m', width=3)
                self.spectrum.setLogMode(x=True, y=True)
                self.spectrum.setYRange(-4, 0, padding=0)
                self.spectrum.setXRange(
                    np.log10(20), np.log10(self.RATE / 2), padding=0.005)

    def update(self):
        """
        Update the mesh and shift the noise each time
        """
        self.frames += 1
        end_time = time.time()
        duration = end_time - self.start_time
        if self.frames == 1000:
            print('FPS = %d' % (self.frames / duration))

        wf_data = self.stream.read(self.CHUNK)
        wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
        wf_data = np.array(wf_data, dtype='b')[::2] + 128
        self.set_plotdata(name='waveform', data_x=self.x, data_y=wf_data, )

        sp_data = fft(np.array(wf_data, dtype='int8') - 128)
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)]
                         ) * 2 / (128 * self.CHUNK)
        self.set_plotdata(name='spectrum', data_x=self.f, data_y=sp_data)


    def start(self):
        """
        Gets the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def animation(self, frame_time=10):
        """
        Calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frame_time)

        harmonies = Progression(self.uri)
        x = threading.Thread(target=harmonies.play)
        x.start()

        print('starting')
        self.start()


# List of songs to try
beatles = 'spotify:track:6dGnYIeXmHdcikdzNNDMm2'
pirates = 'spotify:track:7a9aeLVkn7DIqFjbanKz0k'
tswift = 'spotify:track:0sY6ZUTh4yoctD8VIXz339'

if __name__ == '__main__':
    # Initiate connection to Spotify
    scope = "user-read-playback-state,user-modify-playback-state"
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    # Start song and animation
    t = Terrain(pirates)
    t.animation()
