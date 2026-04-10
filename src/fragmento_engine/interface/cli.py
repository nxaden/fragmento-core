from __future__ import annotations

import argparse
from pathlib import Path

from fragmento_engine import render_folder
from fragmento_engine import TimesliceSpec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a time-slice image from a sequence of photos."
    )
    parser.add_argument("input_folder", type=Path)
    parser.add_argument("output_file", type=Path)
    parser.add_argument(
        "--orientation",
        choices=["vertical", "horizontal"],
        default="vertical",
    )
    parser.add_argument("--slices", type=int, default=None)
    parser.add_argument(
        "--resize-mode",
        choices=["crop", "resize"],
        default="crop",
    )
    parser.add_argument("--reverse-time", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    spec = TimesliceSpec(
        orientation=args.orientation,
        num_slices=args.slices,
        reverse_time=args.reverse_time,
    )

    response = render_folder(
        input_folder=args.input_folder,
        output_file=args.output_file,
        spec=spec,
        resize_mode=args.resize_mode,
    )

    print(f"Rendered using {len(response.input_paths)} images.")
    print(f"Saved: {args.output_file}")


if __name__ == "__main__":
    main()
