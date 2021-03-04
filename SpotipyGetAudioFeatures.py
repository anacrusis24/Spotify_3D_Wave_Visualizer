# shows acoustic features for tracks for the given artist

from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys
import cred

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace = False

# if len(sys.argv) > 1:
#     artist_name = ' '.join(sys.argv[1:])
# else:
#     artist_name = 'weezer'
#
# results = sp.search(q=artist_name, limit=50)
# tids = []
# for i, t in enumerate(results['tracks']['items']):
#     print(' ', i, t['name'])
#     tids.append(t['uri'])

tids = ['spotify:track:7a9aeLVkn7DIqFjbanKz0k']

start = time.time()
features = sp.audio_features(tids)
delta = time.time() - start
# for feature in features:
#     print(json.dumps(feature, indent=4))
#     print()
#     analysis = sp._get(feature['analysis_url'])
#     print(json.dumps(analysis, indent=4))
#     print()
# print("features retrieved in %.2f seconds" % (delta,))

# print(features[0]['analysis_url'])

analysis = sp.audio_analysis('spotify:track:7a9aeLVkn7DIqFjbanKz0k')
# print(analysis['sections'])

for section in analysis['sections']:
    print(section['start'])
    print(section['key'])