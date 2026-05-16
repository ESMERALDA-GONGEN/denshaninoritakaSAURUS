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
    "/usr/share/fonts/opentype/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """日本語は TTC が無いと load_default に落ちて極小になる（特に Linux クラウド）。"""
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _feeling_plain(s: str) -> str:
    """感想は「絵文字＋スペース＋ひらがな」想定。PNG では絵文字を除き□化を防ぐ。"""
    if not s or s == "きろくなし":
        return s
    if " " in s:
        return s.split(" ", 1)[1].strip()
    return s


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


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
    w = 1080
    pad = 44
    inner = 22

    # 1駅あたり：写真エリア（上）＋ テキスト（下）
    photo_band_h = 228
    text_zone_h = 118
    block_h = inner * 2 + photo_band_h + text_zone_h
    gap = 32
    header_h = 198

    ordered = [s for s in route_stations if s["id"] in set(gotten_off_ids)]
    id_order = {s["id"]: i for i, s in enumerate(route_stations)}
    ordered.sort(key=lambda s: id_order.get(s["id"], 999))

    total_h = header_h + gap + len(ordered) * (block_h + gap) + pad

    bg_top = (255, 250, 235)
    bg_bot = (186, 224, 253)
    img = Image.new("RGB", (w, total_h), bg_top)
    draw = ImageDraw.Draw(img)
    for yy in range(total_h):
        t = yy / max(total_h - 1, 1)
        r = int(bg_top[0] * (1 - t) + bg_bot[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bot[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bot[2] * t)
        draw.line([(0, yy), (w, yy)], fill=(r, g, b))

    font_title = _load_font(52)
    font_tag = _load_font(26)
    font_sub = _load_font(30)
    font_name = _load_font(40)
    font_small = _load_font(30)
    font_tiny = _load_font(22)

    # --- ヘッダー（影＋帯）絵文字は使わない（□防止） ---
    hx0, hy0, hx1, hy1 = pad, pad, w - pad, header_h
    draw.rounded_rectangle(
        [hx0 + 5, hy0 + 5, hx1 + 5, hy1 + 5],
        radius=32,
        fill=(203, 213, 225),
    )
    draw.rounded_rectangle(
        [hx0, hy0, hx1, hy1],
        radius=32,
        fill=(255, 255, 255),
        outline=(251, 191, 36),
        width=4,
    )
    cx = w // 2
    draw.text((cx, 56), TITLE, fill=(15, 23, 42), font=font_title, anchor="mm")
    draw.text((cx, 108), "とくべつな しんかんせん の きおく", fill=(100, 116, 139), font=font_tag, anchor="mm")
    date_s = datetime.now().strftime("%Y年%m月%d日")
    draw.text((cx, 148), date_s, fill=(148, 163, 184), font=font_sub, anchor="mm")

    y = header_h + gap

    for st in ordered:
        sid = st["id"]
        bx0, by0, bx1, by1 = pad, y, w - pad, y + block_h

        # カードのうすい影
        draw.rounded_rectangle(
            [bx0 + 4, by0 + 4, bx1 + 4, by1 + 4],
            radius=28,
            fill=(226, 232, 240),
        )
        draw.rounded_rectangle(
            [bx0, by0, bx1, by1],
            radius=28,
            fill=(255, 255, 255),
            outline=(147, 197, 253),
            width=3,
        )

        px0 = bx0 + inner
        py0 = by0 + inner
        px1 = bx1 - inner
        py1 = py0 + photo_band_h

        # 写真レンジ（内側のグレー台）
        draw.rounded_rectangle(
            [px0, py0, px1, py1],
            radius=22,
            fill=(248, 250, 252),
            outline=(226, 232, 240),
            width=2,
        )

        margin = 14
        thumb_max = (px1 - px0 - 2 * margin, py1 - py0 - 2 * margin)

        raw = photos.get(sid)
        pasted = False
        if raw:
            try:
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                im.thumbnail(thumb_max, Image.Resampling.LANCZOS)
                tw, th = im.size
                ox = px0 + margin + (thumb_max[0] - tw) // 2
                oy = py0 + margin + (thumb_max[1] - th) // 2
                rad = 18
                if tw >= 8 and th >= 8:
                    mask = _rounded_mask((tw, th), rad)
                    img.paste(im, (ox, oy), mask)
                else:
                    img.paste(im, (ox, oy))
                pasted = True
            except Exception:
                pasted = False

        if not pasted:
            draw.text(
                ((px0 + px1) // 2, (py0 + py1) // 2),
                "（しゃしんなし）",
                fill=(148, 163, 184),
                font=font_tiny,
                anchor="mm",
            )

        # テキストゾーン（中央寄せ）
        ty_base = py1 + 18
        cx_card = (bx0 + bx1) // 2
        station_line = f"★ {st['name']}えき"
        draw.text((cx_card, ty_base + 8), station_line, fill=(15, 23, 42), font=font_name, anchor="mm")

        feel_raw = feelings.get(sid, "きろくなし")
        feel = _feeling_plain(feel_raw)
        draw.text(
            (cx_card, ty_base + 58),
            feel,
            fill=(71, 85, 105),
            font=font_small,
            anchor="mm",
        )

        y += block_h + gap

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
