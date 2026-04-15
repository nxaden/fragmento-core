from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt

Orientation = Literal["vertical", "horizontal"]
BoundaryCurve = Literal["linear", "smoothstep", "cosine", "hard"]
BorderColorMode = Literal["solid", "auto", "gradient"]
RGBColor = tuple[int, int, int]
RGBImage = npt.NDArray[np.uint8]


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
