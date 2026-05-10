"""縦長の旅アルバム画像を生成する。"""

from __future__ import annotations

import io
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

TITLE = "電車に乗りたかザウルス"

# フォントは環境依存のため、失敗時はデフォルトフォントにフォールバック
FONT_CANDIDATES = (
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_album_image(
    route_stations: list[dict],
    gotten_off_ids: list[str],
    photos: dict[str, bytes],
    feelings: dict[str, str],
) -> bytes:
    """
    降りた駅のみを順に並べた縦長PNGを返す。
    route_stations: 今回の旅の路線順の駅リスト
    gotten_off_ids: 降りた駅ID（路線順に並べる）
    """
    w = 900
    pad = 36
    header_h = 140
    block_h = 280
    gap = 24

    ordered = [s for s in route_stations if s["id"] in set(gotten_off_ids)]
    # 路線図の順序を保持
    id_order = {s["id"]: i for i, s in enumerate(route_stations)}
    ordered.sort(key=lambda s: id_order.get(s["id"], 999))

    total_h = header_h + gap + len(ordered) * (block_h + gap) + pad

    bg_top = (255, 248, 220)
    bg_bot = (186, 230, 253)
    img = Image.new("RGB", (w, total_h), bg_top)
    draw = ImageDraw.Draw(img)
    for y in range(total_h):
        t = y / max(total_h - 1, 1)
        r = int(bg_top[0] * (1 - t) + bg_bot[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bot[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bot[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    font_title = _load_font(40)
    font_sub = _load_font(22)
    font_name = _load_font(30)
    font_small = _load_font(20)

    # タイトル帯
    draw.rounded_rectangle(
        [pad, pad, w - pad, header_h - 20],
        radius=28,
        fill=(255, 255, 255),
        outline=(251, 191, 36),
        width=4,
    )
    draw.text((w // 2, 48), f"🦖 {TITLE}", fill=(30, 58, 95), font=font_title, anchor="mm")
    date_s = datetime.now().strftime("%Y年%m月%d日")
    draw.text((w // 2, 102), date_s, fill=(100, 116, 139), font=font_sub, anchor="mm")

    y = header_h + gap
    thumb_size = (260, 200)

    for st in ordered:
        sid = st["id"]
        draw.rounded_rectangle(
            [pad, y, w - pad, y + block_h],
            radius=24,
            fill=(255, 255, 255),
            outline=(147, 197, 253),
            width=3,
        )

        tx = pad + 24
        ty = y + 20
        draw.text((tx, ty), f"🦖 {st['name']}駅", fill=(30, 41, 59), font=font_name)

        feel = feelings.get(sid, "きろくなし")
        draw.text((tx, ty + 44), feel, fill=(71, 85, 105), font=font_small)

        px = w - pad - thumb_size[0] - 24
        py = y + (block_h - thumb_size[1]) // 2
        rect = [px, py, px + thumb_size[0], py + thumb_size[1]]
        draw.rounded_rectangle(rect, radius=16, fill=(241, 245, 249), outline=(226, 232, 240), width=2)

        raw = photos.get(sid)
        if raw:
            try:
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                im.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                tw, th = im.size
                ox = px + (thumb_size[0] - tw) // 2
                oy = py + (thumb_size[1] - th) // 2
                img.paste(im, (ox, oy))
            except Exception:
                draw.text(
                    (px + thumb_size[0] // 2, py + thumb_size[1] // 2),
                    "📷",
                    fill=(148, 163, 184),
                    font=font_title,
                    anchor="mm",
                )
        else:
            draw.text(
                (px + thumb_size[0] // 2, py + thumb_size[1] // 2),
                "📷",
                fill=(148, 163, 184),
                font=font_title,
                anchor="mm",
            )

        y += block_h + gap

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
