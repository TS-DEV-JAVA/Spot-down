import argparse
import os
from urllib.parse import urlparse
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# theme
theme = Theme({
    "primary": "bright_green",
    "label": "cyan",
    "value": "magenta",
    "error": "bold red"
})

console = Console(theme=theme)

# Setup CLI
parser = argparse.ArgumentParser(description="Spotify Metadata Viewer")
parser.add_argument("--url", required=True, help="Spotify track URL")
args = parser.parse_args()

# creds
client_id = os.getenv("SPOTIPY_CLIENT_ID", "c08a57aa02c44831937550169d549d79")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "bba2736cde3140049a66c1348454aeaf")

if not client_id or not client_secret:
    console.print("[error]Missing Spotify credentials[/error]")
    exit(1)

# Setup Spotipy
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def extract_track_id(spotify_url):
    try:
        parsed = urlparse(spotify_url)
        if 'track' in parsed.path:
            return parsed.path.split('/')[-1]
    except Exception:
        pass
    return None

track_id = extract_track_id(args.url)
if not track_id:
    console.print("[error]Invalid Spotify track URL[/error]")
    exit(1)

# Fetch track metadata
try:
    track = sp.track(track_id)
except Exception as e:
    console.print(f"[error]Failed to fetch metadata: {e}[/error]")
    exit(1)

# Display metadata
table = Table(title="Spotify Track Metadata", title_style="primary")
table.add_column("Field", style="label")
table.add_column("Value", style="value")

table.add_row("Name", track["name"])
table.add_row("Artist(s)", ", ".join([a["name"] for a in track["artists"]]))
table.add_row("Album", track["album"]["name"])
table.add_row("Release Date", track["album"]["release_date"])
table.add_row("Duration (ms)", str(track["duration_ms"]))
table.add_row("Explicit", "Yes" if track["explicit"] else "No")
table.add_row("Popularity", str(track["popularity"]))
table.add_row("Track ID", track["id"])
table.add_row("Preview URL", track["preview_url"] or "None")

console.print(table)
