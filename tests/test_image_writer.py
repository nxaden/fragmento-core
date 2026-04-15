from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence

from pytimeslice.infrastructure.image_writer import PILImageWriter


def _solid_frame(value: int, *, width: int = 6, height: int = 4) -> np.ndarray:
    return np.full((height, width, 3), value, dtype=np.uint8)


def test_pil_image_writer_saves_png_to_disk(tmp_path: Path) -> None:
    output_file = tmp_path / "out" / "timeslice.png"
    image = _solid_frame(123)

    PILImageWriter().save(image, output_file)

    assert output_file.exists()
    with Image.open(output_file) as opened:
        assert opened.size == (6, 4)
        assert opened.mode == "RGB"
        assert np.array_equal(np.array(opened), image)


def test_pil_image_writer_saves_gif_with_expected_frame_order(tmp_path: Path) -> None:
    output_file = tmp_path / "out" / "progression.gif"
    frames = [
        _solid_frame(0),
        _solid_frame(64),
        _solid_frame(128),
        _solid_frame(64),
    ]

    PILImageWriter().save_gif(frames, output_file, duration_ms=90)

    assert output_file.exists()
    with Image.open(output_file) as opened:
        assert opened.n_frames == 4
        assert opened.info["loop"] == 0
        assert opened.info["duration"] == 90

        saved_frames = [
            np.array(frame.convert("RGB")) for frame in ImageSequence.Iterator(opened)
        ]

    assert len(saved_frames) == len(frames)
    for saved_frame, expected_frame in zip(saved_frames, frames):
        assert np.array_equal(saved_frame, expected_frame)
