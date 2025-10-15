# SoundCloud Integration Scripts

This directory contains a set of Python scripts for interacting with the SoundCloud API. These scripts provide functionality for both downloading and uploading audio files, managing authentication, and handling token refreshes.

## Scripts Overview

### `load_songs_soundcloud.py`

- **Purpose**: Downloads all tracks from one or more specified SoundCloud playlists.
- **Authentication**: This script does **not** require SoundCloud API credentials. It can be used to publicly scrape and download content.
- **Usage**:
  1. Open `config/config.py`.
  2. Locate the `SoundcloudSettings` class.
  3. Set the `SOUNDCLOUD_PLAYLIST_URL` variable to a list of the playlist URLs you want to download.
  4. Set the `OUTPUT_FOLDER` to the directory where you want to save the downloaded `.mp3` files.
  5. Run the script from the command line: `python -m music_generator.soundcloud.load_songs_soundcloud`

### `soundcloud_auth.py`

- **Purpose**: Performs the initial OAuth2 authentication with the SoundCloud API to get your first `access_token` and `refresh_token`.
- **Authentication**: This is the first step for any action that requires user authentication (like uploading).
- **Setup**: Before running, you must manually update the script with your `CLIENT_ID`, `CLIENT_SECRET`, and a freshly generated `AUTHORIZATION_CODE`.
- **Usage**:
  1. Follow the instructions in the script's docstring to generate an `AUTHORIZATION_CODE`.
  2. Hardcode your credentials directly in the script.
  3. Run the script: `python -m music_generator.soundcloud.soundcloud_auth`
  4. The script will output an `access_token` and a `refresh_token`. **Immediately** copy these values into your `.env` file.



### `soundcloud_api.py`

- **Purpose**: Uploads a local audio file to a specified SoundCloud playlist.
- **Authentication**: Requires a valid `SOUNDCLOUD_ACCESS_TOKEN`. It also includes logic to automatically refresh the token if it has expired.
- **Features**:
  - Uploads a track with a given title.
  - Searches for a playlist by name.
  - Automatically makes the playlist and track public to ensure they can be linked.
  - Handles token expiration and refresh automatically.
- **Usage**:
  1. Configure the script by modifying the variables in the `main()` function:
     - `audio_file_path`: Path to the local `.mp3` file to upload.
     - `target_playlist_name`: The name of the destination playlist on SoundCloud.
     - `new_track_title`: The title for the new track on SoundCloud.
  2. Run the script: `python -m music_generator.soundcloud.soundcloud_api`

## Authentication Workflow

1.  **Initial Setup (`soundcloud_auth.py`)**:
    -   Manually generate an authorization code from a special SoundCloud URL.
    -   Run `soundcloud_auth.py` to get your first `access_token` and `refresh_token`.
    -   Store these tokens securely in your environment variables or `.env` file.

2.  **Uploading (`soundcloud_api.py`)**:
    -   The `SoundCloudUploader` class automatically uses your `access_token`.
    -   If an upload fails with a `401 Unauthorized` error, it will automatically attempt to use the `refresh_token` to get a new `access_token`.
    -   If the refresh is successful, it saves the new tokens to your `.env` file and retries the upload.

3.  **Manual Refresh (`soundcloud_refresh.py`)**:
    -   If you need to manually refresh your token for any other reason, you can run this script directly.