from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent
COMPONENT_PNG = OUT_DIR / "indian_stock_ai_agent_component_diagram.png"
COMPONENT_3D_PNG = OUT_DIR / "indian_stock_ai_agent_component_diagram_3d.png"

BG = "white"
BOX_FILL = "#fff2a8"
BOX_OUTLINE = "#c9b14a"
LINE = "#8e7b7b"
TEXT = "#24303c"


@dataclass
class Node:
    label: str
    box: tuple[int, int, int, int]


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


def draw_box(draw: ImageDraw.ImageDraw, node: Node, font):
    draw.rectangle(node.box, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    draw_center_text(draw, node.box, node.label, font)


def draw_3d_box(draw: ImageDraw.ImageDraw, node: Node, font, depth: int = 10):
    x1, y1, x2, y2 = node.box
    top = [(x1, y1), (x2, y1), (x2 + depth, y1 - depth), (x1 + depth, y1 - depth)]
    side = [(x2, y1), (x2 + depth, y1 - depth), (x2 + depth, y2 - depth), (x2, y2)]
    back = (x1 + depth, y1 - depth, x2 + depth, y2 - depth)
    draw.polygon(top, fill="#fff9d6", outline=BOX_OUTLINE)
    draw.rectangle(back, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    draw.polygon(side, fill="#e0cf76", outline=BOX_OUTLINE)
    draw.rectangle(node.box, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    draw_center_text(draw, node.box, node.label, font)


def anchor(box, side: str):
    x1, y1, x2, y2 = box
    if side == "left":
        return x1, (y1 + y2) // 2
    if side == "right":
        return x2, (y1 + y2) // 2
    if side == "top":
        return (x1 + x2) // 2, y1
    return (x1 + x2) // 2, y2


def draw_orthogonal(draw: ImageDraw.ImageDraw, start, end, color=LINE, width: int = 2):
    x1, y1 = start
    x2, y2 = end
    mid_x = (x1 + x2) // 2
    points = [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]
    draw.line(points, fill=color, width=width)
    if abs(points[-1][0] - points[-2][0]) >= abs(points[-1][1] - points[-2][1]):
        direction = "right" if points[-1][0] > points[-2][0] else "left"
    else:
        direction = "down" if points[-1][1] > points[-2][1] else "up"
    draw_arrowhead(draw, points[-1], direction, color)


def draw_arrowhead(draw: ImageDraw.ImageDraw, tip, direction: str, color=LINE):
    x, y = tip
    if direction == "right":
        pts = [(x, y), (x - 11, y - 6), (x - 11, y + 6)]
    elif direction == "left":
        pts = [(x, y), (x + 11, y - 6), (x + 11, y + 6)]
    elif direction == "up":
        pts = [(x, y), (x - 6, y + 11), (x + 6, y + 11)]
    else:
        pts = [(x, y), (x - 6, y - 11), (x + 6, y - 11)]
    draw.polygon(pts, fill=color)


def build_nodes():
    app = Node("Application", (458, 28, 534, 60))
    provider = Node("Provider", (86, 214, 156, 248))
    external = Node("External\nUser", (822, 214, 898, 248))

    left = [
        Node("Admin Login", (24, 96, 118, 132)),
        Node("Manage\nMaterials", (20, 162, 116, 204)),
        Node("Analytics\nDashboard", (22, 274, 118, 316)),
        Node("Item\nAnalysis", (52, 378, 148, 420)),
        Node("Create Quiz", (246, 158, 344, 194)),
        Node("Quiz\nScheduling", (246, 244, 344, 286)),
        Node("Export\nReports", (246, 334, 344, 376)),
        Node("AI Admin\nChat", (366, 334, 466, 376)),
        Node("View All\nUsers", (234, 438, 336, 480)),
    ]

    right = [
        Node("Register and\nLogin", (644, 158, 748, 198)),
        Node("Student\nDashboard", (664, 240, 768, 282)),
        Node("View Profile", (786, 240, 884, 282)),
        Node("Attempt Quiz", (842, 336, 940, 376)),
        Node("View Result", (660, 382, 758, 422)),
        Node("AI\nExplanation", (828, 430, 928, 470)),
        Node("Personal\nAnalytics", (668, 486, 776, 528)),
    ]
    return app, provider, external, left, right


def draw_component_diagram(path: Path, is_3d: bool = False):
    width, height = 980, 620
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    title_font = load_font(18, bold=True)
    box_font = load_font(11, bold=False)

    draw.text((20, 16), "3D Component Diagram" if is_3d else "Component Diagram", font=title_font, fill=TEXT)

    app, provider, external, left, right = build_nodes()
    drawer = draw_3d_box if is_3d else draw_box

    drawer(draw, app, box_font)
    drawer(draw, provider, box_font)
    drawer(draw, external, box_font)
    for node in left + right:
        drawer(draw, node, box_font)

    draw_orthogonal(draw, anchor(app.box, "bottom"), anchor(provider.box, "top"))
    draw_orthogonal(draw, anchor(app.box, "bottom"), anchor(external.box, "top"))

    left_hub = (204, 248)
    right_hub = (792, 248)
    draw.line([anchor(provider.box, "right"), left_hub], fill=LINE, width=2)
    draw.line([anchor(external.box, "left"), right_hub], fill=LINE, width=2)

    left_targets = [
        (left[0], "right"),
        (left[1], "right"),
        (left[2], "right"),
        (left[3], "right"),
        (left[4], "left"),
        (left[5], "left"),
        (left[6], "left"),
        (left[7], "left"),
        (left[8], "top"),
    ]
    for node, target_side in left_targets:
        draw_orthogonal(draw, left_hub, anchor(node.box, target_side))

    right_targets = [
        (right[0], "right"),
        (right[1], "top"),
        (right[2], "top"),
        (right[3], "left"),
        (right[4], "top"),
        (right[5], "left"),
        (right[6], "top"),
    ]
    for node, target_side in right_targets:
        draw_orthogonal(draw, right_hub, anchor(node.box, target_side))

    img.save(path)


def main() -> None:
    draw_component_diagram(COMPONENT_PNG, is_3d=False)
    draw_component_diagram(COMPONENT_3D_PNG, is_3d=True)
    print(f"Wrote: {COMPONENT_PNG}")
    print(f"Wrote: {COMPONENT_3D_PNG}")


if __name__ == "__main__":
    main()
