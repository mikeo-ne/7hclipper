#!/usr/bin/env python3
"""YouTube video handler for 7hclipper."""

import re
from urllib.parse import parse_qs, urlparse

try:
    from pytube import YouTube
    from pytubefix import extract
except ImportError:
    YouTube = None


class YouTubeHandler:
    """Handle YouTube video URL parsing and metadata fetching."""

    def __init__(self, url: str):
        self.url = url
        self.video_id = self._extract_video_id(url)
        self.title = ""
        self.author = ""
        self.length = 0

    @staticmethod
    def _extract_video_id(url: str) -> str:
        """Extract video ID from various YouTube URL formats."""
        parsed = urlparse(url)
        if parsed.hostname in ('youtu.be', 'youtube.com', 'www.youtube.com'):
            if parsed.path:
                return parsed.path.lstrip('/').split('/')[0]
            query = parse_qs(parsed.query)
            return query.get('v', [None])[0]
        elif parsed.hostname == 'www.youtube.com' and 'v' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['v'][0]
        raise ValueError(f"Cannot extract video ID from URL: {url}")

    def fetch_metadata(self):
        """Fetch video metadata using pytube."""
        if YouTube is None:
            raise ImportError("pytube not installed. Run: pip install pytube")
        try:
            yt = YouTube(self.url)
            self.title = yt.title
            self.author = yt.author
            self.length = yt.length
            print(f"   Title: {self.title}")
            print(f"   Channel: {self.author}")
            print(f"   Length: {self.length} seconds")
        except Exception as e:
            print(f"Warning: pytube fetch failed: {e}")
            # Fallback: just use URL parsing
        return self