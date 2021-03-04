import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import Harmony as harm
import time
import musicalbeeps

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

player = musicalbeeps.Player(volume = 0.3,
                            mute_output = False)

# while(True):
#     print(tswift_progression[i])
#     player.play_note(tswift_progression[i][0], time_per_measure)
#     i += 1
#     if i == 4:
#         i = 0


print(audio_features)



# To play an A on default octave n°4 for 0.2 seconds
player.play_note("A", 5)

# # To play a G flat on octave n°3 for 2.5 seconds
player.play_note("G3b", 2.5)

# # To play a F sharp on octave n°5 for the default duration of 0.5 seconds
player.play_note("F5#")

analysis = sp.audio_analysis('spotify:track:7a9aeLVkn7DIqFjbanKz0k')
# print(analysis['sections'])

for section in analysis['sections']:
    print(section['start'])
    print(section['key'])
