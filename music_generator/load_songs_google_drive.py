# Script to load songs from a Google Drive folder to the local machine
import os
import re

import gdown
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from radio.config import settings

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# The public Google Drive folder link
folder_url = "https://drive.google.com/drive/folders/1SsD065tmCEADKSlQv3oj6pUEhxzjJM0I"

# The path to the folder where you want to save the songs.
script_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.getenv("GOOGLE_DRIVE_MUSIC_DIR") or settings.MUSIC_OUTPUT_DIR

# --- Google Drive API Authentication ---
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
creds = None
# Path to your token and credentials files.
token_path = os.path.join(script_dir, "..", "youtube_interface", "token.json")
client_secrets_path = os.path.join(
    script_dir, "..", "youtube_interface", "client_secret.json"
)


def get_drive_service():
    """Authenticates and returns a Google Drive service object."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred building the Drive service: {error}")
        return None


def get_folder_id_from_url(url):
    """Extracts the folder ID from a Google Drive URL."""
    match = re.search(r"/folders/([0-9A-Za-z_-]{10,})", url, re.IGNORECASE)
    return match.group(1) if match else None


def get_remote_files(service, folder_id):
    """
    Fetches the list of files from a Google Drive folder ID using the API.
    """
    files = []
    page_token = None
    try:
        while True:
            response = (
                service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed=false",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        return files
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


# --- Main script logic ---


def main():
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    print(f"Songs will be saved in: {output_folder}")

    folder_id = get_folder_id_from_url(folder_url)
    if not folder_id:
        print("Could not extract folder ID from the URL.")
        return

    drive_service = get_drive_service()
    if not drive_service:
        print("Could not connect to Google Drive.")
        return

    try:
        existing_files = set(os.listdir(output_folder))
        print(f"\nFound {len(existing_files)} existing songs locally.")
    except FileNotFoundError:
        existing_files = set()
        print("No existing songs found.")

    print("Fetching list of files from Google Drive folder...")
    remote_files = get_remote_files(drive_service, folder_id)

    if remote_files:
        print(f"Found {len(remote_files)} files in the remote folder.")
        new_files_to_download = [
            f for f in remote_files if f["name"] not in existing_files
        ]

        if not new_files_to_download:
            print("\nAll songs are up to date. No new downloads needed.")
        else:
            print(f"\nFound {len(new_files_to_download)} new songs to download:")
            for file_info in new_files_to_download:
                print(f"- {file_info['name']}")

            print("\nStarting download...")
            for file_info in new_files_to_download:
                file_id = file_info["id"]
                file_name = file_info["name"]
                output_path = os.path.join(output_folder, file_name)

                # Use gdown to handle the download.
                file_url = f"https://drive.google.com/uc?id={file_id}"

                print(f"Downloading '{file_name}'...")
                try:
                    gdown.download(url=file_url, output=output_path, quiet=False)
                    print(f"Successfully downloaded '{file_name}'.")
                except Exception as e:
                    print(f"Failed to download '{file_name}'. Error: {e}")
    else:
        print("\nCould not retrieve file list from Google Drive, or folder is empty.")


if __name__ == "__main__":
    main()
