#!/usr/bin/env python3
"""
Media converter script using ffmpeg and ImageMagick.
Converts files between different formats with automatic tool selection
and animation detection.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

# Format definitions
VIDEO_FORMATS = {'mp4', 'webm', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'm4v', '3gp', 'mpg', 'mpeg'}
IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif', 'ico', 'svg', 'heic', 'heif'}
ANIMATED_IMAGE_FORMATS = {'gif', 'webp'}  # Formats that can be animated


def normalize_extension(ext: str) -> str:
    """Remove leading dot and convert to lowercase."""
    return ext.lstrip('.').lower()


def is_video_format(ext: str) -> bool:
    """Check if extension is a video format."""
    return normalize_extension(ext) in VIDEO_FORMATS


def is_image_format(ext: str) -> bool:
    """Check if extension is an image format."""
    return normalize_extension(ext) in IMAGE_FORMATS


def check_tool_available(tool: str) -> bool:
    """Check if a command-line tool is available."""
    try:
        subprocess.run([tool, '-version'], stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_image_animated(file_path: Path) -> bool:
    """
    Check if an image file is animated (has multiple frames).
    Returns True if animated, False if static or if check fails.
    """
    ext = normalize_extension(file_path.suffix)
    
    # Only GIF and WebP can be animated images
    if ext not in ANIMATED_IMAGE_FORMATS:
        return False
    
    # Try using ImageMagick identify command
    try:
        result = subprocess.run(
            ['magick', 'identify', '-format', '%[nframes]', str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        frame_count = result.stdout.strip()
        if frame_count and frame_count.isdigit():
            return int(frame_count) > 1
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback: Try using PIL/Pillow if available
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            # Check if image has multiple frames
            try:
                img.seek(1)  # Try to seek to second frame
                return True
            except EOFError:
                return False
    except (ImportError, Exception):
        pass
    
    # If we can't determine, assume it's not animated to be safe
    return False


def should_convert_to_animated(input_path: Path, input_ext: str, output_ext: str) -> bool:
    """
    Determine if conversion to animated format (GIF/video) should proceed.
    Returns False if input is not animated and output requires animation.
    """
    output_ext = normalize_extension(output_ext)
    
    # If output is not an animated format, always allow
    if output_ext not in {'gif'} and not is_video_format(output_ext):
        return True
    
    # If input is a video, it's always "animated"
    if is_video_format(input_ext):
        return True
    
    # If input is an image, check if it's animated
    if is_image_format(input_ext):
        if is_image_animated(input_path):
            return True
        else:
            print(f"Skipping static image (not animated): {input_path.name}")
            return False
    
    # Unknown format, allow conversion
    return True


def determine_tool(input_ext: str, output_ext: str) -> Tuple[bool, bool]:
    """
    Determine which tool(s) to use based on input and output formats.
    Returns (use_ffmpeg, use_imagemagick)
    """
    input_ext = normalize_extension(input_ext)
    output_ext = normalize_extension(output_ext)
    
    use_ffmpeg = False
    use_imagemagick = False
    
    # Video formats always use ffmpeg
    if is_video_format(input_ext) or is_video_format(output_ext):
        use_ffmpeg = True
    
    # Image formats typically use ImageMagick
    if is_image_format(input_ext) or is_image_format(output_ext):
        use_imagemagick = True
    
    # Special cases
    # Video to GIF: use ffmpeg
    if is_video_format(input_ext) and output_ext == 'gif':
        use_ffmpeg = True
        use_imagemagick = False
    
    # Animated WebP/GIF conversions: prefer ImageMagick
    if input_ext == 'webp' and output_ext == 'gif':
        use_imagemagick = True
        use_ffmpeg = False
    if input_ext == 'gif' and output_ext == 'webp':
        use_imagemagick = True
        use_ffmpeg = False
    
    # If both could work, prefer ImageMagick for image-to-image, ffmpeg for video
    if use_ffmpeg and use_imagemagick:
        if is_video_format(input_ext) or is_video_format(output_ext):
            use_imagemagick = False
        else:
            use_ffmpeg = False
    
    # If neither selected, default to ffmpeg
    if not use_ffmpeg and not use_imagemagick:
        use_ffmpeg = True
    
    return use_ffmpeg, use_imagemagick


def convert_with_ffmpeg(input_path: Path, output_path: Path, output_ext: str) -> bool:
    """Convert file using ffmpeg."""
    output_ext = normalize_extension(output_ext)
    
    try:
        if output_ext == 'gif':
            # Video to GIF with palette optimization
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-filter_complex', 'fps=20,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=reserve_transparent=on[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5',
                '-loop', '0',
                str(output_path),
                '-y',
                '-loglevel', 'error',
                '-hide_banner'
            ]
        else:
            # Standard conversion
            cmd = [
                'ffmpeg', '-i', str(input_path),
                str(output_path),
                '-y',
                '-loglevel', 'error',
                '-hide_banner'
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path.exists()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: ffmpeg conversion failed: {e}")
        return False


def convert_with_imagemagick(input_path: Path, output_path: Path, input_ext: str, output_ext: str) -> bool:
    """Convert file using ImageMagick."""
    input_ext = normalize_extension(input_ext)
    output_ext = normalize_extension(output_ext)
    
    try:
        if input_ext == 'webp' and output_ext == 'gif':
            # Animated WebP to GIF
            cmd = ['magick', str(input_path), '-layers', 'Optimize', str(output_path)]
        else:
            # Standard conversion
            cmd = ['magick', str(input_path), str(output_path)]
        
        subprocess.run(cmd, check=True, capture_output=True)          
        return output_path.exists()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: ImageMagick conversion failed: {e}")
        return False


def convert_file(input_path: Path, input_ext: str, output_ext: str, output_dir: Optional[Path] = None) -> bool:
    """Convert a single file."""
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return False
    
    # Determine output path
    if output_dir:
        output_path = output_dir / f"{input_path.stem}.{normalize_extension(output_ext)}"
    else:
        output_path = input_path.parent / f"{input_path.stem}.{normalize_extension(output_ext)}"
    
    # Check if conversion to animated format should proceed
    if not should_convert_to_animated(input_path, input_ext, output_ext):
        return False
    
    # Determine which tool to use
    use_ffmpeg, use_imagemagick = determine_tool(input_ext, output_ext)
    
    print(f"Converting: {input_path.name} -> {output_path.name}")
    print(f"Using: {'ffmpeg' if use_ffmpeg else 'ImageMagick'}")
    
    # Perform conversion
    success = False
    if use_ffmpeg:
        if not check_tool_available('ffmpeg'):
            print("Error: ffmpeg is not available. Please install ffmpeg.")
            return False
        success = convert_with_ffmpeg(input_path, output_path, output_ext)
    elif use_imagemagick:
        if not check_tool_available('magick'):
            print("Error: ImageMagick is not available. Please install ImageMagick.")
            return False
        success = convert_with_imagemagick(input_path, output_path, input_ext, output_ext)
    
    if success:
        print(f"Success: Created {output_path.name}")
        if os.environ.get('PY_CONVERT_OVERWRITE') == '1':
            os.remove(input_path)
    else:
        print(f"Error: Conversion failed for {input_path.name}")
    
    return success


def find_files(input_path: Path, input_ext: str) -> List[Path]:
    """Find all files matching the input extension in the given path."""
    input_ext = normalize_extension(input_ext)
    files = []
    
    if input_path.is_file():
        # Check if file extension matches
        if normalize_extension(input_path.suffix) == input_ext:
            files.append(input_path)
    elif input_path.is_dir():
        # Find all files with matching extension
        pattern = f"*.{input_ext}"
        files = list(input_path.glob(pattern))
        # Also check case-insensitive
        if not files:
            files = [f for f in input_path.iterdir() 
                    if f.is_file() and normalize_extension(f.suffix) == input_ext]
    else:
        print(f"Error: Path does not exist: {input_path}")
    
    return files


def main():
    parser = argparse.ArgumentParser(
        description='Convert media files between different formats using ffmpeg and ImageMagick.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #add_help=True,
        epilog="""
Examples:
  %(prog)s jpg png image.jpg
  %(prog)s webm mp4 video.webm
  %(prog)s webp gif "C:\\Images"
  %(prog)s png jpg "C:\\Images" --output "C:\\Output"

NOTES:
  • The 'target' argument accepts either a single file or a directory
  • Static (non-animated) images will be skipped when converting to GIF or video
  • The script automatically uses ffmpeg for video formats and ImageMagick for images
  • Both ffmpeg and ImageMagick must be installed and available in your PATH
  • File extensions can be specified with or without the leading dot (e.g., .jpg or jpg)

TOOL REQUIREMENTS:
  • ffmpeg: Required for video conversions and video-to-GIF conversions
  • ImageMagick: Required for image conversions (install and ensure 'magick' command is available)
        """
    )
    
    #parser.add_argument('--help', '-h',
    #                    help='Show this help message and exit',
    #                    action='help')
    parser.add_argument('--overwrite', '-w',
                        help='Overwrite existing files',
                        action='store_true')
    parser.add_argument('input_type', 
                       help='Input file type/extension (e.g., jpg, png, webm, mp4)')
    parser.add_argument('output_type',
                       help='Output file type/extension (e.g., png, gif, mp4)')
    parser.add_argument('target',
                       help='Input file or directory containing files to convert')
    parser.add_argument('--output', '-o',
                       help='Output directory (default: same as input)',
                       default=None)
    
    
    args = parser.parse_args()
    
    # Check whether to overwrite existing files
    if not args.overwrite:
        print("Note: Existing files will not be overwritten unless --overwrite is specified.")
    else:
        print("Note: Existing files will be overwritten.")
        os.environ['PY_CONVERT_OVERWRITE'] = '1'

    # Debug: Print parsed arguments
    # print(f"DEBUG: Parsed arguments: {args}")
    print(f"DEBUG: Overwrite existing files: {os.environ.get('PY_CONVERT_OVERWRITE')}")

    # Normalize extensions
    input_ext = normalize_extension(args.input_type)
    output_ext = normalize_extension(args.output_type)
    
    # Resolve paths
    target_path = Path(args.target).resolve()
    output_dir = Path(args.output).resolve() if args.output else None
    
    if output_dir and not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error: Cannot create output directory: {e}")
            return 1
    
    # Find files to convert
    files = find_files(target_path, input_ext)
    
    if not files:
        print(f"No {input_ext} files found in {target_path}")
        return 1
    
    print(f"Found {len(files)} file(s) to convert")
    print(f"Converting {input_ext} -> {output_ext}")
    print()
    
    # Convert each file
    success_count = 0
    for file_path in files:
        if convert_file(file_path, input_ext, output_ext, output_dir):
            success_count += 1
        print()
    
    print(f"Conversion complete! {success_count}/{len(files)} file(s) converted successfully.")
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())

