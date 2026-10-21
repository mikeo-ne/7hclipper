"""Vercel serverless function handler for 7hclipper.

Allows deploying 7hclipper as a Vercel serverless function.
Provides transcript analysis and moment identification (works without FFmpeg).
Full video processing (clipping + caption burning) requires FFmpeg installed on the server.

Expected POST body:
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "duration": 60,
    "aspect": "9:16",
    "model": "claude"
}
"""

import json
import os
import sys
import tempfile
import logging

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from py7hclipper.youtube import YouTubeHandler
from py7hclipper.transcript import TranscriptExtractor
from py7hclipper.clipper import VideoClipper
from py7hclipper.captioner import CaptionGenerator

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Vercel serverless handler for 7hclipper.
    
    Expected POST body:
    {
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "duration": 60,
        "aspect": "9:16",
        "model": "claude"
    }
    """
    
    try:
        # Parse request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            body = {}
        
        url = body.get('url', '')
        duration = float(body.get('duration', 60))
        aspect = body.get('aspect', '9:16')
        model = body.get('model', 'claude')
        
        if not url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'URL is required'})
            }
        
        logger.info(f"Processing URL: {url}")
        logger.info(f"Duration: {duration}, Aspect: {aspect}, Model: {model}")
        
        # Initialize YouTube handler (just validates URL)
        yt = YouTubeHandler(url)
        
        # Extract transcript
        transcript_extractor = TranscriptExtractor(yt)
        transcript = transcript_extractor.get_full_transcript()
        
        if not transcript.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No transcript available for this video'})
            }
        
        # Identify best moments (text analysis only - no FFmpeg needed)
        clipper = VideoClipper(transcript, model=model)
        best_moments = clipper.identify_best_moments()
        
        if not best_moments:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No best moments identified'})
            }
        
        # Prepare analysis response - this part works without FFmpeg
        moments_data = []
        for moment in best_moments:
            moments_data.append({
                'start': moment['start'],
                'end': moment['end'],
                'duration': moment['end'] - moment['start'],
                'text': moment['text'][:100] + '...' if len(moment['text']) > 100 else moment['text'],
            })
        
        response = {
            'url': url,
            'video_title': getattr(yt, 'title', 'Unknown'),
            'transcript_length': len(transcript),
            'model_used': model,
            'best_moments': moments_data,
            'analysis_summary': {
                'total_segments_analyzed': len(best_moments),
                'duration_analyzed': duration,
                'aspect_ratio': aspect,
                'note': 'Full video clipping requires FFmpeg. Use 7hclipper CLI locally or deploy to an environment with FFmpeg.'
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }