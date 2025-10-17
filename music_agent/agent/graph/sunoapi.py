"""
Suno api for generating songs
"""

import requests
import time
from app_logging.logger import logger
from config.config import Settings

settings = Settings()


def generate_song_suno(
    song_prompt,
    style,
    title,
    negativeTags,
    vocalGender,
    styleWeight,
    weirdnessConstraint,
    audioWeight,
):

    suno_api_key = settings.suno.SUNO_API_KEY
    callback_url = settings.suno.SUNO_CALLBACK_URL

    payload = {
        "prompt": song_prompt,
        "style": style,  # leave empty if customMode is false
        "title": title,  # leave empty if customMode is false
        "customMode": True,  # Custom mode is true if you want to generate the lyrics yourself, you should set the lyrics in the prompt, if false, the lyrics will be generated automatically.
        "instrumental": False, #There should be no vocals in the song if its true
        "model": "V5",  # Available models: V3_5, V4, V4_5, V5
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
    logger.info(f"Initial generation request response: {response_json}")

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
                    logger.info(f"Current feed status: {feed_data}")

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
                            for i, item in enumerate(songs):
                                audio_url = item.get(
                                    "audioUrl"
                                )  # Corrected key from 'audio_url' to 'audioUrl'
                                title = item.get("title", "untitled_song")
                                if audio_url:
                                    logger.info(f"Downloading '{title}'...")
                                    audio_get_response = requests.get(audio_url)
                                    if audio_get_response.status_code == 200:
                                        filename = f"{title.replace(' ', '_')}_{i}.mp3"
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


if __name__ == "__main__":
    song_prompt = """
 (Brrr, yeah, yeah!)
It's A$AP Aspen, let's ride!
(Ice!)

[Verse 1]
Strapped in, top of the peak, I see the whole city sleepin'
Wind whispers secrets that the concrete's keepin'
Drop in, carve a clean line, leave the worries behind me
Edge to edge, a different kind of grind, see
Hit a kicker, backside one-eighty, vision gettin' hazy
This ain't for the lazy, this that mountain-top crazy
Feel the G-force pullin', ain't no time for slowin'
Every turn a new verse, yeah, the avalanche is growin'

[Chorus]
This that avalanche flow, watch the whole world go slow
White powder on the fit, yeah, from the alpine snow
Gravity's a myth when I'm lettin' it rip, yeah
In the moment, I'm alive, off the frozen cliff, I dip!
Yeah, that avalanche flow, can't nobody stop the glow
From the summit to the street, this the only life I know!

[Verse 2]
See the jump, approachin' fast, blurrin' out the past
A single perfect moment, yeah, a feeling built to last
Pop off the lip, Indy grab, hold it for the flash
Psychedelic swirl of white, a hundred-yard dash
Method air, so clean, board is lookin' mean
Livin' out a snowboard mag, a cinematic scene
This the freedom that I chase, at an unforgiving pace
Leavin' nothin' but a trace in this wide-open space.

[Outro]
Yeah... free...
Just me and the mountain...
Glydin'...
(Swoosh)
A$AP Aspen, gone.
    """
    generate_song_suno(
        song_prompt=song_prompt,
        style="Psychedelic Hip-Hop, Fast-paced Hip-Hop, Trap, Cloud Rap, Southern Hip-Hop, East Coast Hip-Hop, Alternative Hip-Hop, Pop Rap, R&B, Latin Trap, Energetic Hip-Hop",
        title="Freedom ride",
        negativeTags="Heavy Metal, Upbeat Drums",
        vocalGender="m",
        styleWeight=0.5,
        weirdnessConstraint=0.5,
        audioWeight=0.5,
    )