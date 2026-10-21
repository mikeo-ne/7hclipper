#!/usr/bin/env python3
"""Caption generator for 7hclipper - adds captions/subtitles to videos."""

import os
import subprocess
from typing import List, Dict, Optional


class CaptionGenerator:
    """Generate and burn captions onto videos."""

    def __init__(self, transcript: Optional[List[Dict]] = None):
        self.transcript = transcript or []
        self.srt_path: Optional[str] = None

    def generate_captions(self, video_path: str, output_dir: str = "output") -> str:
        """Burn captions onto the video using ffmpeg.

        Args:
            video_path: Path to the video to add captions to
            output_dir: Output directory for the final video

        Returns:
            Path to the video with burnt-in captions
        """
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_captions.mp4")

        # Generate SRT from transcript if not already done
        if not self.srt_path:
            self.srt_path = self._generate_srt()

        if not self.srt_path or not os.path.exists(self.srt_path):
            print("   No SRT file available - generating captions without text")
            self._burn_simple_captions(video_path, output_path)
            return output_path

        try:
            # Use ffmpeg to burn in subtitles
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=f"subtitles={self.srt_path}",
                    c="copy"
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"   ✅ Captions burned in: {output_path}")
            return output_path

        except Exception as e:
            print(f"   FFmpeg subtitle error: {e}")
            self._burn_simple_captions(video_path, output_path)
            return output_path

    def _generate_srt(self) -> Optional[str]:
        """Generate an SRT file from the transcript data."""
        if not self.transcript:
            return None

        srt_path = "/tmp/7hclipper_captions.srt"

        lines = []
        for i, seg in enumerate(self.transcript, 1):
            start_time = self._seconds_to_srt_timecode(seg['start'])
            end_time = self._seconds_to_srt_timecode(seg['end'])
            text = seg['text'].replace('\n', ' ')

            lines.append(f"{i}")
            lines.append(f"{start_time} --> {end_time}")
            lines.append(text)
            lines.append("")  # blank line

        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        self.srt_path = srt_path
        print(f"   Generated SRT with {len(self.transcript)} segments")
        return srt_path

    @staticmethod
    def _seconds_to_srt_timecode(seconds: float) -> str:
        """Convert seconds to SRT timecode format (HH:MM:SS,mmm)."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

    def _burn_simple_captions(self, video_path: str, output_path: str):
        """Burn simple placeholder captions onto video."""
        # Create a simple SRT with a single caption
        srt_path = "/tmp/simple_captions.srt"
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write("1\n")
            f.write("00:00:00,000 --> 00:00:10,000\n")
            f.write("7hclipper - AI powered video clipping\n")
            f.write("\n")

        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, vf=f"subtitles={srt_path}")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"   ✅ Simple captions added: {output_path}")
        except Exception as e:
            print(f"   Simple caption error: {e}")

        # cleanup
        if os.path.exists(srt_path):
            os.remove(srt_path)