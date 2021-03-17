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
from pyqtgraph.Qt import QtCore, QtGui

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

    def make_progression(self, song_key_num, song_mode_num):
        song_key = self.change_key(song_key_num)
        song_mode = self.change_mode(song_mode_num)
        harmony = Harmony.Harmony(song_key[0], song_mode[0][0])
        progression = []

        if song_mode == ['Major']:
            tonic_chord = harmony.triad_harmony(song_key[0])
            IV_chord = harmony.triad_harmony(harmony.scale[3])
            dom_chord = harmony.triad_harmony(harmony.scale[4])
            VI_chord = harmony.triad_harmony(harmony.scale[5])
            progression = [tonic_chord, dom_chord, VI_chord, IV_chord]

        elif song_mode == ['Minor']:
            tonic_chord = harmony.triad_harmony(song_key[0])
            III_chord = harmony.triad_harmony(harmony.scale[2])
            VI_chord = harmony.triad_harmony(harmony.scale[5])
            progression = [tonic_chord, III_chord, tonic_chord, VI_chord]

        return progression

    def player_thread(self, progression, chord, note, time_per_measure):
        """
        Plays a single note given a chord, note, and duration
        """
        musicalbeeps.Player(volume=0.1, mute_output=False).play_note(progression[chord][note], time_per_measure)


    def play(self, print_notes=False, use_sections=False):
        """
        Plays the Spotify song + harmonies
        """
        # Play song on Spotify Desktop
        sp.start_playback(uris=[self.uri])

        section_durations, section_num_measures = self.song_calculations()
        for i in range(len(section_durations)):
            progression = self.make_progression(self.song_key, self.song_mode)
            time_per_measure = self.song_time_signature / self.song_tempo * 60 * 2

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
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle('Terrain')
        self.window.setGeometry(0, 110, 1920, 1080)
        self.window.setCameraPosition(distance=30, elevation=12)
        self.window.show()

        # constants and arrays
        self.nsteps = 1.3  # Distance between each vertex
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)  # Number of faces

        self.RATE = 44100
        self.CHUNK = len(self.xpoints) * len(self.ypoints)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            output=True,
            input_device_index=2,
            frames_per_buffer=self.CHUNK,
        )

        # perlin noise object
        self.noise = OpenSimplex()

        # create the veritices array
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            faces=faces,
            vertexes=verts,
            faceColors=colors,
            drawEdges=True,
            smooth=False,
        )
        self.mesh1.setGLOptions('additive')
        self.window.addItem(self.mesh1)

        self.start_time = time.time()
        self.frames = 0

        self.uri = uri

    def mesh(self, offset=0, height=2.5, wf_data=None):

        if wf_data is not None:
            wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
            wf_data = np.array(wf_data, dtype='b')[::2] + 128
            wf_data = np.array(wf_data, dtype='int32') - 128
            wf_data = wf_data * 0.04
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        else:
            wf_data = np.array([1] * 1024)
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        faces = []
        colors = []
        verts = np.array([  # Each point is a list with x, y, and z (height)
            [  # TODO: verify that the noise param (5) works
                x, y, wf_data[xid][yid] * self.noise.noise2d(x=xid / 5 + offset, y=yid / 5 + offset)
            ] for xid, x in enumerate(self.xpoints) for yid, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        for yid in range(self.nfaces - 1):
            yoff = yid * self.nfaces  # offset, +nfaces to shift down one row
            for xid in range(self.nfaces - 1):
                faces.append([
                    xid + yoff,
                    xid + yoff + self.nfaces,
                    xid + yoff + self.nfaces + 1,
                ])
                faces.append([
                    xid + yoff,
                    xid + yoff + 1,
                    xid + yoff + self.nfaces + 1,
                ])
                colors.append([  #
                    xid / self.nfaces, 1 - xid / self.nfaces, yid / self.nfaces, 0.7
                ])
                colors.append([
                    xid / self.nfaces, 1 - xid / self.nfaces, yid / self.nfaces, 0.8
                ])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

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

        verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

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
    t = Terrain(tswift)
    t.animation()
