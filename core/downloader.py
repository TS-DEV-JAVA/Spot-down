import argparse
import subprocess
import sys
import os
import re
import time
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import requests
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover

console = Console()

SPOTIFY_CLIENT_ID = "c08a57aa02c44831937550169d549d79"
SPOTIFY_CLIENT_SECRET = "bba2736cde3140049a66c1348454aeaf"

parser = argparse.ArgumentParser(description="Spot-down-core-dl, part of spot-down project")
parser.add_argument("url", help="Spotify track URL")
parser.add_argument("--format", default="mp3", help="Audio format (e.g., mp3, flac, m4a, opus)")
parser.add_argument("--good-meta", action="store_true", help="Embed high quality metadata and album art")
parser.add_argument("-o", "--output", default=".", help="Output directory")
args = parser.parse_args()

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)
ytmusic = YTMusic()


def get_spotify_metadata(spotify_url):
    track = sp.track(spotify_url)
    return {
        "title": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "cover_url": track['album']['images'][0]['url']
    }


def search_ytmusic(metadata):
    query = f"{metadata['title']} {metadata['artist']}"
    results = ytmusic.search(query, filter="songs")
    if not results:
        console.print("[bold red]Error: Failed To Find a match while web scraping[/bold red]")
        sys.exit(1)
    return f"https://music.youtube.com/watch?v={results[0]['videoId']}"


def safe_filename(s):
    return re.sub(r'[\\/*?:"<>|]', "", s)


def show_banner():
    banner = Text()
    banner.append("Spot-down-core-dl", style="bold cyan on black")
    console.print(Panel(banner, style="bold green", box=box.ROUNDED, expand=False))


def download_from_youtube(url, filename, audio_format):
    output_template = f"{filename}.%(ext)s"
    with Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[progress.description]{task.description}", style="bold cyan"),
        BarColumn(bar_width=40, style="bold green"),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Downloading...", total=None)
        try:
            subprocess.run(
                [
                    "yt-dlp",
                    "-x",
                    "--audio-format", audio_format,
                    "-o", output_template,
                    "--quiet",
                    "--no-warnings"
                ] + [url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            console.print("[bold red]Failed to download from YouTube.[/bold red]")
            sys.exit(1)
        progress.update(task, completed=100)


def embed_metadata(filename, metadata, audio_format):
    file_path = f"{filename}.{audio_format}"
    cover_path = os.path.join(os.path.dirname(filename), os.path.basename(filename) + "_cover.jpg")

    # dl the cover
    try:
        response = requests.get(metadata['cover_url'], timeout=10)
        if response.ok:
            with open(cover_path, "wb") as f:
                f.write(response.content)
        else:
            console.print("[bold red]Failed to fetch cover image.[/bold red]")
            return
    except Exception as e:
        console.print(f"[bold red]Error downloading cover: {e}[/bold red]")
        return

    title = metadata['title']
    artist = metadata['artist']
    album = metadata['album']

    try:
        if audio_format == "mp3":
            subprocess.run([
                "ffmpeg", "-y", "-i", file_path, "-i", cover_path,
                "-map", "0", "-map", "1", "-c", "copy",
                "-id3v2_version", "3",
                "-metadata", f"title={title}",
                "-metadata", f"artist={artist}",
                "-metadata", f"album={album}",
                "-metadata:s:v", "title=Album cover",
                "-metadata:s:v", "comment=Cover (front)",
                f"{filename}_tagged.mp3"
            ], check=True)
            os.replace(f"{filename}_tagged.mp3", file_path)

        elif audio_format == "flac":
            audio = FLAC(file_path)
            audio["title"] = title
            audio["artist"] = artist
            audio["album"] = album

            image = Picture()
            image.type = 3
            image.mime = "image/jpeg"
            image.desc = "Cover"
            image.data = open(cover_path, "rb").read()
            audio.clear_pictures()
            audio.add_picture(image)
            audio.save()

        elif audio_format == "m4a":
            audio = MP4(file_path)
            audio["\xa9nam"] = title
            audio["\xa9ART"] = artist
            audio["\xa9alb"] = album
            with open(cover_path, "rb") as img:
                audio["covr"] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()

        elif audio_format == "ogg":
            audio = OggVorbis(file_path)
            audio["title"] = title
            audio["artist"] = artist
            audio["album"] = album
            audio.save()

        else:
            console.print(f"[bold yellow]Metadata embedding not supported for format: {audio_format}[/bold yellow]")
            return

        console.print("[bold green]Metadata and cover embedded successfully.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Failed to embed metadata: {e}[/bold red]")

    finally:
        if os.path.exists(cover_path):
            os.remove(cover_path)


def main():
    show_banner()
    metadata = get_spotify_metadata(args.url)
    final_name = f"{metadata['title']} — {metadata['artist']} ({metadata['album']})"
    safe_name = os.path.join(args.output, safe_filename(final_name))

    console.print(Panel.fit(
        f"[bold green]Track:[/] [bold cyan]{metadata['title']}[/]\n"
        f"[bold green]Artist:[/] [bold magenta]{metadata['artist']}[/]\n"
        f"[bold green]Album:[/] [bold yellow]{metadata['album']}[/]",
        title="Metadata Extracted", border_style="bright_magenta"
    ))

    console.print(f"[bold blue]Scraping Youtube music for:[/] [italic]{metadata['title']} by {metadata['artist']}[/italic]")
    video_url = search_ytmusic(metadata)

    console.print(f"[bold green]Found:[/] [link={video_url}]{video_url}[/link]")
    download_from_youtube(video_url, safe_name, args.format)

    if args.good_meta:
        console.print("[bold cyan]Embedding metadata and cover art...[/bold cyan]")
        embed_metadata(safe_name, metadata, args.format)

    console.print(Panel.fit(
        f"[bold green]Saved as:[/] [bold yellow]{safe_name}.{args.format}[/bold yellow]",
        style="bold green", border_style="green", box=box.DOUBLE
    ))


if __name__ == "__main__":
    main()
