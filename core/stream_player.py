import os
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox
from tkinter import StringVar
import time

# for volume controls
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# make surre libmpv-2.dll is found
os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ.get("PATH", "")

try:
    import mpv
except ImportError:
    messagebox.showerror("Error", "Missing python-mpv. Run: pip install python-mpv")
    sys.exit(1)

# ctk theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# volume ccontrol (system volume using pycaw)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

def set_system_volume(level: float):
    volume_interface.SetMasterVolumeLevelScalar(level, None)

def get_system_volume():
    return volume_interface.GetMasterVolumeLevelScalar()

def format_time(seconds):
    try:
        seconds = int(seconds)
        return f"{seconds // 60:02}:{seconds % 60:02}"
    except:
        return "00:00"

class AudioPlayerApp(ctk.CTk):
    def __init__(self, url):
        super().__init__()
        self.title("Streaming...")
        self.geometry("500x365")
        self.resizable(False, False)

        self.url = url
        self.is_paused = False
        self.duration = 0

        self.player = mpv.MPV(
            ytdl=True,
            vo='null',
            vid='no',
            input_default_bindings=True,
            input_vo_keyboard=True,
            log_handler=self.log,
            loglevel='error',
            osc=False
        )

        # title
        self.title_label = ctk.CTkLabel(self, text="Streaming...", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(15, 10))

        # time label
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(fill="x", padx=20)

        self.current_time_label = ctk.CTkLabel(time_frame, text="00:00", width=40)
        self.current_time_label.pack(side="left")

        self.total_time_label = ctk.CTkLabel(time_frame, text="--:--", width=40)
        self.total_time_label.pack(side="right")

        # seek bar
        self.seek_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.on_seek)
        self.seek_slider.pack(fill="x", padx=20, pady=5)

        # play/pause buttom
        self.play_pause_button = ctk.CTkButton(self, text="Pause", command=self.toggle_play_pause)
        self.play_pause_button.pack(pady=10)

        # volume fram
        vol_frame = ctk.CTkFrame(self, fg_color="transparent")
        vol_frame.pack(pady=10)

        self.volume_label = ctk.CTkLabel(vol_frame, text="Volume")
        self.volume_label.pack()

        self.volume_slider = ctk.CTkSlider(vol_frame, from_=0, to=100, orientation="vertical", height=100,
                                           command=self.on_volume_change)
        self.volume_slider.set(get_system_volume() * 100)
        self.volume_slider.pack()

        # exit
        self.exit_button = ctk.CTkButton(self, text="Exit", command=self.quit_player)
        self.exit_button.pack(pady=10)

        # slider update
        self.after(1000, self.update_slider)

        # accual playback
        threading.Thread(target=self.start_playback, daemon=True).start()

    def log(self, loglevel, component, message):
        print(f"[{loglevel}] {component}: {message}")

    def start_playback(self):
        self.player.play(self.url)
        while not self.duration:
            try:
                self.duration = self.player.duration or 0
                self.seek_slider.configure(to=self.duration)
                self.total_time_label.configure(text=format_time(self.duration))
            except:
                pass

    def toggle_play_pause(self):
        if self.is_paused:
            self.player.pause = False
            self.play_pause_button.configure(text="Pause")
        else:
            self.player.pause = True
            self.play_pause_button.configure(text="Play")
        self.is_paused = not self.is_paused

    def on_seek(self, value):
        try:
            if self.duration:
                self.player.seek(float(value) - self.player.time_pos, reference="absolute")
        except:
            pass

    def on_volume_change(self, val):
        try:
            set_system_volume(float(val) / 100.0)
        except:
            pass

    def update_slider(self):
        try:
            if self.player.time_pos is not None:
                self.seek_slider.set(self.player.time_pos)
                self.current_time_label.configure(text=format_time(self.player.time_pos))
        except:
            pass
        self.after(1000, self.update_slider)

    def quit_player(self):
        self.player.quit()
        self.destroy()


# args
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Audio URL to play (mp3, m3u8, etc.)")
    args = parser.parse_args()

    app = AudioPlayerApp(args.url)
    app.mainloop()
