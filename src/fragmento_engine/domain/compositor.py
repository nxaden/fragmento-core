from __future__ import annotations

from collections.abc import Sequence as SequenceCollection
from typing import Sequence

import numpy as np

from .models import (
    CompositeResult,
    RGBImage,
    SliceBand,
    SliceEffects,
    TimeslicePlan,
    TimesliceSpec,
)
from .planner import build_timeslice_plan


def _validate_images(images: Sequence[RGBImage]) -> tuple[int, int, int]:
    if not images:
        raise ValueError("No images loaded.")

    first = images[0]
    if first.ndim != 3 or first.shape[2] != 3:
        raise ValueError("Expected RGB images.")

    height, width, channels = first.shape

    for i, img in enumerate(images):
        if img.ndim != 3 or img.shape[2] != 3:
            raise ValueError(f"Image at index {i} is not an RGB image.")
        if img.shape != (height, width, channels):
            raise ValueError(
                "All images must have the same dimensions after preprocessing."
            )

    return height, width, channels


def _validate_effects(effects: SliceEffects) -> None:
    if effects.border_width < 0:
        raise ValueError("effects.border_width must be at least 0.")
    if effects.shadow_width < 0:
        raise ValueError("effects.shadow_width must be at least 0.")
    if effects.feather_width < 0:
        raise ValueError("effects.feather_width must be at least 0.")
    if not 0.0 <= effects.shadow_opacity <= 1.0:
        raise ValueError("effects.shadow_opacity must be between 0.0 and 1.0.")
    if len(effects.border_color) != 3:
        raise ValueError("effects.border_color must contain exactly 3 channels.")
    if any(channel < 0 or channel > 255 for channel in effects.border_color):
        raise ValueError("effects.border_color channels must be between 0 and 255.")


def _inner_effect_extent(
    requested_width: int,
    band: SliceBand,
) -> int:
    band_span = band.end - band.start
    return min(requested_width, band_span // 2)


def _transition_alpha(width: int) -> np.ndarray:
    return ((np.arange(width, dtype=np.float32) + 0.5) / width).astype(np.float32)


def _shadow_weights(width: int, opacity: float, *, reverse: bool = False) -> np.ndarray:
    weights = opacity * ((np.arange(width, dtype=np.float32) + 1.0) / width)
    if reverse:
        weights = weights[::-1]
    return weights


def _blend_boundary(
    output: RGBImage,
    left_frame: RGBImage,
    right_frame: RGBImage,
    orientation: str,
    boundary: int,
    left_extent: int,
    right_extent: int,
) -> None:
    start = boundary - left_extent
    end = boundary + right_extent
    if start >= end:
        return

    alpha = _transition_alpha(end - start)

    if orientation == "vertical":
        left_region = left_frame[:, start:end, :].astype(np.float32)
        right_region = right_frame[:, start:end, :].astype(np.float32)
        weights = alpha.reshape(1, -1, 1)
        output[:, start:end, :] = np.rint(
            left_region * (1.0 - weights) + right_region * weights
        ).astype(np.uint8)
    else:
        left_region = left_frame[start:end, :, :].astype(np.float32)
        right_region = right_frame[start:end, :, :].astype(np.float32)
        weights = alpha.reshape(-1, 1, 1)
        output[start:end, :, :] = np.rint(
            left_region * (1.0 - weights) + right_region * weights
        ).astype(np.uint8)


def _apply_shadow_region(
    output: RGBImage,
    orientation: str,
    start: int,
    end: int,
    weights: np.ndarray,
) -> None:
    if start >= end:
        return

    if orientation == "vertical":
        region = output[:, start:end, :].astype(np.float32)
        factors = (1.0 - weights).reshape(1, -1, 1)
        output[:, start:end, :] = np.rint(region * factors).astype(np.uint8)
    else:
        region = output[start:end, :, :].astype(np.float32)
        factors = (1.0 - weights).reshape(-1, 1, 1)
        output[start:end, :, :] = np.rint(region * factors).astype(np.uint8)


def _apply_boundary_shadow(
    output: RGBImage,
    orientation: str,
    boundary: int,
    left_extent: int,
    right_extent: int,
    opacity: float,
) -> None:
    if left_extent > 0:
        left_weights = _shadow_weights(left_extent, opacity)
        _apply_shadow_region(
            output=output,
            orientation=orientation,
            start=boundary - left_extent,
            end=boundary,
            weights=left_weights,
        )

    if right_extent > 0:
        right_weights = _shadow_weights(right_extent, opacity, reverse=True)
        _apply_shadow_region(
            output=output,
            orientation=orientation,
            start=boundary,
            end=boundary + right_extent,
            weights=right_weights,
        )


def _apply_boundary_border(
    output: RGBImage,
    orientation: str,
    boundary: int,
    width: int,
    color: SequenceCollection[int],
) -> None:
    if width <= 0:
        return

    span = output.shape[1] if orientation == "vertical" else output.shape[0]
    start = max(0, boundary - (width // 2))
    end = min(span, start + width)
    border_color = np.asarray(color, dtype=np.uint8)

    if orientation == "vertical":
        output[:, start:end, :] = border_color
    else:
        output[start:end, :, :] = border_color


def _apply_slice_effects(
    output: RGBImage,
    images: Sequence[RGBImage],
    plan: TimeslicePlan,
    effects: SliceEffects,
) -> None:
    _validate_effects(effects)

    if len(plan.bands) < 2:
        return

    for left_band, right_band in zip(plan.bands, plan.bands[1:]):
        boundary = left_band.end
        if boundary != right_band.start:
            continue

        left_frame = images[left_band.frame_index]
        right_frame = images[right_band.frame_index]

        feather_left = _inner_effect_extent(effects.feather_width, left_band)
        feather_right = _inner_effect_extent(effects.feather_width, right_band)
        if feather_left > 0 or feather_right > 0:
            _blend_boundary(
                output=output,
                left_frame=left_frame,
                right_frame=right_frame,
                orientation=plan.orientation,
                boundary=boundary,
                left_extent=feather_left,
                right_extent=feather_right,
            )

        shadow_left = _inner_effect_extent(effects.shadow_width, left_band)
        shadow_right = _inner_effect_extent(effects.shadow_width, right_band)
        if (shadow_left > 0 or shadow_right > 0) and effects.shadow_opacity > 0.0:
            _apply_boundary_shadow(
                output=output,
                orientation=plan.orientation,
                boundary=boundary,
                left_extent=shadow_left,
                right_extent=shadow_right,
                opacity=effects.shadow_opacity,
            )

        if effects.border_width > 0:
            _apply_boundary_border(
                output=output,
                orientation=plan.orientation,
                boundary=boundary,
                width=effects.border_width,
                color=effects.border_color,
            )


def apply_timeslice_plan(
    images: Sequence[RGBImage],
    plan: TimeslicePlan,
    effects: SliceEffects | None = None,
) -> CompositeResult:
    height, width, _ = _validate_images(images)
    output = np.zeros((height, width, 3), dtype=np.uint8)

    for band in plan.bands:
        frame = images[band.frame_index]

        if plan.orientation == "vertical":
            output[:, band.start : band.end, :] = frame[:, band.start : band.end, :]
        else:
            output[band.start : band.end, :, :] = frame[band.start : band.end, :, :]

    if effects is not None:
        _apply_slice_effects(
            output=output,
            images=images,
            plan=plan,
            effects=effects,
        )

    used_frame_indices = sorted({band.frame_index for band in plan.bands})

    return CompositeResult(
        image=output,
        plan=plan,
        used_frame_indices=used_frame_indices,
    )


def build_timeslice(
    images: Sequence[RGBImage],
    spec: TimesliceSpec | None = None,
) -> CompositeResult:
    if spec is None:
        spec = TimesliceSpec()

    plan = build_timeslice_plan(images=images, spec=spec)
    return apply_timeslice_plan(images=images, plan=plan, effects=spec.effects)
