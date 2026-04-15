from __future__ import annotations

import argparse
from pathlib import Path

from fragmento_engine import render_folder
from fragmento_engine import SliceEffects, TimesliceSpec


def _parse_color(value: str) -> tuple[int, int, int]:
    raw = value.strip()

    if "," in raw:
        parts = [part.strip() for part in raw.split(",")]
        if len(parts) != 3:
            raise argparse.ArgumentTypeError(
                "Expected a color in R,G,B format with exactly 3 channels."
            )

        try:
            channels = tuple(int(part) for part in parts)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "RGB channels must be integers between 0 and 255."
            ) from exc
    else:
        hex_value = raw.removeprefix("#")
        if len(hex_value) != 6:
            raise argparse.ArgumentTypeError(
                "Expected a color in #RRGGBB or R,G,B format."
            )

        try:
            channels = tuple(
                int(hex_value[index : index + 2], 16) for index in (0, 2, 4)
            )
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "Hex colors must use valid hexadecimal digits."
            ) from exc

    if any(channel < 0 or channel > 255 for channel in channels):
        raise argparse.ArgumentTypeError("Color channels must be between 0 and 255.")

    return channels


def _build_effects(args: argparse.Namespace) -> SliceEffects | None:
    if (
        args.border <= 0
        and args.shadow <= 0
        and args.highlight <= 0
        and args.feather <= 0
    ):
        return None

    return SliceEffects(
        border_width=args.border,
        border_color=args.border_color,
        border_opacity=args.border_opacity,
        border_color_mode=args.border_color_mode,
        shadow_width=args.shadow,
        shadow_opacity=args.shadow_opacity,
        highlight_width=args.highlight,
        highlight_opacity=args.highlight_opacity,
        highlight_color=args.highlight_color,
        feather_width=args.feather,
        curve=args.curve,
    )


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
    parser.add_argument(
        "--border",
        type=int,
        default=0,
        help="Divider thickness in pixels drawn at slice boundaries.",
    )
    parser.add_argument(
        "--border-color",
        type=_parse_color,
        default=(255, 255, 255),
        metavar="COLOR",
        help="Border color as #RRGGBB or R,G,B.",
    )
    parser.add_argument(
        "--border-opacity",
        type=float,
        default=1.0,
        help="Border blend strength from 0.0 to 1.0.",
    )
    parser.add_argument(
        "--border-color-mode",
        choices=["solid", "auto", "gradient"],
        default="solid",
        help=(
            "How divider colors are resolved: fixed color, auto-sampled, "
            "or sampled gradient."
        ),
    )
    parser.add_argument(
        "--shadow",
        type=int,
        default=0,
        help="Inner shadow width in pixels on each side of a slice boundary.",
    )
    parser.add_argument(
        "--shadow-opacity",
        type=float,
        default=0.35,
        help="Shadow strength from 0.0 to 1.0.",
    )
    parser.add_argument(
        "--highlight",
        type=int,
        default=0,
        help="Inner highlight width in pixels on each side of a slice boundary.",
    )
    parser.add_argument(
        "--highlight-opacity",
        type=float,
        default=0.35,
        help="Highlight strength from 0.0 to 1.0.",
    )
    parser.add_argument(
        "--highlight-color",
        type=_parse_color,
        default=(255, 255, 255),
        metavar="COLOR",
        help="Highlight color as #RRGGBB or R,G,B.",
    )
    parser.add_argument(
        "--feather",
        type=int,
        default=0,
        help="Blend width in pixels applied inside each neighboring slice.",
    )
    parser.add_argument(
        "--curve",
        choices=["linear", "smoothstep", "cosine", "hard"],
        default="linear",
        help=(
            "Boundary ramp curve used by feather, shadow, highlight, "
            "and gradient borders."
        ),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    spec = TimesliceSpec(
        orientation=args.orientation,
        num_slices=args.slices,
        reverse_time=args.reverse_time,
        effects=_build_effects(args),
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
