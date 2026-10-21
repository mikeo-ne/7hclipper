# 7hclipper

AI-powered YouTube video clipping and lyric video generation tool.

## Features

- **YouTube video fetching** - Extract metadata and transcripts from YouTube videos
- **Best moment analysis** - AI-powered identification of the most engaging video segments
- **Vertical video clipping** - Auto-reformat to 9:16 aspect ratio for TikTok/Reels/Shorts
- **Automatic captions** - Burn-in subtitles from video transcript
- **Multiple AI model support** - Choose between Claude, Gemini, or GPT for analysis

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd 7hclipper

# Install dependencies
pip install -r requirements.txt

# Ensure ffmpeg is installed on your system
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

## Usage

```bash
python -m sevenhclipper <youtube-url> [options]
```

### Arguments

- `youtube-url` - The YouTube video URL to process
- `--output`, `-o` - Output directory (default: `output`)
- `--duration`, `-d` - Target clip duration in seconds (default: `60`)
- `--aspect` - Output aspect ratio (default: `9:16` for vertical)
- `--model` - AI model for analysis (`claude`, `gemini`, `gpt`, default: `claude`)

### Example

```bash
python -m sevenhclipper "https://www.youtube.com/watch?v=example" \
  --output my_clips \
  --duration 45 \
  --aspect 9:16 \
  --model claude
```

## Output

The tool generates:
- `output/vertical_clip.mp4` - Vertical reformatted video (9:16)
- `output/vertical_clip_captions.mp4` - Video with burnt-in captions

## Requirements

- Python 3.8+
- FFmpeg (system install)
- Python packages: `yt-dlp`, `ffmpeg-python`, `pytube`

## Roadmap

- [x] YouTube metadata and transcript extraction
- [x] Best moment identification using AI analysis
- [x] Vertical video reformatting (9:16)
- [x] Automatic caption generation
- [ ] Advanced AI moment scoring (semantic importance)
- [ ] Multi-moment compilation
- [ ] Lyrics extraction and synchronization
- [ ] Background music addition