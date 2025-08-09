import json
import subprocess
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box

# good tui thingy like the one that launches rich console
console = Console()

# load config json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    console.print(f"[bold red] Failed to load config.json: {e}[/bold red]")
    exit()

# spotify creds 
SPOTIPY_CLIENT_ID = "c08a57aa02c44831937550169d549d79"
SPOTIPY_CLIENT_SECRET = "bba2736cde3140049a66c1348454aeaf"

# spotipy setup
try:
    sp = Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    ))
except Exception as e:
    console.print(f"[bold red] Spotify Auth Error: {e}[/bold red]")
    exit()

# search prompt
console.print(Panel("[bold magenta]Spot-down-search-streamer[/bold magenta]", style="bold purple", expand=False))
query = Prompt.ask("[bold yellow] Search track or artist[/bold yellow]")

try:
    results = sp.search(q=query, type='track', limit=20)
    tracks = results['tracks']['items']
except Exception as e:
    console.print(f"[bold red] Spotify Search Error: {e}[/bold red]")
    exit()

if not tracks:
    console.print("[bold red] No results found[/bold red]")
    exit()

# show results
table = Table(title="[bold purple]Search Results[/bold purple]", box=box.MINIMAL_DOUBLE_HEAD, expand=False, padding=(0, 1))
table.add_column("#", justify="right", style="bold red", no_wrap=True)
table.add_column("Track", style="bold cyan", overflow="fold")
table.add_column("Artist(s)", style="bold blue", overflow="fold")

for i, track in enumerate(tracks, 1):
    name = track['name']
    artists = ", ".join([a['name'] for a in track['artists']])
    table.add_row(str(i), name, artists)

console.print(table)

# choose
try:
    choice = IntPrompt.ask("[bold green] Pick a track by number[/bold green]", choices=[str(i) for i in range(1, len(tracks)+1)])
except Exception:
    console.print("[bold red] Invalid input[/bold red]")
    exit()

# get the track url
chosen_track = tracks[choice - 1]
track_url = chosen_track['external_urls']['spotify']
track_name = chosen_track['name']
track_artists = ", ".join([a['name'] for a in chosen_track['artists']])

# summary/meta table thing
summary = f"""
[bold cyan]Track: {track_name}[/bold cyan]
[bold blue]Artist(s):{track_artists}[/bold blue]

[bold green]Status: Streaming...[/bold green]
"""
console.print(Panel.fit(summary.strip(), title="[bold green]Track Selected[/bold green]", style="bold dark_red"))

# extract to RAW streamable URL with extractor.py script
extract_cmd = [
    "python",
    "core/extractor.py",
    "--url", track_url
]

try:
    console.print("[bold purple] Extracting audio stream URL...[/bold purple]")
    result = subprocess.run(extract_cmd, capture_output=True, text=True, check=True)
    direct_audio_url = result.stdout.strip()

    if not direct_audio_url.startswith("http"):
        raise ValueError("Invalid URL received")

    console.print(f"[bold green] Streaming:[/] [link={direct_audio_url}]{direct_audio_url}[/link]")

    # stream it
    subprocess.run(["py", "core/stream_player.py", "--url", direct_audio_url])

except subprocess.CalledProcessError as e:
    console.print(f"[bold red] extractor.py failed: {e}[/bold red]")
except Exception as e:
    console.print(f"[bold red] Error: {e}[/bold red]")
