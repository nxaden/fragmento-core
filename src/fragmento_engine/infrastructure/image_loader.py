from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image

from fragmento_engine.shared.types import ResizeMode
from fragmento_engine.domain.models import RGBImage

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def center_crop_to_size(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Resize an image to fill the target size, then crop the center region."""
    w, h = img.size

    scale = max(target_w / w, target_h / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))

    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    return resized.crop((left, top, right, bottom))


class PILImageSequenceLoader:
    """PIL-based infrastructure adapter for discovering and loading image sequences."""

    def get_image_paths(self, folder: Path) -> list[Path]:
        """Return supported image paths in sorted order."""
        paths = [
            p
            for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
        ]
        paths.sort()
        return paths

    def load_images(
        self,
        paths: Sequence[Path],
        resize_mode: ResizeMode = "crop",
    ) -> list[RGBImage]:
        """Load image files into normalized RGB numpy arrays."""
        if not paths:
            raise ValueError("No images found in the input folder.")

        images: list[RGBImage] = []

        with Image.open(paths[0]) as first_img:
            first = first_img.convert("RGB")
            base_w, base_h = first.size
            images.append(np.array(first, dtype=np.uint8))

        for path in paths[1:]:
            with Image.open(path) as opened:
                img = opened.convert("RGB")
                w, h = img.size

                if (w, h) != (base_w, base_h):
                    if resize_mode == "resize":
                        img = img.resize((base_w, base_h), Image.Resampling.LANCZOS)
                    elif resize_mode == "crop":
                        img = center_crop_to_size(img, base_w, base_h)
                    else:
                        raise ValueError(f"Unsupported resize_mode: {resize_mode}")

                images.append(np.array(img, dtype=np.uint8))

        return images
