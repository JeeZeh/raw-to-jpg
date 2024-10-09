from pathlib import Path
import os
import tqdm
import argparse
from PIL import Image

# params
parser = argparse.ArgumentParser(description="Convert RAW to JPG")
parser.add_argument(
    "-s",
    "--source",
    help="Source folder of RAW files",
    # required=True,
    default="C:\\Users\\jesse\\OneDrive\\Pictures\\Camera\\",
)
parser.add_argument(
    "-d",
    "--destination",
    help="Destination folder for converted JPG files",
    # required=True,
    default="C:\\Users\\jesse\\Desktop\\Camera\\",
)
parser.add_argument(
    "-r",
    "--raw_ext",
    help="RAW format extension (e.g. CR2)",
    # required=True,
    default="CR2",
)
parser.add_argument(
    "-t",
    "--preserve-times",
    help="Preserve the create and modified date for images.",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-e",
    "--preserve-exif",
    help="Preserve the EXIF information for images.",
    action="store_true",
    default=False,
)
args = parser.parse_args()

# dirs and files
raw_file_type = ".CR2"
raw_dir = Path(args.source)
converted_dir = Path(args.destination)
raw_images = raw_dir.glob(f"**/*.{args.raw_ext}")


def compress_raw(raw_file: Path, source_root: Path, destination_root: Path):
    # file vars
    file_timestamp = os.path.getctime(raw_file.resolve())

    # parse CR2 image
    img = Image.open(raw_file.resolve())
    dest = (destination_root / raw_file.relative_to(source_root)).with_suffix(".jpg")
    dest.parent.mkdir(exist_ok=True, parents=True)

    with dest.open(mode="w+") as out:
        img.save(
            out,
            format="JPEG",
            quality=95,
            exif=img.getexif() if args.preserve_exif else b"",
        )

    if args.preserve_times:
        os.utime(dest, (raw_file.lstat().st_ctime, raw_file.lstat().st_mtime))


if __name__ == "__main__":
    raws = [raw for raw in raw_images]
    for raw in tqdm.tqdm(raws):
        compress_raw(raw, source_root=raw_dir, destination_root=converted_dir)
