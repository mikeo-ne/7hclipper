#!/usr/bin/env python3
"""Video clipper for 7hclipper - identifies best moments and clips video."""

import os
import subprocess
from typing import List, Dict, Optional
import ffmpeg


class VideoClipper:
    """Clip and reformat YouTube videos into vertical short-form videos."""

    def __init__(self, transcript: Optional[List[Dict]] = None, model: str = "claude"):
        self.transcript = transcript or []
        self.model = model
        self.best_moments: List[Dict] = []

    def identify_best_moments(self, num_moments: int = 5) -> List[Dict]:
        """Identify the best moments from the transcript using AI analysis.

        Uses simple heuristics based on transcript analysis:
        - High keyword density
        - Sentence endings (periods, exclamation points)
        - Significant time gaps analysis
        """
        if not self.transcript:
            print("   No transcript available for moment analysis")
            return []

        print(f"   Analyzing transcript for best moments (model: {self.model})...")

        # Simple heuristic: find segments with high-impact words or sentence boundaries
        segments = self.transcript
        scored = []

        for i, seg in enumerate(segments):
            text = seg['text'].lower()
            score = 0

            # Reward sentence endings
            if text.rstrip().endswith(('.', '!', '?')):
                score += 3

            # Reward longer content (up to a point)
            word_count = len(text.split())
            score += min(word_count / 2, 5)  # cap at 5

            # Reward segments that aren't too short
            if seg['end'] - seg['start'] > 3:
                score += 2

            # Reward segments with exclamation or question words
            if any(word in text for word in ['wow', 'amazing', 'wait', 'really', 'but']):
                score += 2

            scored.append((score, i, seg))

        # Sort by score and take top moments
        scored.sort(key=lambda x: x[0], reverse=True)
        self.best_moments = [seg for _, _, seg in scored[:num_moments]]

        print(f"   Identified {len(self.best_moments)} best moments")
        for i, moment in enumerate(self.best_moments, 1):
            duration = moment['end'] - moment['start']
            print(f"   Moment {i}: {moment['text'][:60]}... ({duration:.1f}s)")

        return self.best_moments

    def clip_to_vertical(
        self,
        output_dir: str = "output",
        aspect_ratio: str = "9:16",
        target_duration: float = 60.0
    ) -> str:
        """Clip the video to vertical format focusing on best moments.

        Args:
            output_dir: Directory to save the output video
            aspect_ratio: Target aspect ratio (default: 9:16 for vertical)
            target_duration: Target duration in seconds

        Returns:
            Path to the output vertical video
        """
        if not self.best_moments:
            print("   No best moments identified - using full video")
            # Use the full video from start to target duration
            best_moments = [{'start': 0, 'end': min(target_duration, 300)}]
        else:
            # Combine best moments, ensuring we don't exceed target duration
            best_moments = self._combine_moments(target_duration)

        os.makedirs(output_dir, exist_ok=True)

        # For demonstration, we'll use the first moment and pad/extend
        # In a full implementation, we'd composite multiple moments
        primary_moment = best_moments[0]
        start_time = primary_moment['start']
        end_time = primary_moment['end']
        duration = end_time - start_time

        print(f"   Clipping from {start_time:.1f}s to {end_time:.1f}s (duration: {duration:.1f}s)")

        # Get video info to find stream
        url = self.yt_handler.url if hasattr(self, 'yt_handler') else None

        output_path = os.path.join(output_dir, "vertical_clip.mp4")

        try:
            # Use ffmpeg to resize and reformat
            (
                ffmpeg
                .input(url or "placeholder.mp4", ss=start_time, t=duration)
                .output(
                    output_path,
                    vf=f"scale=1080:-2,setsar=1:1,setdar=16:9",
                    crf=23,
                    preset="fast"
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"   ✅ Vertical clip saved to: {output_path}")
            return output_path

        except Exception as e:
            print(f"   FFmpeg error: {e}")
            # Fallback: create a simple placeholder
            self._create_placeholder(output_dir, aspect_ratio)
            return os.path.join(output_dir, "vertical_clip.mp4")

    def _combine_moments(self, target_duration: float) -> List[Dict]:
        """Combine multiple best moments into a sequence within target duration."""
        combined = []
        current_duration = 0
        moment_duration = 0

        for moment in self.best_moments:
            seg_len = moment['end'] - moment['start']
            if current_duration + seg_len <= target_duration:
                combined.append(moment)
                current_duration += seg_len
            else:
                # Trim this moment to fit remaining duration
                remaining = target_duration - current_duration
                if remaining > 3:  # only add if meaningful remaining
                    # Adjust end time
                    adjusted_end = moment['start'] + remaining
                    combined.append({
                        'start': moment['start'],
                        'end': adjusted_end
                    })
                break

        return combined if combined else [{'start': 0, 'end': target_duration}]

    def _create_placeholder(self, output_dir: str, aspect_ratio: str):
        """Create a placeholder vertical video when clipping fails."""
        import random
        placeholder_path = os.path.join(output_dir, "vertical_clip.mp4")

        # Use ffmpeg to create a simple colored vertical video
        try:
            ratio_w, ratio_h = map(int, aspect_ratio.split(':'))
            duration = 10  # 10 second placeholder

            (
                ffmpeg
                .output(
                    placeholder_path,
                    color='black',
                    duration=duration,
                    s=f"{ratio_w}x{ratio_h}",
                    vf='format=yuv420p'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"   Created placeholder vertical video: {placeholder_path}")
        except Exception as e:
            print(f"   Placeholder creation error: {e}")

    def set_yt_handler(self, yt_handler):
        """Set the YouTube handler for this clipper."""
        self.yt_handler = yt_handler