"""
This script is used to upload songs to SoundCloud.
It also handles token refresh and ensures the track and playlist are public for successful addition.
"""

import requests
import os
import logging
from config.config import soundcloud_settings
from dotenv import find_dotenv, set_key

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class SoundCloudUploader:
    """
    A class to handle uploading songs to SoundCloud, with automatic token refresh.
    """

    def __init__(self):
        """
        Initializes the SoundCloudUploader with credentials from settings.
        """
        self.client_id = soundcloud_settings.SOUNDCLOUD_CLIENT_ID
        self.client_secret = soundcloud_settings.SOUNDCLOUD_CLIENT_SECRET
        self.access_token = soundcloud_settings.SOUNDCLOUD_ACCESS_TOKEN
        self.refresh_token = soundcloud_settings.SOUNDCLOUD_REFRESH_TOKEN
        self.token_url = "https://api.soundcloud.com/oauth2/token"
        self.api_base_url = "https://api.soundcloud.com"

        if not self.access_token:
            logging.error(
                "SOUNDCLOUD_ACCESS_TOKEN is not set. Please run the initial token script first."
            )

    def _get_auth_headers(self):
        """
        Returns the authorization headers for API requests.
        """
        return {"Authorization": f"OAuth {self.access_token}"}

    def _refresh_and_save_tokens(self) -> bool:
        """
        Uses the refresh token to get a new access token and saves it to the .env file.
        Returns True on success, False on failure.
        """
        logging.warning("Access Token has expired. Attempting to refresh...")

        if not self.refresh_token:
            logging.error(
                "Cannot refresh: SOUNDCLOUD_REFRESH_TOKEN is not set in your .env file."
            )
            return False

        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        try:
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            data = response.json()

            new_access_token = data.get("access_token")
            new_refresh_token = data.get(
                "refresh_token"
            )  # SoundCloud might issue a new one

            if not new_access_token:
                logging.error("Refresh failed: Did not receive a new access token.")
                return False

            # Find the .env file in your project
            dotenv_path = find_dotenv()
            if not dotenv_path:
                logging.error("Could not find .env file to update.")
                return False

            # Safely update the .env file with the new token(s)
            set_key(dotenv_path, "SOUNDCLOUD_ACCESS_TOKEN", new_access_token)
            logging.info("Successfully updated SOUNDCLOUD_ACCESS_TOKEN in .env file.")

            # Also update the token in our currently running instance and settings object
            self.access_token = new_access_token
            soundcloud_settings.SOUNDCLOUD_ACCESS_TOKEN = new_access_token

            if new_refresh_token:
                set_key(dotenv_path, "SOUNDCLOUD_REFRESH_TOKEN", new_refresh_token)
                self.refresh_token = new_refresh_token
                soundcloud_settings.SOUNDCLOUD_REFRESH_TOKEN = new_refresh_token
                logging.info(
                    "Successfully updated SOUNDCLOUD_REFRESH_TOKEN in .env file."
                )

            return True

        except requests.exceptions.RequestException as e:
            logging.error(f"An API error occurred during token refresh: {e}")
            if e.response is not None:
                logging.error(f"Error details: {e.response.text}")
            return False

    def upload(
        self,
        file_path: str,
        playlist_name: str,
        track_title: str,
        is_retry: bool = False,
    ) -> bool:
        """
        Uploads a song to SoundCloud. Automatically handles token refresh and ensures
        both the track and playlist are public for successful addition.
        """
        if not os.path.exists(file_path):
            logging.error(f"The file '{file_path}' was not found.")
            return False
        if not self.access_token:
            logging.error(
                "SOUNDCLOUD_ACCESS_TOKEN is not set. Please run the initial token script first."
            )
            return False

        try:
            # --- 1. VERIFY AUTHENTICATION ---
            logging.info("Verifying authentication...")
            me_response = requests.get(
                f"{self.api_base_url}/me", headers=self._get_auth_headers()
            )
            me_response.raise_for_status()
            me_data = me_response.json()
            logging.info(f"Successfully authenticated as: {me_data['username']}")

            # --- 2. UPLOAD THE TRACK AS PUBLIC ---
            logging.info(f"Uploading track as PUBLIC: '{track_title}'...")
            track_data = {
                "track[title]": track_title,
                "track[sharing]": "public",
            }  # Ensure track is public
            files = {
                "track[asset_data]": (
                    os.path.basename(file_path),
                    open(file_path, "rb"),
                )
            }
            upload_response = requests.post(
                f"{self.api_base_url}/tracks",
                headers=self._get_auth_headers(),
                data=track_data,
                files=files,
            )
            upload_response.raise_for_status()
            new_track = upload_response.json()
            new_track_id = new_track["id"]
            logging.info(f"Track uploaded successfully. Track ID: {new_track_id}")

            # --- 3. FIND THE TARGET PLAYLIST ---
            logging.info(f"Searching for playlist: '{playlist_name}'...")
            playlists_response = requests.get(
                f"{self.api_base_url}/me/playlists", headers=self._get_auth_headers()
            )
            playlists_response.raise_for_status()
            target_playlist = next(
                (
                    p
                    for p in playlists_response.json()
                    if p["title"].lower() == playlist_name.lower()
                ),
                None,
            )
            if not target_playlist:
                logging.warning(
                    f"Playlist '{playlist_name}' not found. Track was uploaded but not added to a playlist."
                )
                return True
            playlist_id = target_playlist["id"]
            logging.info(f"Found playlist. Playlist ID: {playlist_id}")

            # --- NEW STEP 3.5: ENSURE PLAYLIST IS PUBLIC ---
            if target_playlist.get("sharing") != "public":
                logging.warning(
                    f"Playlist '{playlist_name}' is private. Changing to public to ensure track can be added."
                )
                playlist_update_payload = {"playlist": {"sharing": "public"}}
                requests.put(
                    f"{self.api_base_url}/playlists/{playlist_id}",
                    headers=self._get_auth_headers(),
                    json=playlist_update_payload,
                ).raise_for_status()
                logging.info("Playlist successfully updated to public.")

            # --- 4. ADD THE TRACK TO THE PLAYLIST ---
            current_track_ids = [track["id"] for track in target_playlist["tracks"]]
            new_track_ids = current_track_ids + [new_track_id]
            form_data_payload = {"playlist[tracks][]": new_track_ids}
            update_response = requests.put(
                f"{self.api_base_url}/playlists/{playlist_id}",
                headers=self._get_auth_headers(),
                data=form_data_payload,
            )
            update_response.raise_for_status()
            logging.info(
                f"SUCCESS! Track '{new_track['title']}' has been added to playlist '{target_playlist['title']}'."
            )
            return True

        except requests.exceptions.RequestException as e:
            # --- Error handling block (no changes here) ---
            if e.response is not None and e.response.status_code == 401:
                if is_retry:
                    logging.error(
                        "Authentication failed even after refreshing the token. Please check your credentials."
                    )
                    return False
                if self._refresh_and_save_tokens():
                    logging.info("Token refreshed successfully. Retrying the upload...")
                    return self.upload(
                        file_path, playlist_name, track_title, is_retry=True
                    )
                else:
                    logging.error(
                        "Could not refresh token. Please run the initial token script to re-authenticate."
                    )
                    return False
            else:
                logging.error(f"An API error occurred: {e}")
                if e.response is not None:
                    logging.error(f"Error details: {e.response.text}")
                return False


def main():
    """Main function to configure and run the script."""
    # --- CONFIGURE YOUR UPLOAD HERE ---
    audio_file_path = "music_generator/soundcloud_songs/Lumira - Candy-Coated Chaos.mp3"
    target_playlist_name = "Draft"
    new_track_title = "Lumira - Candy-new"
    # ----------------------------------

    uploader = SoundCloudUploader()
    uploader.upload(
        file_path=audio_file_path,
        playlist_name=target_playlist_name,
        track_title=new_track_title,
    )


if __name__ == "__main__":
    main()
