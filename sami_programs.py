import subprocess
from pathlib import Path
import json
import re

def get_subtitle_info(video_file):
    """Get subtitle track information from video file using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        str(video_file)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error analyzing {video_file}: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        # Find subtitle streams
        subtitle_streams = [
            stream for stream in data['streams']
            if stream['codec_type'] == 'subtitle'
        ]
        return subtitle_streams
    except Exception as e:
        print(f"Error processing {video_file}: {str(e)}")
        return None

def extract_subtitles(input_dir, output_dir=None):
    """Extract subtitles from all video files in the input directory."""
    input_path = Path(input_dir)
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path / 'extracted_subtitles'

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Get all video files
    video_files = list(input_path.glob('*.mp4')) + list(input_path.glob('*.mkv'))
    total_files = len(video_files)

    print(f"Found {total_files} video files")

    # Process each file
    for index, video_file in enumerate(video_files, 1):
        print(f"\nProcessing file {index}/{total_files}: {video_file.name}")

        # Get subtitle information
        subtitle_streams = get_subtitle_info(video_file)
        if not subtitle_streams:
            print(f"No subtitle streams found in {video_file.name}")
            continue

        # Create base filename without extension
        base_name = video_file.stem

        # Extract each subtitle stream
        for stream in subtitle_streams:
            stream_index = stream['index']

            # Create output filename
            output_file = output_path / f"{base_name}.srt"

            # Extract subtitles using ffmpeg with subtitle transcoding
            cmd = [
                'ffmpeg',
                '-i', str(video_file),
                '-map', f'0:{stream_index}',
                '-f', 'srt',  # Force SRT format output
                str(output_file)
            ]

            try:
                print(f"Extracting subtitles to: {output_file.name}")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"Successfully extracted subtitles from stream {stream_index}")
                else:
                    print(f"Error extracting subtitles: {result.stderr}")

            except Exception as e:
                print(f"Error processing subtitle extraction: {str(e)}")

def main():
    # Get the directory containing the script
    script_dir = Path(__file__).parent

    # Ask for input directory if not the same as script directory
    while True:
        print("\nCurrent directory:", script_dir)
        use_current = input("Use current directory for video files? (y/n): ").lower()

        if use_current == 'y':
            input_dir = script_dir
            break
        elif use_current == 'n':
            input_dir = input("Enter the full path to the directory containing video files: ")
            if Path(input_dir).exists():
                break
            else:
                print("Directory does not exist. Please try again.")

    # Ask for output directory
    use_default = input("Create 'extracted_subtitles' folder in the same directory? (y/n): ").lower()
    if use_default == 'y':
        output_dir = None
    else:
        output_dir = input("Enter the full path for output directory: ")

    # Extract subtitles
    extract_subtitles(input_dir, output_dir)

    print("\nExtraction complete!")

if __name__ == "__main__":
    main()
