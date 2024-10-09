# CR2 to JPG

A simple Python script to convert RAW photos to JPG and retain timestamps.

## Instructions

1. Clone or download
2. Install required packages with `pip install`
3. Run the script and pass source and destination folders, for example: `python ./raw-to-jpg.py --source ~/Desktop/raw --destination ~/Desktop/converted --raw_ext CR2`

### Additional args

- `h, --help`
  - show this help message and exit
- `s SOURCE, --source SOURCE`
  - Source folder of RAW files
- `d DESTINATION, --destination DESTINATION`
  - Destination folder for converted JPG files
- `r RAW_EXT, --raw_ext RAW_EXT`
  - RAW format extension (e.g. CR2)
- `t, --preserve-times`
  - Preserve the create and modified date for images.
- `e, --preserve-exif`
  - Preserve the EXIF information for images.

## Requirements

Script requires the following packages:

- `tqdm` from https://pypi.python.org/pypi/numpy
- `PIL` from https://pypi.python.org/pypi/Pillow

These are now set in requirements.txt for easier install.

Thanks to @mateusz-michalik for the original idea (forked)!
