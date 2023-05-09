from bs4 import BeautifulSoup
import requests
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

user_date = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD\n")

while True:
    try:
        user_date = datetime.datetime.strptime(user_date, "%Y-%m-%d").date()
        break
    except ValueError:
        user_date = input("Incorrect data format, should be YYYY-MM-DD, please try again.\n")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{user_date}/")
soup = BeautifulSoup(response.text, "html.parser")
song_names = soup.select("li ul li h3")
soup_names_list = [song.getText(strip=True) for song in song_names]

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
scope = "playlist-modify-private"
REDIRECT_URI = os.environ.get('REDIRECT_URI')
auth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope, redirect_uri=REDIRECT_URI,
                    show_dialog=True, cache_path="cache.txt")
cache_token = auth.get_access_token(as_dict=False)
sp = spotipy.Spotify(cache_token)
user_id = sp.current_user()["id"]
spotify_uri_list = []

for song in soup_names_list:
    try:
        result = sp.search(q=f"track:{song} year:{user_date.year}", type="track", limit=3)
        uri = result["tracks"]["items"][0]["uri"]
        spotify_uri_list.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

response = sp.user_playlist_create(user=user_id, name="Test Playlist", public=False, collaborative=False,
                                   description="This is just a test.")
playlist_id = response['id']
sp.playlist_add_items(playlist_id, spotify_uri_list)
