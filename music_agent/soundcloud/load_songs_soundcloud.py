import os
from config.config import SoundcloudSettings
from sclib.sync import SoundcloudAPI, Track, Playlist

from app_logging.logger import logger


class Soundcloud:
    """
    Class to load songs from SoundCloud.
    """

    def __init__(self, settings: SoundcloudSettings):
        self.api = SoundcloudAPI()
        self.output_folder = settings.OUTPUT_FOLDER
        self.urls_to_download = settings.SOUNDCLOUD_PLAYLIST_URL

    def download_track(self, track: Track) -> None:
        """Downloads a single track to the specified folder."""
        # Sanitize the title and artist to create a valid filename
        safe_title = "".join(
            c for c in track.title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_artist = "".join(
            c for c in track.artist if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        filename = os.path.join(self.output_folder, f"{safe_artist} - {safe_title}.mp3")

        # Check if the file already exists
        if os.path.exists(filename):
            logger.info(f"  Skipping, already exists: {os.path.basename(filename)}")
            return
        logger.info(f"Output folder: {self.output_folder}")
        logger.info(f"  Downloading: {track.artist} - {track.title}")
        try:
            with open(filename, "wb+") as file:
                track.write_mp3_to(file)
            logger.info(f"  Successfully downloaded: {os.path.basename(filename)}")
        except Exception as e:
            # Note: This library cannot download tracks that are not made
            # "Downloadable" by the artist.
            logger.error(f"  Failed to download {track.title}. Error: {e}")

    def download_songs(self) -> None:
        """
        Main function to download all tracks from a list of SoundCloud URLs,
        which can be single tracks or playlists.
        """
        os.makedirs(self.output_folder, exist_ok=True)
        logger.info(f"Songs will be saved in: {self.output_folder}")
        logger.info(f"Found {len(self.urls_to_download)} URL(s) to process.")

        for i, url in enumerate(self.urls_to_download):
            logger.info(
                f"\n--- Processing URL {i + 1}/{len(self.urls_to_download)} ---"
            )
            logger.info(f"Resolving: {url}")

            try:
                # Resolve the URL. It can return a Track or a Playlist object.
                resolved_item = self.api.resolve(url)

                if isinstance(resolved_item, Playlist):
                    logger.info(
                        f"Playlist found: '{resolved_item.title}' with {len(resolved_item.tracks)} tracks."
                    )
                    # Iterate through all tracks in the playlist and download them
                    for playlist_track in resolved_item.tracks:
                        self.download_track(playlist_track)

                elif isinstance(resolved_item, Track):
                    logger.info("Single track found.")
                    # Download the single track
                    self.download_track(resolved_item)

                else:
                    # This case might occur for invalid URLs
                    logger.warning(
                        f"Could not resolve URL as a track or playlist: {url}"
                    )

            except Exception as e:
                logger.error(f"An error occurred while processing {url}: {e}")

        logger.info("\nScript finished.")


if __name__ == "__main__":

    settings = SoundcloudSettings()
    soundcloud_downloader: Soundcloud = Soundcloud(settings)
    soundcloud_downloader.download_songs()
