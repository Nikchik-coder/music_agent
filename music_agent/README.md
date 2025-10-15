# Music Management Module

This directory contains scripts for downloading and managing music files from various sources, such as Google Drive and SoundCloud. The scripts are designed to be run independently to populate local directories with audio files that can be used by the main application.

## Features

- **Google Drive Downloader**: `load_songs_google_drive.py`
  - Downloads all audio files from a specified public Google Drive folder.
  - Skips files that already exist locally to save bandwidth.
  - Requires Google API credentials for authentication.

- **SoundCloud Downloader**: `load_songs_soundcloud.py`
  - Downloads tracks from a list of SoundCloud URLs (supports both individual tracks and playlists).
  - Skips tracks that have already been downloaded.
  - Fetches music from playlists and individual tracks.

- **Playlist Generator**: `playlist.py`
  - Scans a specified directory for supported audio files (`.mp3`, `.wav`, etc.).
  - Generates a shuffled playlist of the discovered tracks.
  - Can be used to prepare a randomized queue of songs for streaming.

## Setup

Before running any of the scripts, ensure you have the necessary dependencies installed.

### 1. Install Python Libraries

Install all required packages using the main `requirements.txt` file from the project root:

```bash
pip install -r ../requirements.txt
```
This will install `gdown`, `soundcloud-lib`, `google-api-python-client`, and other necessary libraries.

### 2. Google Drive API Credentials

To use the Google Drive downloader, you must set up Google API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the **Google Drive API**.
4. Create credentials for an **OAuth client ID**:
   - Select **Desktop app** as the application type.
   - Download the JSON file containing your credentials.
5. Rename the downloaded file to `client_secret.json` and place it in the `youtube_interface` directory.

The first time you run `load_songs_google_drive.py`, you will be prompted to authorize the application through your browser. This will create a `token.json` file in the same directory, which stores your credentials for future runs.

## Usage

### Downloading Songs from Google Drive

1. Open `load_songs_google_drive.py`.
2. Modify the `folder_url` variable to point to your public Google Drive folder.
3. Run the script from the terminal:

```bash
python music/load_songs_google_drive.py
```

The script will create a `google_drive_songs` folder inside the `music` directory and download all new songs into it.

### Downloading Songs from SoundCloud

1. Open `load_songs_soundcloud.py`.
2. Update the `URLS_TO_DOWNLOAD` list with the SoundCloud track or playlist URLs you want to download.
3. Run the script:

```bash
python music/load_songs_soundcloud.py
```

The script will create a `soundcloud_songs` folder and save all downloaded tracks there. Note that this script can only download tracks that the artist has made available for download.

### Generating a Playlist

The `playlist.py` script is intended to be used by other modules within the application. It provides a function `get_shuffled_playlist(folder_path)` that returns a shuffled list of audio files from a given folder.


## File Descriptions

- **`load_songs_google_drive.py`**: Script to authenticate with the Google Drive API and download audio files.
- **`load_songs_soundcloud.py`**: Script to download tracks from SoundCloud using the `soundcloud-lib` library.
- **`playlist.py`**: A utility module to scan a folder and create a shuffled playlist of audio files.
- **`/songs/`**: (Potentially deprecated) A directory for storing music.
- **`/soundcloud_songs/`**: Default output directory for songs downloaded from SoundCloud.
- **`/google_drive_songs/`**: Default output directory for songs downloaded from Google Drive.
- **`README.md`**: This file.


#Activate venv
.\venv\Scripts\Activate.ps1