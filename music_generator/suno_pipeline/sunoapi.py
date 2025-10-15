"""
Suno api for generating songs
"""

import requests
import time
import logging
import sys

logger = logging.getLogger(__name__)


def generate_song_suno(
    suno_settings,
    song_prompt,
    negativeTags,
    vocalGender,
    styleWeight,
    weirdnessConstraint,
    audioWeight,
):
    logger.info("Trying to load the api keys")
    try:
        suno_api_key = suno_settings.SUNO_API_KEY
        callback_url = suno_settings.SUNO_CALLBACK_URL
    except Exception as e:
        logger.error(
            f"The error occured durinh the api keys initialization, stopping the execution {e}"
        )
        sys.exit(1)

    payload = {
        "prompt": song_prompt,
        "style": "",  # leave empty if customMode is false
        "title": "",  # leave empty if customMode is false
        "customMode": False,  # Lyrics auto generation mode
        "instrumental": True, #There should be no vocals in the song if its true
        "model": "V4_5",  # Available models: V3_5, V4, V4_5
        "negativeTags": negativeTags,  # Music styles or traits to exclude from the generated audio.
        "vocalGender": vocalGender,  # Available genders: m, f
        "styleWeight": styleWeight,  # Weight of the provided style guidance. Range 0.00–1.00.
        "weirdnessConstraint": weirdnessConstraint,  # Constraint on creative deviation/novelty. Range 0.00–1.00.
        "audioWeight": audioWeight,  # Weight of the input audio influence (where applicable). Range 0.00–1.00.
        "callBackUrl": callback_url,
    }
    headers = {
        "Authorization": f"Bearer {suno_api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(callback_url, json=payload, headers=headers)

    response_json = response.json()
    logger.info("Initial generation request response:", response_json)

    if response.status_code == 200 and response_json.get("code") == 200:
        task_id = response_json.get("data", {}).get("taskId")
        if not task_id:
            logger.info("Could not find task ID in the response.")
        else:
            feed_url = (
                f"https://api.sunoapi.org/api/v1/generate/record-info?taskId={task_id}"
            )

            for i in range(60):  # Poll for up to 10 minutes (60 attempts * 10 seconds)
                logger.info(f"Polling for results (attempt {i + 1}/60)...")
                time.sleep(10)

                feed_response = requests.get(feed_url, headers=headers)

                if feed_response.status_code == 200:
                    feed_data = feed_response.json()
                    logger.info("Current feed status:", feed_data)

                    if feed_data.get("code") == 200:
                        task_details = feed_data.get("data", {})
                        status = task_details.get("status")

                        if status == "SUCCESS":
                            logger.info("Audio generation is complete!")
                            # The song details are nested within the 'response' and 'sunoData' keys.
                            response_data = task_details.get("response", {})
                            songs = response_data.get("sunoData", [])
                            filenames = []
                            titles = []
                            for item in songs:
                                audio_url = item.get(
                                    "audioUrl"
                                )  # Corrected key from 'audio_url' to 'audioUrl'
                                title = item.get("title", "untitled_song")
                                if audio_url:
                                    logger.info(f"Downloading '{title}'...")
                                    audio_get_response = requests.get(audio_url)
                                    if audio_get_response.status_code == 200:
                                        filename = f"{title.replace(' ', '_')}.mp3"
                                        with open(filename, "wb") as f:
                                            f.write(audio_get_response.content)
                                        logger.info(
                                            f"Successfully saved audio to '{filename}'"
                                        )
                                        filenames.append(filename)
                                        titles.append(title)
                                    else:
                                        logger.info(
                                            f"Failed to download audio from {audio_url}"
                                        )
                            return filenames, titles
                        elif status in [
                            "CREATE_TASK_FAILED",
                            "GENERATE_AUDIO_FAILED",
                            "CALLBACK_EXCEPTION",
                            "SENSITIVE_WORD_ERROR",
                        ]:
                            logger.info(
                                f"Audio generation failed with status: {status}. Message: {task_details.get('msg')}"
                            )
                            return None, None
                        else:
                            logger.info(
                                f"Generation in progress. Current status: '{status}'"
                            )
                    else:
                        logger.info(f"API error while polling: {feed_data.get('msg')}")
                else:
                    logger.info(
                        f"Polling failed with status code: {feed_response.status_code}. Response: {feed_response.text}"
                    )
            else:
                logger.info(
                    "Polling timed out. The generation is taking longer than expected or has failed."
                )
                return None, None
    else:
        logger.info(
            f"Failed to start the audio generation task. Status: {response.status_code}, Response: {response.text}"
        )
        return None, None
