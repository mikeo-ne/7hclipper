"""Vercel serverless function handler for 7hclipper.

Allows deploying 7hclipper as a Vercel serverless function.
"""

import json
import os
import sys
import tempfile
import logging
import base64
import shutil

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
        
        # Initialize YouTube handler
        yt = YouTubeHandler(url)
        
        # Extract transcript
        transcript_extractor = TranscriptExtractor(yt)
        transcript = transcript_extractor.get_full_transcript()
        
        if not transcript.strip():
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No transcript available for this video'})
            }
        
        # Identify best moments
        clipper = VideoClipper(transcript, model=model)
        best_moments = clipper.identify_best_moments()
        
        if not best_moments:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No best moments identified'})
            }
        
        # Create output directory
        output_dir = tempfile.mkdtemp()
        
        try:
            # Clip to vertical video
            video_clipper = VideoClipper(transcript, model=model)
            video_path = video_clipper.clip_to_vertical(
                best_moments, output_dir, aspect
            )
            
            # Generate captions
            captioner = CaptionGenerator(transcript)
            caption_path = captioner.generate_captions(video_path)
            
            # Read the output files
            video_data = None
            caption_data = None
            
            if os.path.exists(video_path):
                with open(video_path, 'rb') as f:
                    video_data = f.read()
            
            if os.path.exists(caption_path):
                with open(caption_path, 'rb') as f:
                    caption_data = f.read()
            
            # Clean up temp files
            shutil.rmtree(output_dir, ignore_errors=True)
            
            # Build response
            response = {
                'message': 'Video processed successfully' if video_data else 'Video processed with limitations'
            }
            
            # If files exist and are reasonable size, include base64
            if video_data and len(video_data) < 5 * 1024 * 1024:  # < 5MB
                response['video_base64'] = base64.b64encode(video_data).decode('utf-8')
                response['video_filename'] = 'vertical_clip.mp4'
            
            if caption_data and len(caption_data) < 1 * 1024 * 1024:  # < 1MB
                response['caption_base64'] = base64.b64encode(caption_data).decode('utf-8')
                response['caption_filename'] = 'captions.srt'
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response)
            }
            
        except Exception as e:
            logger.error(f"Error during video processing: {str(e)}", exc_info=True)
            # Clean up on error
            shutil.rmtree(output_dir, ignore_errors=True)
            raise
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }