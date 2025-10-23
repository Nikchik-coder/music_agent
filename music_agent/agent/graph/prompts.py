MUSIC_GENERATION_PROMPT = """
<context>
You are the ai agent for music generation with the following memory of the past songs and music style and
music personality and agent name.
You need to follow the music memory and music style and agent personality and agent name to generate the song prompt.
music memory: {music_memory}
music style: {music_style}
agent_personality: {agent_personality}
agent_name: {agent_name}
album_style: {album_style} #This is the style of the album and the inspiration for the album.
</context>

<goal>
You need to generate songs prompt with the following keys:
Please be creative and innovative and follow the music memory and music style and agent personality and agent name to generate the song prompt.
You should also generate songs lyrics based on the personality and style. This should be song promt.
</goal>

<Critical>
1. You should not mention the names of the real artists in the song prompt.
</Critical>     

<example>
{{  
    "song_name": "A creative and engaging name for the song",
    "song_prompt": "Song lyrics based on the personality and style",
    "title": "A creative and engaging title for the song",
    "style": "Psychedelic Hip-Hop, Fast-paced Hip-Hop, Trap, Cloud Rap, Southern Hip-Hop, East Coast Hip-Hop, Alternative Hip-Hop, Pop Rap, R&B, Latin Trap, Energetic Hip-Hop",
    "negativeTags": "Heavy Metal, Upbeat Drums", #Music styles or traits to exclude from the generated audio.
    "vocalGender": "m", #Available genders: m
    "styleWeight": 0.65, #Weight of the provided style guidance. Range 0.00–1.00.
    "weirdnessConstraint": 0.65, #Constraint on creative deviation/novelty. Range 0.00–1.00.
    "audioWeight": 0.65, #Weight of the input audio influence (where applicable). Range 0.00–1.00.
}}
</example>

<structure>
Please provide your response in a JSON format with the following keys:
{{
    "song_name": "A creative and engaging name for the song",
    "song_prompt": "Song lyrics based on the personality style",
    "title": "A creative and engaging title for the song",
    "style": "Psychedelic Hip-Hop, Fast-paced Hip-Hop, Trap, Cloud Rap, Southern Hip-Hop, East Coast Hip-Hop, Alternative Hip-Hop, Pop Rap, R&B, Latin Trap, Energetic Hip-Hop",
    "negativeTags": "Heavy Metal, Upbeat Drums", #Music styles or traits to exclude from the generated audio.
    "vocalGender": "m",
    "styleWeight": 0.65,
    "weirdnessConstraint": 0.65,
    "audioWeight": 0.65,
}}
</structure>
"""



MUSIC_VALIDATION_PROMPT = """
<context>
music memory: {music_memory}
music style: {music_style}
agent_personality: {agent_personality}
agent_name: {agent_name}
song_prompt: {song_prompt}
song_name: {song_name}
style: {style}
title: {title}
negativeTags: {negativeTags}
vocalGender: {vocalGender}
styleWeight: {styleWeight}
weirdnessConstraint: {weirdnessConstraint}
audioWeight: {audioWeight}
</context>

<goal>
You need to validate the song prompt.
The song prompt must should contain the songs lyrics.
The song prompt must have the following structure
{{
    "song_name": "A creative and engaging name for the song",
    "song_prompt": "Song lyrics based on the personality and style",
    "title": "A creative and engaging title for the song",
    "style": "Psychedelic Hip-Hop, Fast-paced Hip-Hop, Trap, Cloud Rap, Southern Hip-Hop, East Coast Hip-Hop, Alternative Hip-Hop, Pop Rap, R&B, Latin Trap, Energetic Hip-Hop",
    "negativeTags": "Heavy Metal, Upbeat Drums", #Music styles or traits to exclude from the generated audio.
    "vocalGender": "m",
    "styleWeight": 0.65,
    "weirdnessConstraint": 0.65,
    "audioWeight": 0.65,
}} 
</goal>

<structure>
The song prompt must be creative and do not repeat the prompts from music memory. It has to be in the style of the
music agent
<Critical>
1. There should be no mention of the names of the real artists in the song prompt.
</Critical>     

Please provide the Json with the following keys:
{{
    "song_prompt_validated": true,
    "recommendations": "Recommendations of how to improve the song prompt if song_prompt_validated is false, otherwise an empty string"
}}
</structure>
"""