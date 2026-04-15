from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

import numpy as np
import numpy.typing as npt

Orientation = Literal["vertical", "horizontal"]
BoundaryCurve = Literal["linear", "smoothstep", "cosine", "hard"]
BorderColorMode = Literal["solid", "auto", "gradient"]
RGBColor = tuple[int, int, int]
RGBImage = npt.NDArray[np.uint8]

_VALID_BORDER_COLOR_MODES = {"solid", "auto", "gradient"}
_VALID_CURVES = {"linear", "smoothstep", "cosine", "hard"}


@dataclass(frozen=True)
class FrameRef:
    """FrameRef is a reference to a singular source frame on disk."""

    index: int
    path: Path


@dataclass(frozen=True)
class SequenceInfo:
    """SequenceInfo describes the loaded sequence at a metadata level."""

    frames: list[FrameRef]
    height: int
    width: int
    channels: int = 3


@dataclass(frozen=True)
class SliceEffects:
    """SliceEffects describes optional treatments applied at slice boundaries."""

    border_width: int = 0
    border_color: RGBColor = (255, 255, 255)
    border_opacity: float = 1.0
    border_color_mode: BorderColorMode = "solid"
    shadow_width: int = 0
    shadow_opacity: float = 0.35
    highlight_width: int = 0
    highlight_opacity: float = 0.35
    highlight_color: RGBColor = (255, 255, 255)
    feather_width: int = 0
    curve: BoundaryCurve = "linear"


def validate_rgb_color(name: str, color: Sequence[int]) -> None:
    if len(color) != 3:
        raise ValueError(f"{name} must contain exactly 3 channels.")
    if any(channel < 0 or channel > 255 for channel in color):
        raise ValueError(f"{name} channels must be between 0 and 255.")


def validate_slice_effects(effects: SliceEffects) -> None:
    if effects.border_width < 0:
        raise ValueError("effects.border_width must be at least 0.")
    if effects.highlight_width < 0:
        raise ValueError("effects.highlight_width must be at least 0.")
    if effects.shadow_width < 0:
        raise ValueError("effects.shadow_width must be at least 0.")
    if effects.feather_width < 0:
        raise ValueError("effects.feather_width must be at least 0.")
    if not 0.0 <= effects.border_opacity <= 1.0:
        raise ValueError("effects.border_opacity must be between 0.0 and 1.0.")
    if not 0.0 <= effects.shadow_opacity <= 1.0:
        raise ValueError("effects.shadow_opacity must be between 0.0 and 1.0.")
    if not 0.0 <= effects.highlight_opacity <= 1.0:
        raise ValueError("effects.highlight_opacity must be between 0.0 and 1.0.")
    if effects.border_color_mode not in _VALID_BORDER_COLOR_MODES:
        raise ValueError(
            "effects.border_color_mode must be one of solid, auto, or gradient."
        )
    if effects.curve not in _VALID_CURVES:
        raise ValueError(
            "effects.curve must be one of linear, smoothstep, cosine, or hard."
        )
    validate_rgb_color("effects.border_color", effects.border_color)
    validate_rgb_color("effects.highlight_color", effects.highlight_color)


@dataclass(frozen=True)
class TimesliceSpec:
    """TimesliceSpec is the user's render intent."""

    orientation: Orientation = "vertical"
    num_slices: int | None = None
    reverse_time: bool = False
    effects: SliceEffects | None = None


@dataclass(frozen=True)
class SliceBand:
    """SliceBand describes one slice, meaning which frame it comes from and what pixel range it occupies."""

    frame_index: int
    start: int
    end: int


@dataclass(frozen=True)
class TimeslicePlan:
    """TimeslicePlan is the full slice layout."""

    orientation: Orientation
    bands: list[SliceBand]


@dataclass(frozen=True)
class CompositeResult:
    """CompositeResult is the final output plus traceable metadata."""

    image: RGBImage
    plan: TimeslicePlan
    used_frame_indices: list[int]
