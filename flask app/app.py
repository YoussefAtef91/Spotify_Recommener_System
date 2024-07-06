from flask import Flask, render_template, url_for, flash, redirect, session
from forms import PlaylistForm
from recommender import Playlist
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dfndsbjfasjfbjebfsfdasfasfasfsaf'

load_dotenv()
client_id = os.getenv('client_id')
secret_id = os.getenv('secret_id')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret_id)
sp = spotipy.Spotify(auth_manager=auth_manager)

@app.route("/", methods=["GET","POST"])
def home():
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist_url = form.playlist_url.data
        pl = Playlist(playlist_url)
        recommendations = pl.recommend()
        session['recommendations'] = recommendations
        session['playlist_url'] = playlist_url
        return redirect(url_for("recommendations"))
    return render_template("home.html", form=form)

@app.route("/recommendations")
def recommendations():
    recommendations = session.get('recommendations', [])
    playlist_url = session.get('playlist_url')
    playlist_id = playlist_url.split("/")[-1]
    return render_template("recommendations.html", title='recommendations page',recommendations=recommendations, playlist_id=playlist_id)


if __name__ == "__main__":
    app.run(debug=True)