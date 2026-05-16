"""スマホ写真の EXIF 向きを反映する。"""

from __future__ import annotations

import io

from PIL import Image, ImageOps


def load_image_upright(data: bytes) -> Image.Image:
    """JPEG/HEIC 等の Orientation を適用してから RGB にそろえる。"""
    im = Image.open(io.BytesIO(data))
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")
