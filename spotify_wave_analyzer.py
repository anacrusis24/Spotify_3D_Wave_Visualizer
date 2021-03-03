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

import numpy as np
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
import struct
import pyaudio
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import time
import cred


class Terrain(object):
    def __init__(self):
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
        update the mesh and shift the noise each time
        """
        self.frames += 1
        if self.frames == 1000:
            end_time = time.time()
            duration = end_time - self.start_time
            print('Frames = %f' % self.frames)
            print('Duration = %f' % duration)
            print('FPS = %d' % (self.frames / duration))

        wf_data = self.stream.read(self.CHUNK)

        verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def animation(self, frametime=10):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        sp.start_playback(uris=['spotify:track:7a9aeLVkn7DIqFjbanKz0k'])

        self.start()

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

if __name__ == '__main__':
    t = Terrain()
    t.animation()