import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ast
import os
from dotenv import load_dotenv
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

artists_df = pd.read_csv("./data/archive/artists.csv")
df = pd.read_pickle('./models/df.pkl')

with open('./models/songId.pkl', 'rb') as file:
    songsId = pickle.load(file)

with open('./models/scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

with open('./models/mlb.pkl', 'rb') as file:
    mlb = pickle.load(file)

load_dotenv()
client_id = os.getenv('client_id')
secret_id = os.getenv('secret_id')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret_id)
sp = spotipy.Spotify(auth_manager=auth_manager)

class Playlist():
    """
    A class to represent a Spotify playlist and generate song recommendations based on it.

    Attributes:
    playlist_url : str
        The URL of the Spotify playlist.
    """
    def __init__(self, playlist_url):
        """
        Constructs all the necessary attributes for the Playlist object.

        Parameters:
        playlist_url : str
            The URL of the Spotify playlist.
        """
        self.playlist_url = playlist_url
        self.sp = sp
        self.artists_df = artists_df
        self.scaler = scaler
        self.mlb = mlb
        self.df = df
        self.songsId = songsId

    def songFeatures(self, songId):
        """
        Fetches and constructs features for a given song ID.

        Parameters:
        song_id : str
            The ID of the song.

        Returns:
        dict
            A dictionary containing features of the song.
        """
        try:
            # Fetch track details from Spotify API
            track = self.sp.track(songId)
            artists = track['artists'][0]['id']
    
            # Fetch artist details from pre-loaded DataFrame or Spotify API
            if self.artists_df[self.artists_df['id'] == artists].any().any():
                genres = self.artists_df[self.artists_df['id'] == artists]['genres'].values[0]
                artists_popularity = self.artists_df[self.artists_df['id'] == artists]['popularity'].values[0]
            else:
                genres = str(self.sp.artist(artists)['genres'])
                artists_popularity = self.sp.artist(artists)['popularity']
    
            # Fetch song audio features from Spotify API
            song_features = self.sp.audio_features(songId)[0]
            song_features['genres'] = genres
            song_features['artist_popularity'] = artists_popularity
            release_date = track['album']['release_date']
            year = int(release_date.split("-")[0])
            song_features['year'] = year
        
            return song_features

        except Exception as e:
            print(f"Error fetching features for song ID {song_id}: {e}")
            return None

    def playlistInfo(self):
        """
        Extracts and returns the list of song IDs in the playlist.

        Returns:
        list
            A list of song IDs in the playlist.
        """
        playlist_id = self.playlist_url.split("/")[-1].split("?")[0]
        try:
            # Fetch playlist details from Spotify API
            playlist_info = self.sp.playlist(playlist_id)
            # Extract song IDs from the playlist
            songsId = []
            if playlist_info['tracks']['total'] > 0:
                for i in range(playlist_info['tracks']['total']):
                    song_id = playlist_info['tracks']['items'][i]['track']['id']
                    if song_id:
                        songsId.append(song_id)
            return songsId
        except Exception as e:
            print(f"Error fetching playlist info: {e}")
            return []

    def playlistFeatures(self):
        """
        Constructs a DataFrame containing features of all songs in the playlist.

        Returns:
        pd.DataFrame
            DataFrame containing features of all songs in the playlist.
        """
        songs_id = self.playlistInfo()
        playlist_features_list = []
        
        # Fetch features for each song in the playlist
        for song_id in songs_id:
            song_features = self.songFeatures(song_id)
            if song_features:
                song_features['genres'] = ast.literal_eval(song_features['genres'])
                song_df = pd.DataFrame([song_features])
                playlist_features_list.append(song_df)

        # Combine all song features into a single DataFrame
        if playlist_features_list:
            playlist_features = pd.concat(playlist_features_list).reset_index(drop=True)
            # Drop unnecessary columns
            playlist_features.drop(['id', 'type', 'uri', 'track_href', 'analysis_url'], axis=1, inplace=True)
            return playlist_features
        else:
            return pd.DataFrame()

    def recommend(self, N=10):
        """
        Recommends top N songs similar to the songs in the playlist.

        Parameters:
        N : int
            The number of songs to recommend (default is 10).

        Returns:
        tuple
            A tuple containing two elements:
                - list: A list of recommended song IDs.
                - dict: A dictionary containing recommended song names and their artists.
        """
        playlistFeatures = self.playlistFeatures()
        if playlistFeatures.empty:
            return {}
            
        # Rename column for consistency
        playlistFeatures.rename(columns={'artist_popularity': 'popularity'}, inplace=True)

        # List of columns to be scaled
        columns_to_scale = ['popularity', 'duration_ms', 'danceability', 'energy', 'key',
           'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
           'liveness', 'valence', 'tempo', 'time_signature', 'year']

        # scale features values
        playlistFeatures[columns_to_scale] = scaler.transform(playlistFeatures[columns_to_scale])

        # Encode genres
        playlistFeatures = playlistFeatures.join(
                pd.DataFrame.sparse.from_spmatrix(
                    mlb.transform(playlistFeatures.pop('genres')),
                    index=playlistFeatures.index,
                    columns=mlb.classes_))

        # Rearrange the columns to match the original datframe
        playlistFeatures = playlistFeatures[df.columns]

        # Calculate the playlist vector
        playlist_vector = np.sum(playlistFeatures, axis=0)
        playlist_vector = np.array(playlist_vector)
        playlist_vector_normalized = normalize(playlist_vector.reshape(1, -1))

        # Compute cosine similarities
        cos_similarities = cosine_similarity(playlist_vector_normalized, df)
        sorted_indices = cos_similarities.argsort(axis=1)[:, ::-1]

        # Get top N recommended songs IDs
        top_similar_songs_indices = sorted_indices[:, :N]
        recommended_songs_ids = [songsId[index] for index in top_similar_songs_indices[0]]

        # Fetch recommended songs names
        recommended_songs_names = {self.sp.track(song_id)['name']: self.sp.track(song_id)['artists'][0]['name'] for song_id in recommended_songs_ids}
        
        return recommended_songs_ids

# pl = Playlist("https://open.spotify.com/playlist/3uMNeNQpW5hQgYIZoO7j7x?si=16673226eb9f46ac")
# print(pl.recommend())