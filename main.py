import subprocess
import os
import json
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({
    "title": "bold green",
    "primary": "magenta",
    "highlight": "cyan",
    "value": "green",
    "error": "red",
    "option": "bold magenta",
    "prompt": "bold cyan",
    "success": "green"
})

console = Console(theme=custom_theme)

with open("config.json", "r") as f:
    DEFAULTS = json.load(f)

BANNER = """
[error]
                       ██████  ██▓███   ▒█████  ▄▄▄█████▓▓█████▄  ▒█████   █     █░███▄    █ 
                      ▒██    ▒ ▓██░  ██▒▒██▒  ██▒▓  ██▒ ▓▒▒██▀ ██▌▒██▒  ██▒▓█░ █ ░█░██ ▀█   █   
                      ░ ▓██▄   ▓██░ ██▓▒▒██░  ██▒▒ ▓██░ ▒░░██   █▌▒██░  ██▒▒█░ █ ░█▓██  ▀█ ██▒     
                        ▒   ██▒▒██▄█▓▒ ▒▒██   ██░░ ▓██▓ ░ ░▓█▄   ▌▒██   ██░░█░ █ ░█▓██▒  ▐▌██▒    
                      ▒██████▒▒▒██▒ ░  ░░ ████▓▒░  ▒██▒ ░ ░▒████▓ ░ ████▓▒░░░██▒██▓▒██░   ▓██░    
                      ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░░ ▒░▒░▒░   ▒ ░░    ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▓░▒ ▒ ░ ▒░   ▒ ▒  
                      ░ ░▒  ░ ░░▒░       ░ ▒ ▒░     ░     ░ ▒  ▒   ░ ▒ ▒░   ▒ ░ ░ ░ ░░   ░ ▒░     
                      ░  ░  ░  ░░       ░ ░ ░ ▒    ░       ░ ░  ░ ░ ░ ░ ▒    ░   ░    ░   ░ ░      
                            ░               ░ ░              ░        ░ ░      ░            ░ 
[/error]
[title]                                       Spot-Down -- Best Spotify Downloader [/title]
"""

def show_banner():
    console.print(BANNER)

def show_config(config):
    table = Table(title="[highlight]Spot-Down Configuration[/highlight]", border_style="highlight", style="highlight")
    table.add_column("[title]Setting[title]", style="primary")
    table.add_column("[title]Value[title]", style="value")

    for key, val in config.items():
        table.add_row(key, str(val))
    console.print(table)

def configure(config):
    console.print("\n[option]Configuration[/option]")
    config["format"] = Prompt.ask("[success]Audio format[success]", choices=["mp3", "flac", "m4a", "opus", "wav"], default=config["format"])
    config["bitrate"] = Prompt.ask("[prompt]Bitrate[/prompt]", choices=["auto", "128k", "192k", "256k", "320k"], default=config["bitrate"])
    config["output"] = Prompt.ask("[prompt]Output folder[/prompt]", default=config["output"])
    config["overwrite"] = Prompt.ask("[prompt]Overwrite mode[/prompt]", choices=["skip", "force", "metadata"], default=config["overwrite"])

    # Save the updated config to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    console.print("[success]Configuration saved successfully![/success]")

def run_download(query, config):
    os.makedirs(config["output"], exist_ok=True)
    cmd = [
    "python", "core/downloader.py",
    query,
    f"--format={config['format']}",
    "--good-meta",
    f"-o={config['output']}"
]

    console.print(f"\n[highlight]Downloading:[/highlight] [value]{query}[/value]\n")
    try:
        subprocess.run(cmd, check=True)
        console.print("[success] Download complete.[/success]")
    except subprocess.CalledProcessError as e:
        console.print("\n[error] Error during download.[/error]")
        console.print(f"[error]{str(e)}[/error]")

def show_metadata(query):
    if "?" in query:
        query = query.split("?")[0]

    cmd = ["python", "core/meta.py", "--url=" + query]
    console.print(f"\n[highlight]Fetching metadata for:[/highlight] [value]{query}[/value]\n")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        console.print("[error]Error fetching metadata.[/error]")
        console.print(f"[error]{e}[/error]")

def play_music(config):
    folder = config.get("output", ".")
    supported = (".mp3", ".flac", ".m4a", ".ogg", ".opus", ".wav", ".webm", ".mp4")

    try:
        files = [f for f in os.listdir(folder) if f.lower().endswith(supported)]
    except FileNotFoundError:
        console.print(f"[error]Folder not found: {folder}[/error]")
        return

    if not files:
        console.print("[error]No music files found in output folder.[/error]")
        return

    console.print("\n[highlight]Available Music Files:[/highlight]\n")
    for i, file in enumerate(files, start=1):
        console.print(f"[primary]{i}.[/primary] [value]{file}[/value]")

    while True:
        try:
            index = IntPrompt.ask("\n[prompt]Which one do you want to listen to?[/prompt]", choices=[str(i) for i in range(1, len(files)+1)])
            selected = files[index - 1]
            break
        except (IndexError, ValueError):
            console.print("[error]Invalid choice.[/error]")

    filepath = os.path.join(folder, selected)
    console.print(f"\n[highlight]Playing:[/highlight] [value]{selected}[/value]\n")

    try:
        subprocess.run(["python", "core/player.py", "--play", filepath], check=True)
    except subprocess.CalledProcessError as e:
        console.print("[error]Failed to launch player.[/error]")
        console.print(f"[error]{str(e)}[/error]")

def stream_music():
    url = Prompt.ask("[bold green]Enter Spotify URL to stream[/bold green]")

    try:
        result = subprocess.run(
            ["python", "core/extractor.py", "--url", url],
            capture_output=True,
            text=True,
            check=True
        )

        audio_url = result.stdout.strip()  # this should be just the URL
        if not audio_url.startswith("http"):
            console.print(f"[error]Invalid URL output: {audio_url}[/error]")
            return

        console.print(f"[success]Streaming:[/success] [value]{audio_url}[/value]")

        # plat url using stream_player
        subprocess.run(["python", "core/stream_player.py", "--url", audio_url])

    except subprocess.CalledProcessError as e:
        console.print(f"[error]Extractor failed:[/error] {e.stderr.strip()}")

def main():
    config = DEFAULTS.copy()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        show_banner()
        show_config(config)

        console.print("\n[bold green]Menu[/bold green]")
        console.print("[red]1.[/red] [green]Download from Spotify URL[/green]")
        console.print("[red]2.[/red] [green]Stream from Spotify URL[/green]")
        console.print("[red]3.[/red] [green]Search & Download[/green]")
        console.print("[red]4.[/red] [green]Search & Stream[/green]")
        console.print("[red]5.[/red] [green]View Metadata[/green]")
        console.print("[red]6.[/red] [green]Play Music[/green]")
        console.print("[red]7.[/red] [green]Configure Settings[/green]")
        console.print("[red]8.[/red] [green]Exit[/green]")

        choice = IntPrompt.ask("\n[blue]Select an option[/blue]", choices=[str(i) for i in range(1, 9)])

        if choice == 1:
            query = Prompt.ask("[bold green]Enter a Spotify Url[/bold green]")
            run_download(query, config)
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

        elif choice == 7:
            configure(config)

        elif choice == 5:
            query = Prompt.ask("[green]Enter a spotify Url[/green]")
            show_metadata(query)
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

        elif choice == 6:
            play_music(config)
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

        elif choice == 2:
            stream_music()
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

        elif choice == 8:
            console.print("\n[primary]Goodbye.[/primary]\n")
            break

        elif choice == 3:
            try:
                subprocess.run(["python", "core/search_download.py"], check=True)
            except subprocess.CalledProcessError as e:
                console.print("[error]Search & Download failed.[/error]")
                console.print(f"[error]{str(e)}[/error]")
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

        elif choice == 4:
            try:
                subprocess.run(["python", "core/search_stream.py"], check=True)
            except subprocess.CalledProcessError as e:
                console.print("[error]Search & Stream failed.[/error]")
                console.print(f"[error]{str(e)}[/error]")
            console.input("[prompt]\nPress Enter to continue...[/prompt]")

if __name__ == "__main__":
    main()
