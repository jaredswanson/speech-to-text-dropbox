# Speech-to-Text Dropbox

A simple utility that converts speech in audio files to text using OpenAI's Whisper model.

## Features

- Processes individual MP3 files or directories of MP3s
- Treats directories as audiobooks, combining all transcriptions into one file
- Moves processed files to a separate directory
- Can resume batch processing if interrupted
- Simple to use - just drop files in the "dropbox" directory and run the script

## Prerequisites

This script requires both Python dependencies and system dependencies:

1. **Python 3.x**

2. **FFmpeg**: Required for audio processing
   - On Ubuntu/Debian:
     ```
     sudo apt update && sudo apt install ffmpeg
     ```
   - On macOS (using Homebrew):
     ```
     brew install ffmpeg
     ```
   - On Windows:
     Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/speech-to-text-dropbox.git
   cd speech-to-text-dropbox
   ```

2. Install Whisper and dependencies:
   ```
   pip install torch ffmpeg-python
   pip install git+https://github.com/openai/whisper.git
   ```

   Note: For GPU acceleration (recommended for larger models):
   - Follow PyTorch's installation instructions for your specific CUDA version: https://pytorch.org/get-started/locally/

## Usage

1. Place MP3 files in the `dropbox` directory:
   - Individual files will be processed one by one
   - Directories of files will be treated as audiobooks and combined

2. Run the script:
   ```
   python speech_to_text.py
   ```

3. Find transcribed text in the `output` directory

### Optional Arguments

- `--model`: Choose Whisper model size (tiny, base, small, medium, large)
  ```
  python speech_to_text.py --model medium
  ```
  
  Model sizes trade-off accuracy for speed:
  - tiny: Fastest, least accurate
  - base: Good balance for most use cases
  - small: Better accuracy, slower
  - medium: High accuracy, significantly slower
  - large: Highest accuracy, very slow (recommended only with GPU)

- `--base-dir`: Specify a different base directory
  ```
  python speech_to_text.py --base-dir /path/to/directory
  ```

## Directory Structure

- `dropbox/` - Place audio files here for processing
- `output/` - Transcribed text files appear here
- `processed/` - Processed audio files are moved here

## Troubleshooting

- **"No module named 'whisper'"**: Make sure you installed Whisper using the git link above
- **FFmpeg errors**: Ensure FFmpeg is properly installed and accessible in your PATH
- **CUDA/GPU errors**: For GPU usage, make sure your PyTorch installation matches your CUDA version

## License

MIT
