This started as a personal project to automate converting a folder of image files so they were all png files. It quickly grew into wanting to be able to convert
any type of media easily.

DESCRIPTION:
  Convert media files between different formats using ffmpeg and ImageMagick.
  Automatically selects the appropriate tool based on file types and checks
  if images are animated before converting to GIF or video formats.

USAGE:
  py_convert.py <input_type> <output_type> <target> [--output DIR]

ARGUMENTS:
  input_type    Input file type/extension (e.g., jpg, png, webm, mp4, gif, webp)
  output_type   Output file type/extension (e.g., png, gif, mp4, jpg)
  target        Input file or directory containing files to convert
  --output, -o  (Optional) Output directory (default: same as input directory)

SUPPORTED FORMATS:
  Video:  mp4, webm, avi, mkv, mov, flv, wmv, m4v, 3gp, mpg, mpeg
  Image:  jpg, jpeg, png, gif, webp, bmp, tiff, tif, ico, svg, heic, heif

EXAMPLES:
  **Convert single image file**
  py_convert.py jpg png image.jpg

  **Convert video file**
  py_convert.py webm mp4 video.webm

  **Convert all WebP files in a directory to GIF (only animated ones)**
  py_convert.py webp gif "C:\\Images"

  **Convert PNG files to JPG with custom output directory**
  py_convert.py png jpg "C:\\Images" --output "C:\\Output"

  **Convert animated GIF to WebP**
  py_convert.py gif webp animation.gif

  **Convert video to GIF**
  py_convert.py mp4 gif video.mp4

NOTES:
  • Static (non-animated) images will be skipped when converting to GIF or video
  • The script automatically uses ffmpeg for video formats and ImageMagick for images
  • Both ffmpeg and ImageMagick must be installed and available in your PATH
  • File extensions can be specified with or without the leading dot (e.g., .jpg or jpg)

TOOL REQUIREMENTS:
  • ffmpeg: Required for video conversions and video-to-GIF conversions
  • ImageMagick: Required for image conversions (install and ensure 'magick' command is available)
