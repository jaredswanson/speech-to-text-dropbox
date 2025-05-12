#!/usr/bin/env python3
"""
speech-to-text-dropbox

A script that processes MP3 files using OpenAI's Whisper model to convert speech to text.
"""

import os
import sys
import shutil
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("speech-to-text.log")
    ]
)
logger = logging.getLogger(__name__)

def setup_directories(base_dir="."):
    """Create necessary directories if they don't exist."""
    directories = {
        "dropbox": os.path.join(base_dir, "dropbox"),
        "output": os.path.join(base_dir, "output"),
        "processed": os.path.join(base_dir, "processed")
    }
    
    for name, path in directories.items():
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory {name} is ready at: {path}")
    
    return directories

def is_audio_file(filename):
    """Check if the file is an audio file (currently only MP3)."""
    audio_extensions = ['.mp3']
    return any(filename.lower().endswith(ext) for ext in audio_extensions)

def get_output_filename(input_path, output_dir):
    """Generate appropriate output filename for the text result."""
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]
    return os.path.join(output_dir, f"{base_name}.txt")

def process_audio_file(file_path, output_dir, model):
    """Process a single audio file using Whisper."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    output_path = get_output_filename(file_path, output_dir)
    
    # Check if already processed
    if os.path.exists(output_path):
        logger.info(f"File already processed: {file_path}")
        return True
    
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Transcribe audio using Whisper
        result = model.transcribe(file_path)
        
        # Write result to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        logger.info(f"Transcription saved to: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return False

def process_directory(dir_path, output_dir, processed_dir, model):
    """Process a directory of audio files (audiobook)."""
    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        return
    
    # Create a unique output file for the audiobook
    dir_name = os.path.basename(dir_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audiobook_output = os.path.join(output_dir, f"{dir_name}_{timestamp}.txt")
    
    # Get all audio files in the directory
    audio_files = [
        os.path.join(dir_path, f) for f in sorted(os.listdir(dir_path))
        if is_audio_file(f)
    ]
    
    if not audio_files:
        logger.warning(f"No audio files found in: {dir_path}")
        return
    
    # Track processed files in case we need to resume
    processed_files = []
    
    try:
        # Process each file and append to the audiobook text
        with open(audiobook_output, 'w', encoding='utf-8') as output_file:
            for i, audio_file in enumerate(audio_files):
                logger.info(f"Processing audiobook part [{i+1}/{len(audio_files)}]: {audio_file}")
                
                # Transcribe audio
                result = model.transcribe(audio_file)
                
                # Write chapter header and content
                file_name = os.path.basename(audio_file)
                output_file.write(f"\n\n--- Chapter/Part: {file_name} ---\n\n")
                output_file.write(result["text"])
                
                # Mark file as processed
                processed_files.append(audio_file)
        
        logger.info(f"Audiobook transcription complete: {audiobook_output}")
        
        # Move the entire directory to processed
        processed_path = os.path.join(processed_dir, os.path.basename(dir_path))
        if os.path.exists(processed_path):
            processed_path = f"{processed_path}_{timestamp}"
        
        shutil.move(dir_path, processed_path)
        logger.info(f"Moved audiobook directory to: {processed_path}")
        
    except Exception as e:
        logger.error(f"Error processing audiobook: {str(e)}")
        logger.info(f"Processed {len(processed_files)} of {len(audio_files)} files before error")

def move_to_processed(file_path, processed_dir):
    """Move a processed file to the processed directory."""
    if not os.path.exists(file_path):
        return
    
    filename = os.path.basename(file_path)
    dest_path = os.path.join(processed_dir, filename)
    
    # Handle duplicate names
    if os.path.exists(dest_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, extension = os.path.splitext(filename)
        dest_path = os.path.join(processed_dir, f"{base_name}_{timestamp}{extension}")
    
    shutil.move(file_path, dest_path)
    logger.info(f"Moved processed file to: {dest_path}")

def process_dropbox(dropbox_dir, output_dir, processed_dir, model_name="base"):
    """Process all items in the dropbox directory."""
    if not os.path.exists(dropbox_dir):
        logger.error(f"Dropbox directory not found: {dropbox_dir}")
        return
    
    try:
        # Import whisper here to handle potential import errors more gracefully
        import whisper
        
        # Load Whisper model
        logger.info(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        # Get items in dropbox
        items = os.listdir(dropbox_dir)
        
        if not items:
            logger.info("No items found in dropbox.")
            return
        
        for item in items:
            item_path = os.path.join(dropbox_dir, item)
            
            # Handle directories (audiobooks)
            if os.path.isdir(item_path):
                logger.info(f"Processing directory as audiobook: {item}")
                process_directory(item_path, output_dir, processed_dir, model)
            
            # Handle individual audio files
            elif is_audio_file(item):
                logger.info(f"Processing individual audio file: {item}")
                success = process_audio_file(item_path, output_dir, model)
                if success:
                    move_to_processed(item_path, processed_dir)
            
            else:
                logger.warning(f"Skipping unsupported item: {item}")
    
    except ImportError:
        logger.error("Failed to import Whisper. Make sure it's installed correctly.")
        logger.error("Install with: pip install git+https://github.com/openai/whisper.git")
        sys.exit(1)

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Process audio files in dropbox directory using OpenAI's Whisper."
    )
    parser.add_argument(
        "--model", 
        choices=["tiny", "base", "small", "medium", "large"], 
        default="base",
        help="Whisper model to use (default: base)"
    )
    parser.add_argument(
        "--base-dir", 
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Base directory for the script (default: script directory)"
    )
    
    args = parser.parse_args()
    
    # Setup directories
    dirs = setup_directories(args.base_dir)
    
    logger.info(f"Starting speech-to-text-dropbox with model: {args.model}")
    
    # Process the dropbox
    process_dropbox(
        dirs["dropbox"],
        dirs["output"],
        dirs["processed"],
        model_name=args.model
    )
    
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()

