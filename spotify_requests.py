import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess
import sys
import requests
import pprint

class Spotify:
    def __init__(self):
        scope = 'user-read-playback-state, user-modify-playback-state, playlist-read-private, user-follow-read, user-library-read, user-library-modify'

        # Credentials file format: client secret, client id, redirect uri, username, all on separate lines w/ no extra quotes/characters
        credentials_file = open("C:/Users/Griffin/Desktop/py/cleaned_up_sp_widget/spotify_credentials.txt", "r")
        credentials = credentials_file.readlines()
        for i in range(3):
            credentials[i] = credentials[i].strip()



        self.sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_secret = credentials[0], client_id = credentials[1], redirect_uri = credentials[2], scope = scope, username=credentials[3]))

        self.pb = self.sp.current_playback('US')


        if self.pb is None:
            print("Nothing playing, exiting (cannot start playback without a specific device ID)")
            sys.exit()
        
        self.request_parse_song_data()

    def request_parse_song_data(self):

        playback = self.pb

        artist_list = playback['item']['artists']
        artist_string = ""

        for a in artist_list:
            artist_string += a['name'] + ", "
        artist_string = artist_string[:-2]

        title = playback['item']['name']

        album_cover_url = playback['item']['album']['images'][0]['url']
        response = requests.get(album_cover_url)
        file = open("album.png", "wb")
        file.write(response.content)
        file.close()

        self.display_string = artist_string + " - " + title

        self.shuffle_state = self.pb['shuffle_state']
        self.device_id = self.pb['device']['id']
        self.is_playing = self.pb['is_playing']
        self.shuffle_state = self.pb['shuffle_state']
        self.track_id = self.pb['item']['id']

        self.is_liked = self.sp.current_user_saved_tracks_contains([self.track_id])[0] # BUGGED - ONLY CHECKS SAVED SONGS THAT WOULD SHOW UP IN 'LIKED SONGS', NOT SONGS SAVED BY SAVING A WHOLE ALBUM
        self.progress = self.pb['progress_ms']
        self.duration = self.pb['item']['duration_ms']
        self.volume = self.pb['device']['volume_percent']

        self.album_uri = self.pb['item']['album']['uri']
        self.artist_uri = self.pb['item']['album']['artists'][0]['uri']

        self.playlist_context_uri = None


        if self.pb['context'] is not None and self.pb['context']['type'] == 'playlist':
            self.playlist_context_uri = self.pb['context']['uri']
        
        #self.restrictions = self.pb['actions']['disallows'] # use this for determing if certain buttons are disabled


    def request_parse_user_data(self):

        current_album = self.sp.album(self.album_uri)

        self.artist_name = current_album['artists'][0]['name']
        self.album_name = current_album['name']
        self.playlist_name = None # by default, otherwise doesnt set variable if there isnt a playlist context

        self.song_names_in_current_album = []

        album_total = current_album['tracks']['total']
        if album_total > 50:
            album_total = 50
            

        for i in range(0, album_total):
            self.song_names_in_current_album.append(current_album['tracks']['items'][i]['name'])

        artist_top_tracks = self.sp.artist_top_tracks(self.artist_uri, 'US')
        
        self.artist_top_track_names = []
        self.artist_top_track_uris = []

        for i in range(0, len(artist_top_tracks['tracks'])):
            self.artist_top_track_names.append(artist_top_tracks['tracks'][i]['name'])
            self.artist_top_track_uris.append(artist_top_tracks['tracks'][i]['uri'])

        self.playlist_song_names = []

        if self.playlist_context_uri != None:
            playlist_data = self.sp.playlist(self.playlist_context_uri)

            self.playlist_name = playlist_data['name']

            #print(playlist_data['tracks']['total'])

            #Temp fix:
            total = playlist_data['tracks']['total']
            if total > 50:
                total = 50

            for i in range(0, total): # I think the maximum number of songs you can pull at once is 50, but the total # still gives all songs in playlist.
                self.playlist_song_names.append(playlist_data['tracks']['items'][i]['track']['name'])

    def request_parse_library_data(self):
        # gets: most recent: 20 liked songs, 20 liked albums, 20 saved playlists
        # Probably can't use context IDs here since the context will be created
        print('called request_parse_library_data')

        likes_obj = self.sp.current_user_saved_tracks(limit=20, market='US')
        albums_obj = self.sp.current_user_saved_albums(limit=20, market='US')
        playlist_obj = self.sp.current_user_playlists(limit=20)

        self.user_likes = []
        self.user_likes_uris = []
        self.saved_albums = []
        self.saved_album_uris = []
        self.saved_playlists = []
        self.saved_playlists_uris = []
        

        for i in range(0, 20):
            self.user_likes.append(likes_obj['items'][i]['track']['name'])
            self.user_likes_uris.append(likes_obj['items'][i]['track']['uri'])

            self.saved_albums.append(albums_obj['items'][i]['album']['name'])
            self.saved_album_uris.append(albums_obj['items'][i]['album']['uri'])

            self.saved_playlists.append(playlist_obj['items'][i]['name'])
            self.saved_playlists_uris.append(playlist_obj['items'][i]['uri'])

    def update_pb(self):
        self.pb = self.sp.current_playback('US')
    
    def update_playstate(self): # called on song change / sync button call
        self.update_pb()
        self.is_playing = self.pb['is_playing']
        self.track_id = self.pb['item']['id']
        self.is_liked = self.sp.current_user_saved_tracks_contains([self.track_id])

    def update_track_progress(self):
        self.update_pb()
        self.progress = self.pb['progress_ms']
        self.duration = self.pb['item']['duration_ms']
    
    def pause(self):
        self.sp.pause_playback(self.device_id)
    def play(self):
        self.sp.start_playback(self.device_id)
    def skip(self):
        self.sp.next_track(self.device_id)
    def previous(self):
        self.sp.previous_track(self.device_id)
    def shuffle(self, state):
        self.sp.shuffle(state, self.device_id)
    def like(self):
        self.sp.current_user_saved_tracks_add([self.track_id])
    def unlike(self):
        self.sp.current_user_saved_tracks_delete([self.track_id])
    def set_volume(self, value):
        self.sp.volume(value, self.device_id)
    def set_progress(self, position_ms):
        self.sp.seek_track(position_ms, device_id=self.device_id)

    # Only works for context types album and playlist. Not artist.
    def play_song_by_context(self, offset, context_uri):
        self.sp.start_playback(device_id=self.device_id, context_uri=context_uri, offset={"position":offset})

    def play_song_by_context_artist(self, uri):
        self.sp.start_playback(device_id=self.device_id, uris = [uri])
