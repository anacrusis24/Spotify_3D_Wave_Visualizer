import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import Harmony as harm
import time
import musicalbeeps
import numpy as np

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

player = musicalbeeps.Player(volume = 0.3,
                            mute_output = False)

analysis = sp.audio_analysis('spotify:track:7a9aeLVkn7DIqFjbanKz0k')
section_start_times = []
section_durations = []
section_keys = []
section_modes = []
section_tempos = []
section_time_signature = []

for section in analysis['sections']:
    section_start_times.append(section['start'])
    section_durations.append(section['duration'])
    section_keys.append(section['key'])
    section_modes.append(section['mode'])
    section_tempos.append(section['tempo'])
    section_time_signature.append(section['time_signature'])

section_start_times = np.array(section_start_times)
section_durations = np.array(section_durations)
section_tempos = np.array(section_tempos)
section_time_signature = np.array(section_time_signature)
section_num_measures = section_durations * (section_tempos/60) / section_time_signature
# section_num_measures = np.round(section_num_measures)

#key mapping to letters
for i in range(len(section_keys)):
    if section_keys[i] == 0:
        section_keys[i] = 'C'
    elif section_keys[i] == 1:
        section_keys[i] = 'C#'
    elif section_keys[i] == 2:
        section_keys[i] = 'D'
    elif section_keys[i] == 3:
        section_keys[i] = 'Eb'
    elif section_keys[i] == 4:
        section_keys[i] = 'E'
    elif section_keys[i] == 5:
        section_keys[i] = 'F'
    elif section_keys[i] == 6:
        section_keys[i] = 'F#'
    elif section_keys[i] == 7:
        section_keys[i] = 'G'
    elif section_keys[i] == 8:
        section_keys[i] = 'G#'
    elif section_keys[i] == 9:
        section_keys[i] = 'A'
    elif section_keys[i] == 10:
        section_keys[i] = 'Bb'
    elif section_keys[i] == 11:
        section_keys[i] = 'B'

for i in range(len(section_modes)):
    if section_modes[i] == 0:
        section_modes[i] = 'Minor'
    elif section_modes[i] == 1:
        section_modes[i] = "Major"

for i in range(len(section_durations)):
    harmony = harm.Harmony(section_keys[i], section_modes[i])
    tonic_chord = harmony.triad_harmony(section_keys[i])
    IV_chord = harmony.triad_harmony(harmony.scale[3])
    major_dom_chord = harmony.triad_harmony(harmony.scale[4])
    VI_chord = harmony.triad_harmony(harmony.scale[5])
    tswift_progression = [tonic_chord, major_dom_chord, VI_chord, IV_chord]

    for j in range(int(section_num_measures[i])):
        k = j
        if k > len(tswift_progression) - 1:
            k = j % len(tswift_progression)
        player.play_note(tswift_progression[k][0], section_durations[i]/section_num_measures[i])
        print(tswift_progression[k])