import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from django.shortcuts import render
from django.conf import settings
from pydub import AudioSegment

def index(request):
    """Renders the main page with the URL input form."""
    return render(request, 'index.html')

def extract_video_id(url):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def download_audio(video_id, temp_dir):
    """Downloads audio for a single video_id and returns the path."""
    output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
    final_mp3_path = os.path.join(temp_dir, f"{video_id}.mp3")
    
    try:
        print("Testing yt-dlp directly...")
        command = [
            'yt-dlp', '--extract-audio', '--audio-format', 'mp3',
            '--audio-quality', '0', '-o', output_template,
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        return final_mp3_path if os.path.exists(final_mp3_path) else None
    except Exception as e:
        print(f"Error downloading {video_id}: {e}")
        return None


def create_jukebox_view(request):
    """
    Handles the form submission, creates the jukebox, and provides a download link.
    """
    if request.method != 'POST':
        return render(request, 'index.html', {'error': 'Invalid request method.'})

    urls_text = request.POST.get('urls')
    if not urls_text:
        return render(request, 'index.html', {'error': 'Please provide at least one YouTube URL.'})

    video_urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
    
    # Create a unique directory for this request to handle simultaneous users
    session_id = str(uuid.uuid4())
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', session_id)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'jukeboxes')
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Note: For a real-world app, this downloading loop should be handled
    # by a background task queue like Celery to avoid long request times.
    mp3_paths = []
    for url in video_urls:
        video_id = extract_video_id(url)
        if video_id:
            path = download_audio(video_id, temp_dir)
            if path:
                mp3_paths.append(path)

    if not mp3_paths:
        shutil.rmtree(temp_dir) # Clean up
        return render(request, 'index.html', {'error': 'Could not download audio for any of the provided URLs.'})

    # Combine audio files
    combined_audio = AudioSegment.empty()
    for path in mp3_paths:
        try:
            combined_audio += AudioSegment.from_mp3(path)
        except Exception as e:
            print(f"Could not process {path}: {e}")
    
    # Export final file
    output_filename = f"jukebox_{session_id}.mp3"
    final_output_path = os.path.join(output_dir, output_filename)
    combined_audio.export(final_output_path, format="mp3")

    # Clean up temporary files
    shutil.rmtree(temp_dir)

    download_url = os.path.join(settings.MEDIA_URL, 'jukeboxes', output_filename)
    
    context = {
        'success': True,
        'download_url': download_url,
        'filename': output_filename,
    }
    return render(request, 'success.html', context)
