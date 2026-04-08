from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


OUTPUT_SVG = Path(__file__).resolve().parent / "indian_stock_ai_agent_use_case_diagram.svg"
OUTPUT_PNG = Path(__file__).resolve().parent / "indian_stock_ai_agent_use_case_diagram.png"


@dataclass
class UseCase:
    title: str
    x: int
    y: int
    w: int
    h: int
    fill: str
    stroke: str
    text_color: str = "#2a3b4c"


@dataclass
class Link:
    src: str
    dst: str
    src_side: str = "right"
    dst_side: str = "left"
    color: str = "#99a8b4"
    mid_x: int | None = None
    mid_y: int | None = None


def oval_anchor(node: UseCase, side: str) -> tuple[int, int]:
    if side == "top":
        return node.x + node.w // 2, node.y
    if side == "bottom":
        return node.x + node.w // 2, node.y + node.h
    if side == "left":
        return node.x, node.y + node.h // 2
    if side == "right":
        return node.x + node.w, node.y + node.h // 2
    raise ValueError(side)


def line_path(src: tuple[int, int], dst: tuple[int, int], mid_x: int | None, mid_y: int | None) -> str:
    x1, y1 = src
    x2, y2 = dst
    if mid_x is not None:
        return f"M {x1},{y1} L {mid_x},{y1} L {mid_x},{y2} L {x2},{y2}"
    if mid_y is not None:
        return f"M {x1},{y1} L {x1},{mid_y} L {x2},{mid_y} L {x2},{y2}"
    if abs(x1 - x2) > abs(y1 - y2):
        mid_x = (x1 + x2) // 2
        return f"M {x1},{y1} L {mid_x},{y1} L {mid_x},{y2} L {x2},{y2}"
    mid_y = (y1 + y2) // 2
    return f"M {x1},{y1} L {x1},{mid_y} L {x2},{mid_y} L {x2},{y2}"


def render_use_case(node: UseCase) -> str:
    lines = wrap(node.title, width=max(22, node.w // 8)) or [node.title]
    text_start_y = node.y + 20 - (len(lines) - 1) * 7
    text = []
    for idx, line in enumerate(lines):
        y = text_start_y + idx * 16
        text.append(
            f'<text x="{node.x + node.w / 2}" y="{y}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="{node.text_color}">{escape(line)}</text>'
        )
    return "\n".join(
        [
            f'<ellipse cx="{node.x + node.w / 2}" cy="{node.y + node.h / 2}" rx="{node.w / 2}" ry="{node.h / 2}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"/>',
            *text,
        ]
    )


def render_actor(x: int, y: int, label: str, color: str = "#5c6773") -> str:
    head = f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="2"/>'
    body = f'<line x1="{x}" y1="{y + 9}" x2="{x}" y2="{y + 42}" stroke="{color}" stroke-width="2"/>'
    arms = f'<line x1="{x - 16}" y1="{y + 22}" x2="{x + 16}" y2="{y + 22}" stroke="{color}" stroke-width="2"/>'
    left_leg = f'<line x1="{x}" y1="{y + 42}" x2="{x - 13}" y2="{y + 65}" stroke="{color}" stroke-width="2"/>'
    right_leg = f'<line x1="{x}" y1="{y + 42}" x2="{x + 13}" y2="{y + 65}" stroke="{color}" stroke-width="2"/>'
    label_node = f'<text x="{x}" y="{y - 14}" text-anchor="middle" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="15" fill="{color}">{escape(label)}</text>'
    return "\n".join([label_node, head, body, arms, left_leg, right_leg])


def render_link(src: UseCase | tuple[int, int], dst: UseCase | tuple[int, int], link: Link | None = None) -> str:
    if isinstance(src, UseCase):
        assert link is not None
        x1, y1 = oval_anchor(src, link.src_side)
        if isinstance(dst, UseCase):
            x2, y2 = oval_anchor(dst, link.dst_side)
        else:
            x2, y2 = dst
        d = line_path((x1, y1), (x2, y2), link.mid_x, link.mid_y)
        color = link.color
    else:
        x1, y1 = src
        if isinstance(dst, UseCase):
            side = "left" if x1 < dst.x + dst.w / 2 else "right"
            x2, y2 = oval_anchor(dst, side)
        else:
            x2, y2 = dst
        d = line_path((x1, y1), (x2, y2), None, None)
        color = "#99a8b4"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" stroke-dasharray="7 6" marker-end="url(#arrow)"/>'


def build_diagram() -> str:
    cases = {
        "upload": UseCase("Browse and Upload Stock Query / Portfolio", 178, 26, 420, 42, "#9eddea", "#9a79a7"),
        "dashboard": UseCase("View Live Analysis Dashboard", 132, 118, 512, 42, "#cde86b", "#9a79a7"),
        "status": UseCase("View Job Status and Saved Reports", 420, 196, 330, 48, "#d8b3eb", "#8f6aa7"),
        "login": UseCase("Register and Login", 150, 276, 360, 42, "#cde86b", "#9a79a7"),
        "job": UseCase("Create Async Analysis Job", 172, 370, 414, 44, "#9eddea", "#9a79a7"),
        "profile": UseCase("View Profile / API Key Status", 198, 462, 220, 42, "#cde86b", "#9a79a7"),
        "analyze": UseCase("Run Stock Analysis and Predict Performance", 160, 550, 482, 44, "#9eddea", "#9a79a7"),
        "results": UseCase("View Results, AI Explanation, and Price Levels", 152, 646, 500, 42, "#cde86b", "#9a79a7"),
        "download": UseCase("Download PDF Reports and Chat History", 166, 742, 430, 44, "#d8b3eb", "#8f6aa7"),
        "compare": UseCase("Compare Stocks, View Trends, and Admin Stats", 132, 842, 520, 44, "#cde86b", "#9a79a7"),
    }

    links: list[tuple[tuple[int, int] | UseCase, tuple[int, int] | UseCase, Link | None]] = [
        ((70, 802), cases["upload"], None),
        ((70, 802), cases["dashboard"], None),
        ((70, 802), cases["login"], None),
        ((70, 802), cases["job"], None),
        ((70, 802), cases["profile"], None),
        ((70, 802), cases["analyze"], None),
        ((70, 802), cases["results"], None),
        ((70, 802), cases["download"], None),
        ((70, 802), cases["compare"], None),
        ((734, 802), cases["status"], None),
        ((734, 802), cases["analyze"], None),
        ((734, 802), cases["results"], None),
        ((734, 802), cases["download"], None),
        ((734, 802), cases["compare"], None),
        (cases["upload"], cases["dashboard"], Link("upload", "dashboard", src_side="bottom", dst_side="top", mid_x=344)),
        (cases["dashboard"], cases["login"], Link("dashboard", "login", src_side="bottom", dst_side="top", mid_x=388)),
        (cases["login"], cases["job"], Link("login", "job", src_side="bottom", dst_side="top", mid_x=342)),
        (cases["job"], cases["profile"], Link("job", "profile", src_side="bottom", dst_side="top", mid_x=322)),
        (cases["profile"], cases["analyze"], Link("profile", "analyze", src_side="bottom", dst_side="top", mid_x=312)),
        (cases["analyze"], cases["results"], Link("analyze", "results", src_side="bottom", dst_side="top", mid_x=401)),
        (cases["results"], cases["download"], Link("results", "download", src_side="bottom", dst_side="top", mid_x=356)),
        (cases["download"], cases["compare"], Link("download", "compare", src_side="bottom", dst_side="top", mid_x=332)),
    ]

    group_boxes = [
        ('<rect x="20" y="18" width="700" height="270" rx="22" ry="22" fill="none" stroke="#b1bfce" stroke-width="2" stroke-dasharray="10 8"/>'),
        ('<rect x="20" y="310" width="700" height="210" rx="22" ry="22" fill="none" stroke="#b1bfce" stroke-width="2" stroke-dasharray="10 8"/>'),
        ('<rect x="20" y="540" width="700" height="370" rx="22" ry="22" fill="none" stroke="#b1bfce" stroke-width="2" stroke-dasharray="10 8"/>'),
    ]

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="780" height="920" viewBox="0 0 780 920">',
        "<defs>",
        '<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
        '<stop offset="0%" stop-color="#ffffff"/>',
        '<stop offset="100%" stop-color="#f4f8fc"/>',
        "</linearGradient>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">',
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#9aa8b5"/>',
        "</marker>",
        "</defs>",
        '<rect x="0" y="0" width="780" height="920" fill="url(#bg)"/>',
        '<text x="18" y="26" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="18" fill="#1f2e3a">Use Case</text>',
        *group_boxes,
        '<text x="28" y="298" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="14" fill="#4e5f71">Application</text>',
        '<text x="28" y="318" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="14" fill="#4e5f71">Access + Auth</text>',
        '<text x="28" y="530" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="14" fill="#4e5f71">Core Analysis Flow</text>',
        '<text x="28" y="544" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="14" fill="#4e5f71">and Report Output</text>',
        render_actor(30, 792, "Platform Admin"),
        render_actor(728, 792, "Remote User"),
    ]

    for src, dst, link in links:
        svg.append(render_link(src, dst, link))

    for node in cases.values():
        svg.append(render_use_case(node))

    svg.append(
        '<text x="390" y="902" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#6d7a87">'
        "Indian Stock AI Agent use case diagram"
        "</text>"
    )
    svg.append("</svg>")
    return "\n".join(svg)


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = []
    if bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/seguisb.ttf",
                "C:/Windows/Fonts/segoeuib.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]
        )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_png() -> None:
    from PIL import Image, ImageDraw

    width = 1560
    height = 1840
    img = Image.new("RGBA", (width, height), (245, 249, 253, 255))
    draw = ImageDraw.Draw(img)

    title_font = load_font(30, bold=True)
    group_font = load_font(18, bold=True)
    label_font = load_font(15, bold=True)
    node_font = load_font(13)

    draw.rectangle((0, 0, width, height), fill=(245, 249, 253, 255))
    draw.text((26, 18), "Use Case", font=title_font, fill=(31, 46, 58, 255))

    for box in [(20, 18, 1460, 288), (20, 310, 1460, 520), (20, 540, 1460, 910)]:
        draw.rounded_rectangle(box, radius=24, outline=(177, 191, 206, 255), width=2)

    draw.text((28, 292), "Application", font=group_font, fill=(78, 95, 113, 255))
    draw.text((28, 312), "Access + Auth", font=group_font, fill=(78, 95, 113, 255))
    draw.text((28, 522), "Core Analysis Flow", font=group_font, fill=(78, 95, 113, 255))
    draw.text((28, 542), "and Report Output", font=group_font, fill=(78, 95, 113, 255))

    def actor(x: int, y: int, name: str):
        draw.text((x, y - 14), name, font=label_font, fill=(92, 103, 115, 255), anchor="ma")
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(92, 103, 115, 255), width=2)
        draw.line((x, y + 9, x, y + 42), fill=(92, 103, 115, 255), width=2)
        draw.line((x - 16, y + 22, x + 16, y + 22), fill=(92, 103, 115, 255), width=2)
        draw.line((x, y + 42, x - 13, y + 65), fill=(92, 103, 115, 255), width=2)
        draw.line((x, y + 42, x + 13, y + 65), fill=(92, 103, 115, 255), width=2)

    actor(30, 792, "Platform Admin")
    actor(728, 792, "Remote User")

    cases = {
        "upload": UseCase("Browse and Upload Stock Query / Portfolio", 178, 26, 420, 42, "#9eddea", "#9a79a7"),
        "dashboard": UseCase("View Live Analysis Dashboard", 132, 118, 512, 42, "#cde86b", "#9a79a7"),
        "status": UseCase("View Job Status and Saved Reports", 420, 196, 330, 48, "#d8b3eb", "#8f6aa7"),
        "login": UseCase("Register and Login", 150, 276, 360, 42, "#cde86b", "#9a79a7"),
        "job": UseCase("Create Async Analysis Job", 172, 370, 414, 44, "#9eddea", "#9a79a7"),
        "profile": UseCase("View Profile / API Key Status", 198, 462, 220, 42, "#cde86b", "#9a79a7"),
        "analyze": UseCase("Run Stock Analysis and Predict Performance", 160, 550, 482, 44, "#9eddea", "#9a79a7"),
        "results": UseCase("View Results, AI Explanation, and Price Levels", 152, 646, 500, 42, "#cde86b", "#9a79a7"),
        "download": UseCase("Download PDF Reports and Chat History", 166, 742, 430, 44, "#d8b3eb", "#8f6aa7"),
        "compare": UseCase("Compare Stocks, View Trends, and Admin Stats", 132, 842, 520, 44, "#cde86b", "#9a79a7"),
    }

    links = [
        ((70, 802), cases["upload"]),
        ((70, 802), cases["dashboard"]),
        ((70, 802), cases["login"]),
        ((70, 802), cases["job"]),
        ((70, 802), cases["profile"]),
        ((70, 802), cases["analyze"]),
        ((70, 802), cases["results"]),
        ((70, 802), cases["download"]),
        ((70, 802), cases["compare"]),
        ((734, 802), cases["status"]),
        ((734, 802), cases["analyze"]),
        ((734, 802), cases["results"]),
        ((734, 802), cases["download"]),
        ((734, 802), cases["compare"]),
    ]

    def draw_use_case(node: UseCase):
        cx = node.x + node.w / 2
        cy = node.y + node.h / 2
        bbox = (node.x, node.y, node.x + node.w, node.y + node.h)
        draw.ellipse(bbox, fill=node.fill, outline=node.stroke, width=2)
        lines = wrap(node.title, width=max(22, node.w // 8)) or [node.title]
        text_y = cy - (len(lines) - 1) * 8
        for i, line in enumerate(lines):
            draw.text((cx, text_y + i * 16), line, font=node_font, fill=node.text_color, anchor="ma")

    def connect(src: tuple[int, int], node: UseCase):
        x1, y1 = src
        side = "left" if x1 < node.x + node.w / 2 else "right"
        if side == "left":
            x2 = node.x
        else:
            x2 = node.x + node.w
        y2 = node.y + node.h / 2
        mid_x = (x1 + x2) // 2
        draw.line((x1, y1, x1, y2), fill=(154, 168, 181, 255), width=3)
        draw.line((x1, y2, x2, y2), fill=(154, 168, 181, 255), width=3)
        draw.polygon([(x2, y2), (x2 - 10 if side == "right" else x2 + 10, y2 - 6), (x2 - 10 if side == "right" else x2 + 10, y2 + 6)], fill=(154, 168, 181, 255))

    for src, node in links:
        connect(src, node)

    for node in cases.values():
        draw_use_case(node)

    draw.text((780, 1806), "Indian Stock AI Agent use case diagram", font=node_font, fill=(109, 122, 135, 255), anchor="ma")
    img.save(OUTPUT_PNG)


def main() -> None:
    OUTPUT_SVG.write_text(build_diagram(), encoding="utf-8")
    render_png()
    print(f"Use case diagram written to: {OUTPUT_SVG}")
    print(f"Use case diagram written to: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
