import re
from pathlib import Path

def clean_subtitle_text(text):
    """Clean subtitle text by removing HTML tags and normalizing whitespace."""
    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)
    # Replace multiple spaces and newlines with single space
    text = ' '.join(text.split())
    return text.strip()

def process_srt_file(file_path):
    """Extract text content from SRT file, returning list of cleaned subtitle texts."""
    subtitle_texts = []
    current_text = []
    in_subtitle_text = False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and numeric identifiers
                if not line:
                    if current_text:  # End of a subtitle block
                        text = clean_subtitle_text(' '.join(current_text))
                        if text:  # Only add non-empty texts
                            subtitle_texts.append(text)
                        current_text = []
                    in_subtitle_text = False
                    continue

                # Skip timestamp lines
                if '-->' in line:
                    in_subtitle_text = True
                    continue

                # Skip numeric identifiers (usually just a number)
                if line.isdigit():
                    continue

                # If we're in the text part of a subtitle, add the line
                if in_subtitle_text:
                    current_text.append(line)

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

    # Add the last subtitle if there is one
    if current_text:
        text = clean_subtitle_text(' '.join(current_text))
        if text:
            subtitle_texts.append(text)

    return subtitle_texts

def process_srt_directory(input_dir, output_file):
    """Process all SRT files in directory and combine into single output file."""
    input_path = Path(input_dir)
    srt_files = list(input_path.glob('*.srt'))

    if not srt_files:
        print("No SRT files found in the directory!")
        return

    print(f"Found {len(srt_files)} SRT files")
    all_subtitles = []

    # Process each SRT file
    for srt_file in srt_files:
        print(f"Processing: {srt_file.name}")
        subtitles = process_srt_file(srt_file)
        all_subtitles.extend(subtitles)

    # Remove duplicates while preserving order
    seen = set()
    unique_subtitles = [x for x in all_subtitles if not (x in seen or seen.add(x))]

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for subtitle in unique_subtitles:
            if subtitle:  # Extra check to ensure no empty lines
                f.write(subtitle + '\n')

    print(f"\nProcessing complete!")
    print(f"Total subtitles extracted: {len(unique_subtitles)}")
    print(f"Output written to: {output_file}")

def main():
    # Get the directory containing the script
    script_dir = Path(__file__).parent

    # Ask for input directory
    while True:
        print("\nCurrent directory:", script_dir)
        use_current = input("Are the SRT files in the current directory? (y/n): ").lower()

        if use_current == 'y':
            input_dir = script_dir
            break
        elif use_current == 'n':
            input_dir = input("Enter the full path to the directory containing SRT files: ")
            if Path(input_dir).exists():
                break
            else:
                print("Directory does not exist. Please try again.")

    # Set output file path
    output_file = Path(input_dir) / "combined_subtitles.txt"

    # Process the files
    process_srt_directory(input_dir, output_file)

if __name__ == "__main__":
    main()
