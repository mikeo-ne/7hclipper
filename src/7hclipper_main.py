#!/usr/bin/env python3
"""7hclipper - AI-powered YouTube video clipping and lyric video generation.

This tool clips the best moments from YouTube videos and generates
vertical short-form videos with captions and lyric transcripts.
"""

__version__ = "0.1.0"
__author__ = "7hclipper"

import sys
import argparse
from .youtube import YouTubeHandler
from .transcript import TranscriptExtractor
from .clipper import VideoClipper
from .captioner import CaptionGenerator


def main():
    parser = argparse.ArgumentParser(
        description="7hclipper: Clip YouTube videos and generate lyric videos"
    )
    parser.add_argument(
        "url", help="YouTube video URL to process"
    )
    parser.add_argument(
        "--output", "-o", default="output",
        help="Output directory for clipped videos (default: output)"
    )
    parser.add_argument(
        "--duration", "-d", type=float, default=60.0,
        help="Target clip duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--aspect", default="9:16",
        help="Output video aspect ratio (default: 9:16 for vertical)"
    )
    parser.add_argument(
        "--model", choices=["claude", "gemini", "gpt"],
        default="claude",
        help="AI model for transcript/lyrics generation (default: claude)"
    )
    args = parser.parse_args()

    print(f"🚀 7hclipper v{__version__}")
    print(f"Processing: {args.url}")
    print(f"Target duration: {args.duration}s")
    print(f"Output aspect: {args.aspect}")

    # Initialize components
    yt = YouTubeHandler(args.url)
    print("📥 Fetching video info...")

    # Extract transcript
    print("📝 Extracting transcript...")
    transcript_extractor = TranscriptExtractor(yt)
    transcript = transcript_extractor.get_full_transcript()

    # Identify best moments
    print("🤖 Analyzing best moments using AI...")
    clipper = VideoClipper(transcript, model=args.model)
    best_moments = clipper.identify_best_moments()

    # Clip and generate vertical video
    print("✂️ Clipping and reformatting to vertical...")
    video_clipper = VideoClipper(transcript, model=args.model)
    video_path = video_clipper.clip_to_vertical(
        best_moments, args.output, args.aspect
    )

    # Generate captions/lyrics
    print("💬 Generating captions...")
    captioner = CaptionGenerator(transcript)
    caption_path = captioner.generate_captions(video_path)

    print(f"\n✅ Done! Output: {video_path}")
    print(f"   Captions: {caption_path}")


if __name__ == "__main__":
    main()