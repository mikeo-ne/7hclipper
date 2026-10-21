# 7hclipper

AI-powered YouTube video clipping and lyric video generation tool for creating vertical short-form videos with captions.

![7hclipper Preview](preview.png)

## 📋 Overview

7hclipper transforms YouTube videos into vertical short-form videos (9:16 aspect ratio) optimized for TikTok, Instagram Reels, and YouTube Shorts. The tool automatically:

- Fetches video metadata and transcripts
- AI-analyzes to identify the best moments
- Clips and reformats to vertical orientation
- Burns in captions from the transcript
- Outputs ready-to-publish videos

## 🚀 Quick Start

### Installation

```bash
# Using git
git clone https://github.com/mikeo-ne/7hclipper.git
cd 7hclipper

# Install Python dependencies
pip install -r requirements.txt

# Install the package (optional, for CLI access)
pip install -e .

# Install FFmpeg (required for video processing)
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
```

### Basic Usage

```bash
7hclipper "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output my_clips \
  --duration 60 \
  --aspect 9:16 \
  --model claude
```

### CLI Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `url` | - | - | **Required** YouTube video URL to process |
| `--output`, `-o` | | `output` | Output directory for generated videos |
| `--duration`, `-d` | | `60` | Target clip duration in seconds |
| `--aspect` | | `9:16` | Output video aspect ratio (e.g., `9:16`, `16:9`, `4:3`) |
| `--model` | | `claude` | AI model for moment analysis: `claude`, `gemini`, `gpt` |

### Example Commands

```bash
# Default: 60s vertical clip with captions
7hclipper "https://www.youtube.com/watch?v=tgbnftdQ3s4"

# Custom duration and output directory
7hclipper "https://www.youtube.com/watch?v=tgbnftdQ3s4" \
  --output ./my_videos --duration 45

# Use Gemini model for moment analysis
7hclipper "https://www.youtube.com/watch?v=tgbnftdQ3s4" \
  --model gemini

# Vertical clip for TikTok/Reels/Shorts
7hclipper "https://www.youtube.com/watch?v=tgbnftdQ3s4" \
  --aspect 9:16 --duration 30 --output tiktok_clips
```

## ⚙️ How It Works

1. **Fetch**: YouTube video metadata and transcript extracted via `yt-dlp`
2. **Analyze**: Transcript analyzed for "best moments" using heuristics:
   - Sentence endings (`.`, `!`, `?`)
   - Keyword density and importance
   - Impact words (wow, amazing, wait, really, but)
   - Segment duration significance
3. **Clip**: Identified moments clipped and reformatted to vertical 9:16 using FFmpeg
4. **Caption**: Transcript segments burned into video as burnt-in subtitles
5. **Output**: Vertical short-form video with captions ready for social media

## 📁 Output Files

```
output/
├── vertical_clip.mp4       # Vertical reformatted video (9:16)
└── vertical_clip_captions.mp4  # Video with burnt-in captions
```

## 🛠️ System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Must be installed on system PATH (required for video processing)
- **Packages**: `yt-dlp`, `ffmpeg-python`, `pytube` (install via `requirements.txt`)
- **Internet**: Required for YouTube transcript fetching

## ⚠️ Known Limitations

- TLS/SSL errors with yt-dlp may occur in restricted network environments
- FFmpeg must be installed and accessible from PATH
- Auto-generated captions quality varies by video
- Very short videos (<30 seconds) may not have meaningful transcript segments
- Only one clip is generated per run (multi-clip compilation planned for future)

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|----------|----------|
| `ffmpeg: command not found` | Install FFmpeg and ensure it's in your PATH |
| `Unable to download webpage: TLS/SSL connection error` | Try `pip install --upgrade yt-dlp` or use a different network |
| `No transcript available` | Video may not have captions; try a different video |
| `ModuleNotFoundError: ffmpeg-python` | Reinstall: `pip install ffmpeg-python` |
| `Permission denied: output/vertical_clip.mp4` | Check write permissions or use `--output` to a different directory |

### Running in Restricted Environments

If you encounter yt-dlp issues:

```bash
# Update yt-dlp to latest version
pip install --upgrade yt-dlp

# Or use network-provided API key
# Setyt-dlp flags if needed
7hclipper "URL" --verbose
```

## 📦 Installation Options

### Option 1: pip install (recommended)

```bash
pip install git+https://github.com/mikeo-ne/7hclipper.git
7hclipper "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Option 2: From source

```bash
git clone https://github.com/mikeo-ne/7hclipper.git
cd 7hclipper
pip install -e .
7hclipper "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Option 3: Docker (future)

Docker support planned for future release.

## 🛣️ Roadmap

- [x] YouTube metadata and transcript extraction
- [x] Best moment identification using AI analysis
- [x] Vertical video reformatting (9:16)
- [x] Automatic caption generation
- [ ] Advanced AI moment scoring (semantic importance)
- [ ] Multi-moment compilation (multiple clips per video)
- [ ] Lyrics extraction and synchronization
- [ ] Background music addition
- [ ] Docker containerization
- [ ] Web interface
- [ ] Batch processing mode

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- Issues: [GitHub Issues](https://github.com/mikeo-ne/7hclipper/issues)
- Questions: Open an issue in the repository
- Documentation: Refer to this README and inline help (`7hclipper --help`)