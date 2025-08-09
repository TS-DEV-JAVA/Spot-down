import argparse
import sys
import subprocess
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import youtube_scrape  # import custom module

SPOTIFY_CLIENT_ID = "c08a57aa02c44831937550169d549d79"
SPOTIFY_CLIENT_SECRET = "bba2736cde3140049a66c1348454aeaf"

parser = argparse.ArgumentParser(description="Get direct audio URL from Spotify track via YouTube")
parser.add_argument("--url", required=True, help="Spotify track URL")
args = parser.parse_args()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

def get_spotify_metadata(spotify_url):
    track = sp.track(spotify_url)
    return {
        "title": track['name'],
        "artist": track['artists'][0]['name']
    }

def search_youtube(metadata):
    query = f"{metadata['title']} {metadata['artist']}"
    youtube_url = youtube_scrape.scrape_first_url(query)
    if not youtube_url:
        print("Error: No YouTube result found.", file=sys.stderr)
        sys.exit(1)
    return youtube_url

def get_direct_audio_url(yt_url):
    try:
        result = subprocess.run(
            ["yt-dlp", "-f", "bestaudio[ext!=m3u8]/bestaudio", "-g", "--no-warnings", yt_url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: yt-dlp failed.", file=sys.stderr)
        sys.exit(1)

# main proccess
metadata = get_spotify_metadata(args.url)
youtube_url = search_youtube(metadata)
audio_url = get_direct_audio_url(youtube_url)
print(audio_url)
