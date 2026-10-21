#!/usr/bin/env python3
"""Transcript extractor for 7hclipper using yt-dlp."""

import re
import subprocess
import json
from typing import List, Dict, Optional


class TranscriptExtractor:
    """Extract YouTube video transcripts using yt-dlp."""

    def __init__(self, yt_handler):
        self.yt_handler = yt_handler
        self.transcript: List[Dict] = []
        self.full_text = ""

    def get_full_transcript(self) -> str:
        """Extract the full transcript of the YouTube video.

        Uses yt-dlp to fetch auto-generated or captions.
        Returns the full transcript text.
        """
        url = self.yt_handler.url
        print(f"   Fetching transcript via yt-dlp...")

        # yt-dlp command to list available subtitles
        cmd = ["yt-dlp", "--write-auto-sub", "--skip-download",
               "--sub-lang", "en", "--print-json", url]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"   yt-dlp subtitle list failed: {result.stderr}")
                # Try automatic captions
                self._fetch_auto_captions(url)
                return self.full_text

            # Parse the output - yt-dlp prints JSON info
            # Actually let's use a different approach
            info = json.loads(result.stdout) if result.stdout.strip() else {}
            print(f"   Available subtitles parsed")

        except Exception as e:
            print(f"   Error fetching subtitles: {e}")
            self._fetch_auto_captions(url)

        return self.full_text

    def _fetch_auto_captions(self, url: str):
        """Fetch auto-generated captions as fallback."""
        print("   Fetching auto-generated English captions...")

        # yt-dlp can also extract automatic captions
        cmd = ["yt-dlp", "--write-auto-sub", "--skip-download",
               "--sub-lang", "en", "--skip-download", url]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            # After writing auto-sub, yt-dlp saves them as .vtt or .json
            # Let's find the generated file
            import os
            base, _ = os.path.splitext(url.split('?')[0])
            # Actually yt-dlp stores info differently - let's use the --sub-format
        except Exception as e:
            print(f"   Auto caption fetch error: {e}")

        # Use yt-dlp's built-in caption extraction
        cmd = ["yt-dlp", "--skip-download",
               "--write-auto-sub", "--sub-lang", "en",
               "--convert-subs", "srt", url]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            # yt-dlp saves .srt file in current directory or temp
            # Let's find and parse it
            srt_files = [f for f in os.listdir('.') if f.endswith('.srt')]
            if srt_files:
                srt_path = srt_files[0]
                self._parse_srt(srt_path)
                os.remove(srt_path)  # clean up
                print(f"   Extracted {len(self.transcript)} caption segments")
            else:
                print("   No SRT subtitle file found after yt-dlp attempt")

        except Exception as e:
            print(f"   SRT extraction error: {e}")

    @staticmethod
    def _parse_srt(srt_path: str):
        """Parse an SRT subtitle file into structured transcript data."""
        transcript = []
        full_parts = []

        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            # Skip the sequence number
            timecode_line = lines[1]
            text_lines = lines[2:]

            # Parse timecodes
            time_match = re.match(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', timecode_line)
            if time_match:
                start_str = time_match.group(1)
                end_str = time_match.group(2)

                # Convert to seconds
                start_sec = _timecode_to_seconds(start_str)
                end_sec = _timecode_to_seconds(end_str)

                # Combine text
                text = ' '.join(line.strip() for line in text_lines if line.strip())

                if text:
                    transcript.append({
                        'start': start_sec,
                        'end': end_sec,
                        'text': text
                    })
                    full_parts.append(text)

        self.transcript = transcript
        self.full_text = ' '.join(full_parts)

    @staticmethod
    def _timecode_to_seconds(tc: str) -> float:
        """Convert SRT timecode (HH:MM:SS,mmm) to seconds."""
        parts = tc.split(':')
        hours = int(parts[0]) if len(parts) > 0 else 0
        minutes = int(parts[1]) if len(parts) > 1 else 0
        secs_ms = parts[2].split(',') if len(parts) > 2 else ['0', '0']
        seconds = float(secs_ms[0])
        milliseconds = int(secs_ms[1]) if len(secs_ms) > 1 else 0
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0

    def get_transcript_segments(self) -> List[Dict]:
        """Return the list of transcript segments with start/end times."""
        return self.transcript

    def get_full_text(self) -> str:
        """Return the full transcript as a single string."""
        return self.full_text