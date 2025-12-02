This started as a personal project to automate converting a folder of image files so they were all png files. It quickly grew into wanting to be able to convert
any type of media easily.
<br/>
<br/>As of now the script can convert media files between different formates using ffmpeg and ImageMagick.
<br/>The script will automatically select the best tool for the conversion task based on file types and checks
<br/>if images are animated prior to converting to GIF or video formats.

## TOOL REQUIREMENTS:
  <br/>• ffmpeg: Required for video conversions and video-to-GIF conversions
  <br/>• ImageMagick: Required for image conversions (install and ensure 'magick' command is available)

## USAGE:
  <br/>py_convert.py [--output OUTPUT] [--help] [--overwrite] <input_type> <output_type> <target>

## ARGUMENTS:
  <br/>input_type         Input file type/extension (e.g., jpg, png, webm, mp4, gif, webp)
  <br/>output_type        Output file type/extension (e.g., png, gif, mp4, jpg)
  <br/>target             Input file or directory containing files to convert
  <br/>--output, -o       (Optional) Output directory (default: same as input directory)
  <br/>--help, -h         Shows a help message and then exits.
  <br/>--overwrite, -w    Auto-removes original files after conversion.

## SUPPORTED FORMATS:
  <br/>Video:  mp4, webm, avi, mkv, mov, flv, wmv, m4v, 3gp, mpg, mpeg
  <br/>Image:  jpg, jpeg, png, gif, webp, bmp, tiff, tif, ico, svg, heic, heif

## EXAMPLES:
  **Convert single image file**
  <br/>py_convert.py jpg png image.jpg

  **Convert video file and remove original**
  <br/>py_convert.py --overwrite webm mp4 video.webm

  **Convert all WebP files in a directory to GIF (only animated ones)**
  <br/>py_convert.py webp gif "C:\\Images"

  **Convert PNG files to JPG with custom output directory**
  <br/>py_convert.py png jpg "C:\\Images" --output "C:\\Output"

  **Convert animated GIF to WebP**
  <br/>py_convert.py gif webp animation.gif

  **Convert video to GIF**
  <br/>py_convert.py mp4 gif video.mp4

## NOTES:
  <br/>• Static (non-animated) images will be skipped when converting to GIF or video
  <br/>• The script automatically uses ffmpeg for video formats and ImageMagick for images
  <br/>• Both ffmpeg and ImageMagick must be installed and available in your PATH
  <br/>• File extensions can be specified with or without the leading dot (e.g., .jpg or jpg)