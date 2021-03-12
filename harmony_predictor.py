import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import Harmony as harm
import time
import musicalbeeps
import numpy as np
import threading

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

player = musicalbeeps.Player(volume = 0.3, mute_output = False)
uri = 'spotify:track:0sY6ZUTh4yoctD8VIXz339'
analysis = sp.audio_analysis(uri)
section_start_times = []
section_durations = []
list_keys = []
list_modes = []
section_tempos = []
section_time_signature = []
song_time_signature = sp.audio_features(uri)[0]['time_signature']
song_tempo = sp.audio_features(uri)[0]['tempo']
song_key = [sp.audio_features(uri)[0]['key']]
song_mode = [sp.audio_features(uri)[0]['mode']]

for section in analysis['sections']:
    section_start_times.append(section['start'])
    section_durations.append(section['duration'])
    list_keys.append(section['key'])
    list_modes.append(section['mode'])
    section_tempos.append(section['tempo'])
    section_time_signature.append(section['time_signature'])

section_start_times = np.array(section_start_times)
section_durations = np.array(section_durations)
section_tempos = np.array(section_tempos)
section_time_signature = np.array(section_time_signature)
section_num_measures = section_durations * (section_tempos/60) / section_time_signature
# section_num_measures = np.round(section_num_measures)

#key mapping to letters
def change_key_abc(list_keys):
    for i in range(len(list_keys)):
        if list_keys[i] == 0:
            list_keys[i] = 'C'
        elif list_keys[i] == 1:
            list_keys[i] = 'C#'
        elif list_keys[i] == 2:
            list_keys[i] = 'D'
        elif list_keys[i] == 3:
            list_keys[i] = 'Eb'
        elif list_keys[i] == 4:
            list_keys[i] = 'E'
        elif list_keys[i] == 5:
            list_keys[i] = 'F'
        elif list_keys[i] == 6:
            list_keys[i] = 'F#'
        elif list_keys[i] == 7:
            list_keys[i] = 'G'
        elif list_keys[i] == 8:
            list_keys[i] = 'G#'
        elif list_keys[i] == 9:
            list_keys[i] = 'A'
        elif list_keys[i] == 10:
            list_keys[i] = 'Bb'
        elif list_keys[i] == 11:
            list_keys[i] = 'B'

        return list_keys

def change_mode(list_modes):
    for i in range(len(list_modes)):
        if list_modes[i] == 0:
            list_modes[i] = 'Minor'
        elif list_modes[i] == 1:
            list_modes[i] = "Major"
    return list_modes



def player_thread(chord, note, time_per_measure):
    print('Player %d started' % note)
    musicalbeeps.Player(volume = 0.1, mute_output = False).play_note(tswift_progression[chord][note], time_per_measure)
print(song_mode)
print(change_key_abc(song_key)[0])
sp.start_playback(uris=[uri])
for i in range(len(section_durations)):
    harmony = harm.Harmony(change_key_abc(song_key)[0], change_mode(song_mode)[0])
    tonic_chord = harmony.triad_harmony(change_key_abc(song_key)[0])
    IV_chord = harmony.triad_harmony(harmony.scale[3])
    major_dom_chord = harmony.triad_harmony(harmony.scale[4])
    VI_chord = harmony.triad_harmony(harmony.scale[5])
    tswift_progression = [tonic_chord, major_dom_chord, VI_chord, IV_chord]
    time_per_measure = song_time_signature / song_tempo * 60 * 2

    for j in range(int(section_num_measures[i])):
        k = j
        if k > len(tswift_progression) - 1:
            k = j % len(tswift_progression)

        threads = []

        for note in range(len(tswift_progression[k])):
            player = threading.Thread(target = player_thread, args = (k, note, time_per_measure))
            # player.play_note(tswift_progression[k][note], section_durations[i]/section_num_measures[i])
            threads.append(player)
            player.start()
        for thread in threads:
            thread.join()
        print(tswift_progression[k])





# if __name__ == "__main__":
#     start_time = time.time()
#
#     x = threading.Thread(target=conductor_thread)
#     x.start()