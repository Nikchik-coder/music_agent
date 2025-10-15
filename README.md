# Xyber Radio - Dynamic YouTube Streaming System

A sophisticated automation tool for creating dynamic, schedule-driven YouTube live streams with real-time content management, audio generation, and seamless OBS integration.

## ✨ Features

- **Dynamic Scheduling**: Control the entire broadcast flow using a `schedule.json` file. Change scenes, videos, and audio on-the-fly.
- **YouTube API Integration**: Automatically creates YouTube live broadcasts, sets titles, and manages stream keys.
- **OBS Automation**: Connects to OBS via WebSockets to switch scenes, control media sources, manage transitions, and start/stop streaming.
- **Continuous Background Music**: Plays background music with automatic "ducking" when a scene with its own audio is playing.
- **Audio Generation**: Multiple audio generation services (ElevenLabs, Cartesia) for dynamic content.
- **YouTube Chat Integration**: Interactive chat responder for audience engagement.
- **News Aggregation**: Automated news gathering and script writing.
- **Live Content Updates**: Update the current scene during a broadcast by simply editing the schedule file.

## 📋 Prerequisites

- **Python 3.12+**
- **OBS Studio** with WebSocket plugin enabled
- **Google Cloud Project** with YouTube Data API v3 enabled
- **Windows 10/11** (PowerShell support)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd xyber_radio
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
py -m venv venv

# Activate virtual environment (PowerShell)
venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Docker Installation (Alternative)

```bash
# Build and run using Docker Compose
docker-compose up -d

# For development with volume mounts
docker-compose -f docker-compose.debug.yml up -d
```

## ⚙️ Configuration

### 1. OBS WebSocket

1. In OBS, go to `Tools` -> `WebSocket Server Settings`.
2. Enable the WebSocket server.
3. Set a `Server Password`.
4. Create a `.env` file in the project root and add your OBS credentials:

```env
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_obs_websocket_password
```

### 2. YouTube API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to your project, then to `APIs & Services` -> `Credentials`.
3. Create an `OAuth 2.0 Client ID` for a **Desktop app**.
4. Download the JSON file and rename it to `client_secrets.json`.
5. Place `client_secrets.json` inside the `main/src/` directory.

### 3. Schedule Configuration

Create or edit `schedule.json` in the project root:

```json
{
  "current_scene": {
    "scene_name": "Scene-News",
    "video_path": "video/action_talking.mp4",
    "audio_path": "ellevenlabs_audio/generated_audio/audio_20250718_113258.mp3",
    "has_audio": true
  },
  "background_music": {
    "enabled": true,
    "file_path": "music/king-gizzard-and-the-lizard-wizard-raw-feel.wav"
  },
  "_available_scenes": {
    "talking": {
      "scene_name": "Scene-Talking",
      "video_path": "video/action_talking.mp4",
      "audio_path": "ellevenlabs_audio/generated_audio/audio_20250718_113258.mp3",
      "has_audio": true
    },
    "news": {
      "scene_name": "Scene-News",
      "video_path": "video/news_anchor.mp4",
      "audio_path": "cartesia_audio/generated_audio/audio_20250717_171633.wav",
      "has_audio": true
    }
  }
}
```

### 4. API Keys (Optional)

Add additional API keys to your `.env` file:

```env
ELEVENLABS_API_KEY=your_elevenlabs_key
CARTESIA_API_KEY=your_cartesia_key
GOOGLE_API_KEY=your_google_api_key
```

## 🎮 Usage

### Running the Full YouTube Stream

This is the main entry point. It will authenticate with YouTube, create a new broadcast, and start streaming your scheduled content.

```bash
python main/src/run_stream.py
```

On the first run, you will be prompted to authenticate with Google via your web browser.

### Running the Local Prototype

Use this script for testing your scene logic and OBS integration without involving the YouTube API.

```bash
python main/src/stream_example.py
```

### Audio Generation Tools

**ElevenLabs Audio:**
```bash
python ellevenlabs_audio/ellevenlabs.py
```

**Cartesia Audio:**
```bash
python cartesia_audio/src/autio_generation.py
```

### News Aggregation
```bash
python researcher/src/news_agregator.py
python researcher/src/script_writer.py
```

### Changing the Scene Live

While a stream is running, you can execute this script in a separate terminal to instantly change the scene:

```bash
python main/src/change_scene_example.py
```

## 📁 Project Structure

```
xyber_radio/
├── main/                          # Core streaming functionality
│   ├── src/
│   │   ├── run_stream.py          # Main YouTube streaming script
│   │   ├── stream_example.py      # Local prototyping script
│   │   ├── obs_functions.py       # OBS integration functions
│   │   ├── change_scene_example.py# Live scene change utility
│   │   └── client_secrets.json    # Google API credentials
├── youtube_interface/             # YouTube chat interaction
├── cartesia_audio/                # Cartesia audio generation
├── ellevenlabs_audio/             # ElevenLabs audio generation
├── researcher/                    # News aggregation and script writing
├── music/                         # Music generation and files
├── video/                         # Video assets
├── config/                        # Configuration files
├── utils/                         # Utility functions
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata and dependencies
├── docker-compose.yml             # Production Docker configuration
├── docker-compose.debug.yml       # Development Docker configuration
└── schedule.json                  # Current scene schedule
```

## 🎵 Background Music System

The background music system operates independently from scene changes:

- **Normal Volume**: Default volume when scene has no audio
- **Ducked Volume**: Reduced volume when scene has audio content
- **Continuous Playback**: Music never stops, only volume changes
- **Configuration**: Set in `schedule.json` under `background_music`

## 🔄 Dynamic Scene Management

- Edit `schedule.json` while the script is running
- Changes are detected automatically via file watcher
- Smooth fade transitions between scenes
- Each scene can have:
  - Video content
  - Audio content (optional)
  - Audio flag for background music ducking

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're running from project root with activated venv
2. **OBS Connection Failed**: Check OBS WebSocket settings and ensure OBS is running
3. **Audio Generation Errors**: Verify API keys in `.env` file
4. **File Not Found**: Check paths in `schedule.json` are relative to project root
5. **YouTube Authentication Errors**: Verify client_secrets.json is properly configured

### Debug Mode

For detailed logging, modify the script to include debug information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Add your changes
3. Test thoroughly
4. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use Python 3.12+ syntax features
- Add type hints to all functions
- Handle exceptions gracefully

## 📞 Support

For issues and questions:

1. Check existing issues in the repository
2. Review troubleshooting section
3. Create new issue with detailed description

## 📄 License

[Add your license information here]

---

**Happy Streaming! 🎬🎵**


# TODO: 

- [youtube_interface](youtube_interface) – This library or service contains two separate entities. The LLM feature should likely be extracted into a separate essence, such as a library. The YouTube library should then be integrated with this LLM library in the chat service located at radio/services/chat_service.py.

- All modules used as libraries in the main radio framework folder probably should be gathered into a common folder in the project root, as there appear to be many of them.