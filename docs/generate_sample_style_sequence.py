from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path(__file__).resolve().parent / "indian_stock_ai_agent_sequence_style.png"


def load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates += [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/seguisb.ttf",
        ]
    else:
        candidates += [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(26, bold=True)
FONT_HEADER = load_font(20, bold=True)
FONT_TEXT = load_font(15)


def box(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, text: str, fill: str) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline="#8b5a2b", width=1)
    draw.text((x + w / 2, y + h / 2), text, anchor="mm", font=FONT_HEADER, fill="#222222")


def arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, label: str) -> None:
    color = "#263645"
    draw.line((x1, y1, x2, y2), fill=color, width=2)
    head = 8
    if x2 >= x1:
        pts = [(x2, y2), (x2 - 12, y2 - head), (x2 - 12, y2 + head)]
    else:
        pts = [(x2, y2), (x2 + 12, y2 - head), (x2 + 12, y2 + head)]
    draw.polygon(pts, fill=color)
    draw.text(((x1 + x2) / 2, y1 - 12), label, anchor="mm", font=FONT_TEXT, fill="#333333")


def main() -> None:
    img = Image.new("RGB", (1180, 1320), "white")
    draw = ImageDraw.Draw(img)

    draw.text((18, 18), "Sequence Diagram", font=FONT_TITLE, fill="#222222")

    left_x = 110
    mid_x = 560
    right_x = 1030
    top_y = 90
    box_w = 170
    box_h = 42

    box(draw, left_x - box_w // 2, top_y, box_w, box_h, "Service Provider", "#d98b39")
    box(draw, mid_x - box_w // 2, top_y, box_w, box_h, "Web Server", "#d98b39")
    box(draw, right_x - box_w // 2, top_y, box_w, box_h, "Remote User", "#9ac25b")

    lifeline_top = top_y + box_h
    lifeline_bottom = 1260
    for x in (left_x, mid_x, right_x):
        draw.line((x, lifeline_top, x, lifeline_bottom), fill="#d24646", width=3)

    y = 190
    gap = 74

    arrow(draw, left_x, y, mid_x, y, "Start analysis query")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Forward user request")
    y += gap
    arrow(draw, right_x, y, mid_x, y, "Show progress / wait state")
    y += gap
    arrow(draw, left_x, y, mid_x, y, "Start CLI / server workflow")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Run agent pipeline")
    y += gap
    arrow(draw, right_x, y, mid_x, y, "Return data + insights")
    y += gap
    arrow(draw, left_x, y, mid_x, y, "Open dashboard / web view")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Show login / auth flow")
    y += gap
    arrow(draw, right_x, y, mid_x, y, "Submit analysis request")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Run Fundamental / Technical / News")
    y += gap
    arrow(draw, right_x, y, mid_x, y, "Agent outputs returned")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Generate report + recommendation")
    y += gap
    arrow(draw, right_x, y, mid_x, y, "Result / PDF path")
    y += gap
    arrow(draw, mid_x, y, right_x, y, "Show report / chat history")
    y += gap
    arrow(draw, left_x, y, mid_x, y, "View logs / reports")

    img.save(OUT_PATH)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
