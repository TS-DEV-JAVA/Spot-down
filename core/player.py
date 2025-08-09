import argparse
import os
import wave
import pyaudio
import subprocess
from pathlib import Path
import tempfile
import threading
import shutil
import tkinter as tk
from PIL import Image, ImageTk


def extract_cover_art(input_file):
    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_image_path = temp_image.name
    temp_image.close()

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-an",  # no audio
            "-vcodec", "copy",
            temp_image_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(temp_image_path) and os.path.getsize(temp_image_path) > 0:
            return temp_image_path
        else:
            os.remove(temp_image_path)
    except Exception:
        pass

    return None


def show_cover_window(cover_path, title="Now Playing"):
    def launch():
        window = tk.Tk()
        window.title(title)
        window.resizable(False, False)
        window.attributes("-fullscreen", False)
        window.configure(bg="black")

        if cover_path:
            img = Image.open(cover_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(window, image=photo, bg="black")
            label.image = photo
            label.pack(padx=20, pady=20)
        else:
            label = tk.Label(window, text="No Cover Art Found", fg="white", bg="black", font=("Arial", 18))
            label.pack(padx=20, pady=20)

        window.mainloop()

    # run tkinter window in another thread
    threading.Thread(target=launch, daemon=True).start()


def convert_to_wav(input_file):
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_wav_path = temp_wav.name
    temp_wav.close()

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-f", "wav",
            temp_wav_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[ERROR] Failed to convert file with ffmpeg: {e}")
        return None

    return temp_wav_path


def play_audio(file_path):
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        return

    # convert to wav aka RAW Audio also aka pcm
    wav_path = convert_to_wav(file_path)
    if not wav_path or not Path(wav_path).exists():
        print("[ERROR] Conversion to .wav failed.")
        return

    # show cover art
    cover_path = extract_cover_art(file_path)
    show_cover_window(cover_path, title=f"Now Playing: {Path(file_path).name}")

    try:
        wf = wave.open(wav_path, 'rb')
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pa.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        pa.terminate()
        wf.close()
    finally:
        os.remove(wav_path)
        if cover_path and Path(cover_path).exists():
            os.remove(cover_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--play", help="Path to ANY audio file to play")
    args = parser.parse_args()

    if args.play:
        play_audio(args.play)
