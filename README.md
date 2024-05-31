# Spotify Songs Recommender System

## Project Description

This project implements a Spotify song recommender system using three different Spotify datasets. The recommender system classifies songs based on various features such as popularity, danceability, energy, and genre, among others. By analyzing the songs in a given Spotify playlist, the system recommends the top N songs that are similar to the playlist's overall profile.

## Data Description

The project uses three different datasets containing information about tracks and artists. These datasets are stored in the `data` folder:

- `archive`: Contains datasets of tracks and a dataset of artists with their popularity and genres.
- `archive (1)`: Contains a dataset of tracks.
- `archive (2)`: Contains a dataset of tracks.

### Columns in the Datasets

- `id`: Unique identifier for the song.
- `name`: Name of the song.
- `popularity`: Popularity score of the song.
- `duration_ms`: Duration of the song in milliseconds.
- `danceability`: Danceability score of the song.
- `energy`: Energy score of the song.
- `key`: Key in which the song is composed.
- `loudness`: Loudness level of the song.
- `mode`: Mode (major or minor) of the song.
- `speechiness`: Speechiness score of the song.
- `acousticness`: Acousticness score of the song.
- `instrumentalness`: Instrumentalness score of the song.
- `liveness`: Liveness score of the song.
- `valence`: Valence score of the song.
- `tempo`: Tempo of the song in beats per minute.
- `time_signature`: Time signature of the song.
- `artist_name`: Name of the artist.
- `artist_id`: Unique identifier for the artist.
- `year`: Release year of the song.
- `genre`: Genre of the song.
- `genres`: List of genres associated with the artist.
- `artist_popularity`: Popularity score of the artist.

## Requirements

The project requires the following Python libraries:

- pandas
- numpy
- matplotlib
- tqdm
- spotipy
- ast
- os
- dotenv
- scikit-learn

To install the necessary libraries, run:

```bash
pip install pandas numpy matplotlib tqdm spotipy python-dotenv scikit-learn
```

## Directory Structure

The project has the following structure:

```
.
├── data
│   ├── archive
│   │   ├── tracks.csv
│   │   ├── artists.csv
│   ├── archive (1)
│   │   ├── tracks.csv
│   ├── archive (2)
│   │   ├── tracks.csv
├── models
│   ├── df.pkl
│   ├── mlb.pkl
│   ├── scaler.pkl
│   ├── songId.pkl
├── notebooks
│   ├── 00_preprocessing.ipynb
│   ├── 01_recommender.ipynb
├── README.md
```
