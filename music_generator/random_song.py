"""
This module is used to get a random song from the playlist and play it on the stream
"""

import logging
import os
import random

SUPPORTED_EXTENSIONS = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]


def get_shuffled_playlist(folder_path: str) -> list[str]:
    """
    Scans a directory for audio files and returns a shuffled playlist.

    Args:
        folder_path (str): The path to the folder containing music files.

    Returns:
        list[str]: A shuffled list of absolute paths to the music files.

    """
    if not os.path.isdir(folder_path):
        logging.error(f"Music folder not found: {folder_path}")
        return []

    try:
        music_files = []
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                full_path = os.path.join(os.path.abspath(folder_path), filename)
                music_files.append(full_path)

        if not music_files:
            logging.warning(f"No supported audio files found in: {folder_path}")
            return []

        random.shuffle(music_files)
        logging.info(f"Created a shuffled playlist with {len(music_files)} songs.")
        logging.info(f"playlist: {music_files}")
        return music_files
    except Exception as e:
        logging.error(f"Failed to scan music folder '{folder_path}': {e}")
        return []


def get_random_song(folder_path: str) -> str:
    """
    Get a random song from the playlist.
    """
    playlist = get_shuffled_playlist(folder_path)
    return random.choice(playlist)


if __name__ == "__main__":
    print(get_random_song("music/soundcloud_songs"))
