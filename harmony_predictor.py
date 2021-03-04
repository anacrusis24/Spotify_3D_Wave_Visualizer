import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import Harmony as harm
import time

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

# Shows playing devices
audio_features = sp.audio_features('spotify:track:7a9aeLVkn7DIqFjbanKz0k')

key = audio_features[0]['key']
mode = audio_features[0]['mode']
tempo = audio_features[0]['tempo']
time_signature = audio_features[0]['time_signature']
time_per_measure = time_signature * 1/tempo * 60

#key mapping to letters
if key == 0:
    key = 'C'
elif key == 1:
    key = 'C#'
elif key == 2:
    key = 'D'
elif key == 3:
    key = 'Eb'
elif key == 4:
    key = 'E'
elif key == 5:
    key = 'F'
elif key == 6:
    key = 'F#'
elif key == 7:
    key = 'G'
elif key == 8:
    key = 'G#'
elif key == 9:
    key = 'A'
elif key == 10:
    key = 'Bb'
elif key == 11:
    key = 'B'

if mode == 0:
    mode = 'Minor'
elif mode == 1:
    mode = "Major"

harmony = harm.Harmony(key, mode)

tonic_chord = harmony.triad_harmony(key)
IV_chord = harmony.triad_harmony(harmony.scale[3])
major_dom_chord = harmony.major_dom(harmony.scale[4])
VI_chord = harmony.triad_harmony(harmony.scale[5])

tswift_progression = [tonic_chord, major_dom_chord, VI_chord, IV_chord]
i = 0

while(True):
    print(tswift_progression[i])
    i += 1
    if i == 4:
        i = 0
    time.sleep(time_per_measure)
