"""
https://github.com/plamere/spotipy/blob/master/examples/player.py
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import cred

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

# Shows playing devices
res = sp.devices()
pprint(res)

# Change track
sp.start_playback(uris=['spotify:track:7a9aeLVkn7DIqFjbanKz0k'])

# Change volume
sp.volume(100)
sleep(5)
sp.volume(50)
sleep(5)
sp.volume(100)