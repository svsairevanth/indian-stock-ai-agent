from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path(__file__).resolve().parent / "indian_stock_ai_agent_3d_component_v2.png"


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


FONT_TITLE = load_font(24, bold=True)
FONT_HEAD = load_font(16, bold=True)
FONT_TEXT = load_font(14)


@dataclass
class Node:
    text: str
    x: int
    y: int
    w: int = 86
    h: int = 48
    fill: str = "#fff3a8"
    edge: str = "#bcae58"
    three_d: bool = False


def draw_box(draw: ImageDraw.ImageDraw, node: Node):
    x, y, w, h = node.x, node.y, node.w, node.h
    if node.three_d:
        side = 10
        top_pts = [(x, y), (x + side, y - side), (x + w + side, y - side), (x + w, y)]
        side_pts = [(x + w, y), (x + w + side, y - side), (x + w + side, y + h - side), (x + w, y + h)]
        draw.polygon(top_pts, fill="#f4eef0", outline="#9b8f96")
        draw.polygon(side_pts, fill="#8d7f86", outline="#7a6c72")
        draw.rectangle((x, y, x + w, y + h), fill="#ffffff", outline="#9b8f96", width=1)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=node.fill, outline=node.edge, width=1)

    lines = node.text.split("\n")
    total_h = len(lines) * 15
    cy = y + (h - total_h) / 2 + 1
    for line in lines:
        draw.text((x + w / 2, cy), line, anchor="ma", font=FONT_TEXT, fill="#333333")
        cy += 15


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#9b8f96"):
    draw.line((start, end), fill=color, width=2)
    x1, y1 = start
    x2, y2 = end
    size = 7
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 12, y2 - size), (x2 - 12, y2 + size)]
        else:
            pts = [(x2, y2), (x2 + 12, y2 - size), (x2 + 12, y2 + size)]
    else:
        if y2 >= y1:
            pts = [(x2, y2), (x2 - size, y2 - 12), (x2 + size, y2 - 12)]
        else:
            pts = [(x2, y2), (x2 - size, y2 + 12), (x2 + size, y2 + 12)]
    draw.polygon(pts, fill=color)


def main():
    img = Image.new("RGB", (1320, 820), "white")
    draw = ImageDraw.Draw(img)

    draw.text((18, 18), "3D Component Diagram", font=FONT_TITLE, fill="#111111")

    app = Node("Indian Stock\nAI Agent", 620, 80, w=110, h=60, three_d=True)
    left_core = Node("Entry /\nInterface", 210, 270, w=110, h=60, three_d=True)
    right_core = Node("Pipeline\nOrchestrator", 980, 270, w=120, h=60, three_d=True)

    left_items = [
        Node("main.py", 40, 120),
        Node("agent.py", 40, 200),
        Node("web_server.py", 40, 280),
        Node("chat.html", 40, 360),
        Node("openai_sdk.py", 40, 440),
        Node("app_data.db", 180, 560),
        Node("Auth APIs", 260, 170),
        Node("Chat / Reports", 260, 260),
    ]

    right_items = [
        Node("fundamental_\nanalyst.py", 830, 300),
        Node("technical_\nanalyst.py", 830, 390),
        Node("sentiment_\nanalyst.py", 830, 480),
        Node("news_intelligence_\nagent.py", 830, 570),
        Node("macro_\nanalyst.py", 1115, 300),
        Node("document_\nanalyst.py", 1115, 390),
        Node("bull / bear /\njudge", 1115, 480),
        Node("risk_manager.py\nportfolio_analyst.py", 1115, 570),
        Node("tools/*\nstock/news/risk", 960, 150),
        Node("pdf_generator.py", 1180, 665),
        Node("models/\nschemas.py", 980, 665),
    ]

    for node in [app, left_core, right_core, *left_items, *right_items]:
        draw_box(draw, node)

    # App to main components
    arrow(draw, (670, 140), (265, 270))
    arrow(draw, (705, 140), (1040, 270))

    # Left cluster
    left_center = (left_core.x, left_core.y + left_core.h // 2)
    for item in left_items[:5]:
        arrow(draw, (item.x + item.w, item.y + item.h // 2), left_center)
    arrow(draw, left_center, (260, 194))
    arrow(draw, left_center, (260, 284))
    arrow(draw, left_center, (180, 584))

    # Right cluster
    right_center = (right_core.x + right_core.w, right_core.y + right_core.h // 2)
    arrow(draw, (1040, 270), (1003, 174))
    for item in right_items:
        if item.text == "tools/*\nstock/news/risk":
            continue
        arrow(draw, right_center, (item.x, item.y + item.h // 2))

    # tool hub into orchestrator and PDF/model modules
    arrow(draw, (1003, 198), (1040, 270))
    arrow(draw, (1003, 198), (890, 324))
    arrow(draw, (1003, 198), (890, 414))
    arrow(draw, (1003, 198), (890, 504))
    arrow(draw, (1003, 198), (890, 594))
    arrow(draw, (1003, 198), (1115, 324))
    arrow(draw, (1003, 198), (1115, 414))
    arrow(draw, (1003, 198), (1115, 504))
    arrow(draw, (1003, 198), (1115, 594))
    arrow(draw, (1040, 330), (980, 689))
    arrow(draw, (1100, 330), (1180, 689))

    img.save(OUT_PATH)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
