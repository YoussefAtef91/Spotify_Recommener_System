from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class PlaylistForm(FlaskForm):
    playlist_url = StringField('Playlist Url', validators=[DataRequired()])
    submit = SubmitField("Submit")