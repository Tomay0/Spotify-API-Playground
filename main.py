import spotipy
import math
import random
from spotipy.oauth2 import SpotifyOAuth

def main():
  scope = "user-library-read user-top-read playlist-read-private playlist-modify-private user-read-currently-playing"

  sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

  playlist_from_top_artists(sp)

def get_all_liked_songs(sp):
  song_list = []

  results = sp.current_user_saved_tracks(limit=50, offset=0)
  total_songs = results['total']
  offset = 0

  while offset < total_songs:
    offset += 50

    for idx, item in enumerate(results['items']):
      track = item['track']
      song_list.append(track)

    results = sp.current_user_saved_tracks(limit=50, offset=offset)

  return song_list

def playlist_from_50_liked_songs(sp):
  song_list = [track['id'] for track in get_all_liked_songs(sp)]

  generate_random_playlist(sp, "Randomised liked songs", song_list, 50)

def generate_random_playlist(sp, name, songs, count=50):
  current_user = sp.current_user()['id']

  # pick 50 random songs
  playlist = random.sample(songs, count)

  playlist_id = sp.user_playlist_create(user=current_user, name=name, public=False)['id']

  # playlist = ", ".join(playlist)

  for i in range(math.ceil(count / 10.0)):
    sp.user_playlist_add_tracks(user=current_user, playlist_id=playlist_id, tracks=playlist[10 * i : 10 * i + 10])


def get_my_artists(sp):
  # returns all artists that you liked
  song_list = get_all_liked_songs(sp)

  artists = {}

  for song in song_list:
    for artist in song['artists']:
      artists[artist['id']] = artist['name']

  return artists

def songs_from_artist(sp, id):
  albums = sp.artist_albums(id, limit=50)
  total_songs = albums['total']
  offset = 0

  tracks = {}

  while offset < total_songs:
    for album in albums['items']:
      album_tracks = sp.album_tracks(album['id'], limit=50)

      for track in album_tracks['items']:
        artist_ids = [artist['id'] for artist in track['artists']]

        if id in artist_ids:
          tracks[track['id']] = track

    offset += 50
    albums = sp.artist_albums(id, limit=50, offset=offset)

  return tracks

def playlist_from_artists(sp, artists, count):
  songs = {}

  for artist in artists:
    print(f"Obtaining songs from artist: {artist}...")
    song_list = songs_from_artist(sp, artist)

    for s in song_list:
      songs[s] = song_list[s]

  print("Generating playlist...")

  song_list = [track['id'] for track in songs.values()]

  generate_random_playlist(sp, "Generated Playlist", song_list, count)

  print("Done!")

def top_artists(sp, count):
  return sp.current_user_top_artists(limit=count)['items']

def playlist_from_top_artists(sp):
  playlist_from_artists(sp, [artist['id'] for artist in top_artists(sp, 2)], 30)


main()
