"""7hclipper - AI-powered YouTube video clipping and lyric video generation."""

__version__ = "0.1.0"

from .youtube import YouTubeHandler
from .transcript import TranscriptExtractor
from .clipper import VideoClipper
from .captioner import CaptionGenerator

print("🎵 7hclipper loaded successfully")
print("   Features: YouTube fetching, transcript extraction, moment clipping, vertical video generation with captions")