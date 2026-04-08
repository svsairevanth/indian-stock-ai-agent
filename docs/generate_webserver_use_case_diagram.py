from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT_PNG = Path(__file__).resolve().parent / "indian_stock_ai_agent_webserver_use_case.png"

BOX_FILL = "#fff2a8"
BOX_OUTLINE = "#c9b14a"
TEXT = "#24303c"
LINE = "#8e7b7b"


def load_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_center_text(draw: ImageDraw.ImageDraw, box, text: str, font, fill=TEXT, line_gap: int = 2):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = []
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        heights.append(bb[3] - bb[1])
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = (y1 + y2) / 2 - total / 2
    cx = (x1 + x2) / 2
    for idx, line in enumerate(lines):
        draw.text((cx, y), line, font=font, fill=fill, anchor="ma")
        y += heights[idx] + line_gap


def draw_box(draw: ImageDraw.ImageDraw, box, text: str, font):
    draw.rectangle(box, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    draw_center_text(draw, box, text, font)


def draw_arrow(draw: ImageDraw.ImageDraw, start, end):
    draw.line([start, end], fill=LINE, width=2)
    x, y = end
    draw.polygon([(x, y), (x - 8, y - 12), (x + 8, y - 12)], fill=LINE)


def main() -> None:
    width, height = 860, 520
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    title_font = load_font(18, bold=True)
    box_font = load_font(12, bold=True)
    list_font = load_font(13, bold=False)

    draw.text((24, 18), "Web Server Use Case", font=title_font, fill=TEXT)

    provider_box = (24, 84, 112, 118)
    user_box = (748, 84, 836, 118)
    server_box = (388, 390, 472, 436)

    draw_box(draw, provider_box, "Provider", box_font)
    draw_box(draw, user_box, "Remote\nUser", box_font)
    draw_box(draw, server_box, "Web\nServer", box_font)

    left_text = [
        "2: Admin login",
        "3: Manage users and sessions",
        "4: Review chat history",
        "5: Open generated reports",
        "6: View admin stats",
        "7: Check system health",
    ]
    right_text = [
        "1: Register and login",
        "8: Submit stock query",
        "9: Start async analysis job",
        "10: View result and PDF",
        "11: Read AI explanation",
        "12: View report history",
    ]

    for idx, line in enumerate(left_text):
        draw.text((178, 86 + idx * 26), line, font=list_font, fill="#494949")
    for idx, line in enumerate(right_text):
        draw.text((510, 86 + idx * 26), line, font=list_font, fill="#494949")

    draw_arrow(draw, (112, 118), (420, 390))
    draw_arrow(draw, (748, 118), (440, 390))

    img.save(OUTPUT_PNG)
    print(f"Use case diagram written to: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
