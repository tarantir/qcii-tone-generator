#!/usr/bin/env python3
"""Cross-platform WAV playback helper shared by the CLI tone generator scripts."""

import platform
import shutil
import subprocess


def find_player():
    system = platform.system()
    if system == "Linux":
        for cmd in ("paplay", "aplay", "ffplay"):
            if shutil.which(cmd):
                return [cmd]
    elif system == "Darwin":
        return ["afplay"]
    elif system == "Windows":
        return None  # handled via winsound
    return None


def play_file(path):
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            player = find_player()
            if not player:
                print(f"No player found. Install 'paplay', 'aplay', or 'ffplay' "
                      f"to preview audio, or open the file manually: {path}")
                return
            subprocess.Popen(player + [path],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Playback failed: {e}")
