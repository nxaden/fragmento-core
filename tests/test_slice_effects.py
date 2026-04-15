import numpy as np

from fragmento_engine import SliceEffects, TimesliceSpec, render_images
from fragmento_engine.interface.cli import _build_effects, build_parser


def _solid_frame(value: int, *, width: int = 8, height: int = 2) -> np.ndarray:
    return np.full((height, width, 3), value, dtype=np.uint8)


def test_feather_effect_blends_adjacent_slices() -> None:
    result = render_images(
        images=[_solid_frame(0), _solid_frame(200)],
        spec=TimesliceSpec(
            orientation="vertical",
            num_slices=2,
            effects=SliceEffects(feather_width=2),
        ),
    )

    first_row = result.image[0, :, 0].tolist()
    assert first_row == [0, 0, 25, 75, 125, 175, 200, 200]


def test_shadow_effect_darkens_boundary_pixels() -> None:
    result = render_images(
        images=[_solid_frame(200), _solid_frame(200)],
        spec=TimesliceSpec(
            orientation="vertical",
            num_slices=2,
            effects=SliceEffects(shadow_width=2, shadow_opacity=0.5),
        ),
    )

    first_row = result.image[0, :, 0].tolist()
    assert first_row == [200, 200, 150, 100, 100, 150, 200, 200]


def test_border_effect_draws_colored_divider() -> None:
    result = render_images(
        images=[_solid_frame(0), _solid_frame(255)],
        spec=TimesliceSpec(
            orientation="vertical",
            num_slices=2,
            effects=SliceEffects(border_width=1, border_color=(10, 20, 30)),
        ),
    )

    divider = result.image[:, 4, :]
    assert np.all(divider == np.array([10, 20, 30], dtype=np.uint8))


def test_cli_builds_slice_effects_from_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "frames",
            "out.jpg",
            "--border",
            "3",
            "--border-color",
            "#123456",
            "--shadow",
            "4",
            "--shadow-opacity",
            "0.6",
            "--feather",
            "5",
        ]
    )

    assert _build_effects(args) == SliceEffects(
        border_width=3,
        border_color=(18, 52, 86),
        shadow_width=4,
        shadow_opacity=0.6,
        feather_width=5,
    )
