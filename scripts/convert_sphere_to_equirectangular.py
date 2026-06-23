#!/usr/bin/env python3
"""Convert COLMAP reconstructions from sphere-sfm's SPHERE model to upstream's EQUIRECTANGULAR model.

sphere-sfm (a COLMAP 3.8 fork) added a camera model named "SPHERE" (model ID 11) with
parameters "f, cx, cy". Upstream COLMAP 4.x instead provides a native "EQUIRECTANGULAR"
model (model ID 17) whose parameters are simply "w, h" (the image dimensions).

This script converts the text-format reconstruction files produced by sphere-sfm so
they can be loaded by upstream COLMAP 4.x:

    cameras.txt   -> SPHERE cameras become EQUIRECTANGULAR
    images.txt    -> copied unchanged
    points3D.txt  -> copied unchanged

Binary reconstructions (cameras.bin/images.bin/points3D.bin) are not supported here
because upstream 4.x additionally expects rigs.bin/frames.bin. If you have binary files,
first run `colmap model_converter --input_type bin --output_type txt` with sphere-sfm,
then run this script, then load the result in upstream COLMAP.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def convert_cameras_text(input_path: Path, output_path: Path) -> int:
    """Convert cameras.txt: SPHERE -> EQUIRECTANGULAR.

    Returns the number of cameras converted.
    """
    converted = 0
    out_lines: list[str] = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                out_lines.append(line.rstrip("\n"))
                continue

            parts = stripped.split()
            # Text format:
            # CAMERA_ID MODEL WIDTH HEIGHT PARAMS...
            if len(parts) < 5:
                out_lines.append(line.rstrip("\n"))
                continue

            model_name = parts[1]
            if model_name != "SPHERE":
                out_lines.append(line.rstrip("\n"))
                continue

            camera_id = parts[0]
            width = parts[2]
            height = parts[3]
            # Old SPHERE params: f, cx, cy. New EQUIRECTANGULAR params: w, h.
            new_params = f"{width}, {height}"
            out_lines.append(
                f"{camera_id} EQUIRECTANGULAR {width} {height} {new_params}"
            )
            converted += 1

    output_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return converted


def copy_if_exists(src: Path, dst: Path) -> bool:
    if src.exists():
        shutil.copy2(src, dst)
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a sphere-sfm reconstruction to upstream COLMAP 4.x "
            "EQUIRECTANGULAR format."
        )
    )
    parser.add_argument(
        "--input_path",
        type=Path,
        required=True,
        help="Directory containing sphere-sfm cameras.txt (and optionally images.txt, points3D.txt).",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        required=True,
        help="Directory to write the converted reconstruction.")
    args = parser.parse_args(argv)

    input_path: Path = args.input_path
    output_path: Path = args.output_path

    if not input_path.is_dir():
        print(f"ERROR: input path is not a directory: {input_path}", file=sys.stderr)
        return 1

    output_path.mkdir(parents=True, exist_ok=True)

    cameras_in = input_path / "cameras.txt"
    cameras_out = output_path / "cameras.txt"
    if cameras_in.exists():
        converted = convert_cameras_text(cameras_in, cameras_out)
        print(f"Converted {converted} SPHERE camera(s) to EQUIRECTANGULAR.")
    else:
        print(
            "WARNING: cameras.txt not found. Binary conversion is not supported "
            "by this script; convert to text first with sphere-sfm's "
            "`colmap model_converter --input_type bin --output_type txt`.",
            file=sys.stderr,
        )

    for filename in ("images.txt", "points3D.txt"):
        copied = copy_if_exists(input_path / filename, output_path / filename)
        if copied:
            print(f"Copied {filename} unchanged.")

    print(f"Output written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
