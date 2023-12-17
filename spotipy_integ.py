
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def shareTrack(artist_name, track_name):
  spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

  results = spotify.search(q="track:" + track_name + " artist:" + artist_name, type='track', limit=1)

  items = results['tracks']['items']
  
  count = 0
  response = ""
  for track in items:
      count += 1
      response+=f"TRACK: [{track['name']}] RELEASED [{track['album']['release_date']}] POPULARITY: [{track['popularity']}] DURATION: [{track['duration_ms']}] LINK: [{track['external_urls']['spotify']}] THUMBNAIL: [{track['album']['images'][0]['url']}] ID: [{track['id']}]\n"
  
  return track['artists'][0]['name'], track['name'], track['album']['name'], track['album']['release_date'], track['popularity'], track['duration_ms'], track['external_urls']['spotify'], track['album']['images'][0]['url'], track['id']