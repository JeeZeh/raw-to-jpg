import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
import platform
from pprint import pprint
from win32_setctime import setctime

import tqdm
from PIL import Image


def parse_args():
    # params
    parser = argparse.ArgumentParser(description="Convert RAW to JPEG")
    parser.add_argument(
        "-s", "--source", help="Source folder of RAW files.", required=True
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="Destination folder for converted JPEG files. (Default=.tmp/)",
    )
    parser.add_argument(
        "-e",
        "--raw_extension",
        help="RAW format extension (e.g. CR2).",
        required=True,
    )
    parser.add_argument(
        "-q",
        "--quality",
        help="JPEG quality to use during conversion (1-100, Default=95).",
        default=95,
    )
    parser.add_argument(
        "-b",
        "--last_modified_before",
        help="Filter to photos last modified on or before this date (Format: YYYY-MM-DD).",
    )
    parser.add_argument(
        "--preserve-times",
        help="Preserve the accessed and modified date for images. NOTE: file creation time cannot be preserved.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--preserve-exif",
        help="Preserve the EXIF information for images.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--replace",
        help="Replace original files with JPEG versions.",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    if args.replace and args.destination:
        raise ValueError(
            "'-d/--destination' must not be specified when '-r/--replace' is also specified."
        )

    return args


def compress_raw(
    raw_file: Path,
    source_root: Path,
    destination_root: Path,
    quality=95,
    preserve_exif=False,
    preserve_times=False,
):
    # parse CR2 image
    img = Image.open(raw_file.resolve())
    dest = (destination_root / raw_file.relative_to(source_root)).with_suffix(".jpg")

    if dest.exists():
        return (raw_file, dest)

    dest.parent.mkdir(exist_ok=True, parents=True)

    img.save(
        dest,
        format="JPEG",
        quality=max(1, min(100, quality)),
        exif=img.getexif() if preserve_exif else b"",
    )

    if preserve_times:
        # Transfer create date (Windows only).
        if platform.system() == "Windows":
            # A 'fake' create date may exist if the file is moved or copied, in this case, we will take the
            # modified date if it is earlier.
            create_date = min(raw_file.lstat().st_mtime, raw_file.lstat().st_ctime)
            setctime(dest, create_date)

        # Transfer accessed and modified time.
        os.utime(dest, (raw_file.lstat().st_atime, raw_file.lstat().st_mtime))

    return (raw_file, dest)


if __name__ == "__main__":
    args = parse_args()

    raw_file_type = ".CR2"
    src_dir = Path(args.source)
    dest_dir = Path(args.destination) if args.destination else src_dir / ".tmp"
    raw_images = list(src_dir.glob(f"**/*.{args.raw_extension}"))

    if args.last_modified_before:
        last_modified_date = datetime.strptime(
            args.last_modified_before, "%Y-%m-%d"
        ).date()
        raw_images = [
            raw
            for raw in raw_images
            if datetime.fromtimestamp(raw.lstat().st_mtime, tz=timezone.utc).date()
            <= last_modified_date
        ]
        print(
            f"Found {len(raw_images)} RAW images(s) last modified on or before {last_modified_date} (src={src_dir}, ext={args.raw_extension})"
        )
    else:
        print(
            f"Found {len(raw_images)} RAW image(s) (src={src_dir}, ext={args.raw_extension})"
        )

    process_args = {
        "quality": int(args.quality),
        "preserve_exif": args.preserve_exif,
        "preserve_times": args.preserve_times,
    }

    print("Configuration:")
    pprint(
        {"source": src_dir, "destination": dest_dir, **process_args},
        indent=2,
        width=1,
    )
    input("Press any key to begin processing...")

    results: list[tuple[Path, Path]] = []
    for raw in tqdm.tqdm(raw_images):
        results.append(
            compress_raw(
                raw, source_root=src_dir, destination_root=dest_dir, **process_args
            )
        )

    if args.replace:
        input("Press any key to replace original images with compressed versions.")
        for original, new in tqdm.tqdm(results):
            if new.relative_to(dest_dir).with_suffix("") != original.relative_to(
                src_dir
            ).with_suffix(""):
                raise ValueError(
                    f"Original file '{original}' does not match new file '{new}'"
                )
            # Replace the original file with the new file
            replaced = new.replace(original.with_suffix(new.suffix))
            # Ensure we keep the same extension (e.g. jpg).
            original.unlink(missing_ok=True)
