import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import Harmony as harm
import time
import musicalbeeps
import threading
import numpy as np

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

# Shows playing devices
audio_features = sp.audio_features('spotify:track:7a9aeLVkn7DIqFjbanKz0k')

key = audio_features[0]['key']
mode = audio_features[0]['mode']
tempo = audio_features[0]['tempo']
time_signature = audio_features[0]['time_signature']
time_per_measure = time_signature * 1/tempo * 60 + 3

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

player = musicalbeeps.Player(volume = 0.3, mute_output = False)

def player_thread(chord, note):
    print('Player %d started' % note)
    player.play_note(tswift_progression[chord][note], time_per_measure)

def conductor_thread():
    print('Conductor Started')
    chords_played = 0
    while chords_played < len(tswift_progression):
        duration = time.time() - start_time
        if chords_played < int(np.floor(duration / time_per_measure)) - 1:
            print('new chord')
            threads = list()

            for note in range(3):
                player = threading.Thread(target=player_thread, args=(chords_played, note))
                threads.append(player)
                player.start()

            for thread in threads:
                thread.join()

            chords_played += 1


if __name__ == "__main__":
    player = musicalbeeps.Player(volume=0.3,
                                 mute_output=False)

    start_time = time.time()

    x = threading.Thread(target=conductor_thread)
    x.start()
    # print(tswift_progression) # [['D', 'F', 'A'], ['A', 'C#', 'E'], ['Bb', 'D', 'F'], ['G', 'Bb', 'D']]

