from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent
ARCH_PNG = OUT_DIR / "indian_stock_ai_agent_architecture_flow.png"
INTERACTION_PNG = OUT_DIR / "indian_stock_ai_agent_interaction_flow.png"


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


def center_text(draw: ImageDraw.ImageDraw, box, text: str, font, fill="#24303c", line_gap: int = 3):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = []
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        heights.append(bb[3] - bb[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = (y1 + y2) / 2 - total_h / 2
    cx = (x1 + x2) / 2
    for idx, line in enumerate(lines):
        draw.text((cx, y), line, font=font, fill=fill, anchor="ma")
        y += heights[idx] + line_gap


def draw_box(draw: ImageDraw.ImageDraw, box, text: str, font, fill, outline, radius: int = 0, text_fill="#24303c"):
    if radius:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    else:
        draw.rectangle(box, fill=fill, outline=outline, width=2)
    center_text(draw, box, text, font, fill=text_fill)


def draw_cylinder(draw: ImageDraw.ImageDraw, box, text: str, font):
    x1, y1, x2, y2 = box
    rim = 14
    fill = "#f79a3b"
    outline = "#d67619"
    draw.rectangle((x1, y1 + rim // 2, x2, y2 - rim // 2), fill=fill, outline=outline, width=2)
    draw.ellipse((x1, y1, x2, y1 + rim), fill="#fbb06a", outline=outline, width=2)
    draw.ellipse((x1, y2 - rim, x2, y2), fill="#f08b2f", outline=outline, width=2)
    center_text(draw, box, text, font, fill="white")


def arrow(draw: ImageDraw.ImageDraw, start, end, color="#6b6b6b", width: int = 2, dashed: bool = False):
    if dashed:
        dash = 8
        gap = 6
        x1, y1 = start
        x2, y2 = end
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps == 0:
            return
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        on = True
        length = 0
        px, py = x1, y1
        for i in range(1, int(steps) + 1):
            cx = x1 + dx * i
            cy = y1 + dy * i
            seg = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
            length += seg
            threshold = dash if on else gap
            if length >= threshold:
                if on:
                    draw.line((px, py, cx, cy), fill=color, width=width)
                on = not on
                length = 0
            px, py = cx, cy
        if on:
            draw.line((px, py, x2, y2), fill=color, width=width)
    else:
        draw.line((start, end), fill=color, width=width)
    draw_arrowhead(draw, end, start, color)


def draw_arrowhead(draw: ImageDraw.ImageDraw, tip, prev, color):
    x2, y2 = tip
    x1, y1 = prev
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 12, y2 - 6), (x2 - 12, y2 + 6)]
        else:
            pts = [(x2, y2), (x2 + 12, y2 - 6), (x2 + 12, y2 + 6)]
    else:
        if y2 >= y1:
            pts = [(x2, y2), (x2 - 6, y2 - 12), (x2 + 6, y2 - 12)]
        else:
            pts = [(x2, y2), (x2 - 6, y2 + 12), (x2 + 6, y2 + 12)]
    draw.polygon(pts, fill=color)


def edge_point(box, side: str):
    x1, y1, x2, y2 = box
    if side == "left":
        return x1, (y1 + y2) // 2
    if side == "right":
        return x2, (y1 + y2) // 2
    if side == "top":
        return (x1 + x2) // 2, y1
    return (x1 + x2) // 2, y2


def architecture_flow():
    img = Image.new("RGB", (920, 920), "white")
    draw = ImageDraw.Draw(img)
    title_font = load_font(20, True)
    box_font = load_font(15, True)
    body_font = load_font(14, False)
    small_font = load_font(12, False)

    draw.text((18, 18), "Architecture Flow Diagram", font=title_font, fill="#24303c")

    web_box = (28, 112, 170, 160)
    db_box = (36, 488, 150, 668)
    provider_panel = (514, 38, 892, 602)
    remote_box = (540, 666, 688, 710)

    draw_box(draw, web_box, "Web Server", box_font, "#8462b1", "#6d4b99", text_fill="white")
    draw_cylinder(draw, db_box, "WEB\nDatabase", box_font)
    draw_box(draw, remote_box, "Remote User", box_font, "#121212", "#111111", text_fill="white")
    draw.rounded_rectangle(provider_panel, radius=28, fill="#d68c91", outline="#ba5c60", width=2)
    draw.rectangle((540, 66, 564, 572), fill="white")
    draw.rectangle((842, 66, 866, 572), fill="white")
    draw.text((702, 68), "Service Provider", font=box_font, fill="#b63438", anchor="ma")

    provider_lines = [
        "Admin login,",
        "Upload and manage stock queries,",
        "Create analysis jobs and report workflows,",
        "View branch / sector analytics,",
        "View item analysis results,",
        "View stock comparison reports,",
        "Export reports and audit records,",
        "View all users and report history.",
    ]
    y = 112
    for line in provider_lines:
        draw.text((560, y), line, font=body_font, fill="#7d1f24")
        y += 58

    arrow(draw, (170, 136), (514, 136), color="#54b9c3", dashed=True)
    draw.text((248, 118), "Accepting all information", font=small_font, fill="#4f6a6d")
    arrow(draw, (514, 178), (170, 178), color="#54b9c3", dashed=True)
    draw.text((306, 160), "Results / Data Storage", font=small_font, fill="#4f6a6d")

    arrow(draw, (98, 488), (98, 160), color="#505050")
    arrow(draw, (78, 160), (78, 488), color="#505050")
    draw.text((6, 320), "Accessing\nData", font=small_font, fill="#555555")
    draw.text((132, 380), "Process all\nuser queries", font=small_font, fill="#555555")

    arrow(draw, (514, 516), (152, 608), color="#6ec7d4", dashed=True)
    draw.text((412, 570), "Store and retrievals", font=box_font, fill="#ca3436", anchor="ma")
    arrow(draw, (616, 602), (614, 666), color="#e69d54", dashed=True)

    draw.text((516, 786), "REGISTER AND LOGIN", font=small_font, fill="#666666")
    draw.text((516, 828), "SUBMIT STOCK QUERY", font=small_font, fill="#666666")
    draw.text((516, 870), "VIEW RESULT AND PROFILE", font=small_font, fill="#666666")

    img.save(ARCH_PNG)


def interaction_flow():
    img = Image.new("RGB", (980, 620), "white")
    draw = ImageDraw.Draw(img)
    title_font = load_font(18, True)
    box_font = load_font(12, True)
    small_font = load_font(11, False)

    draw.text((18, 18), "Interaction Flow Diagram", font=title_font, fill="#24303c")

    provider = (20, 170, 112, 198)
    remote = (432, 528, 554, 556)
    system = (446, 166, 552, 206)

    top_oval = (344, 34, 872, 116)
    left_login = (182, 168, 362, 236)
    left_big = (54, 246, 422, 420)
    left_bottom = (42, 458, 474, 566)
    right_top = (672, 168, 946, 252)
    center_right = (554, 328, 796, 436)
    right_profile = (796, 340, 962, 432)

    draw_box(draw, provider, "Service Provider", small_font, "#8160ad", "#6d4b99", text_fill="white")
    draw_box(draw, remote, "Remote User", small_font, "#8160ad", "#6d4b99", text_fill="white")
    draw_box(draw, system, "System", box_font, "#6f689b", "#5e5789", text_fill="white")

    ovals = [
        (top_oval, "Admin Login, Upload and Manage Study\nMaterials, Create Quiz and Schedule\nAssessment, View Branch and Section\nAnalytics, View Item Analysis Results.", "#b7db70"),
        (left_login, "Login", "#b7db70"),
        (left_big, "View Quiz Comparison\nReports, Export Attempts and\nMaterials, View Student and\nQuiz Records.", "#6fd3e5"),
        (left_bottom, "View Personal Analytics, View\nResults and AI Explanations, View\nAll Assigned Queries.", "#6fd3e5"),
        (right_top, "ATTEMPT QUIZ AND SUBMIT\nRESPONSES", "#b7db70"),
        (center_right, "Register and Login\nwith the System", "#b7db70"),
        (right_profile, "VIEW YOUR PROFILE", "#b7db70"),
    ]

    for box, text, fill in ovals:
        draw.ellipse(box, fill=fill, outline="#c65c63", width=2)
        center_text(draw, box, text, small_font)

    arrow(draw, edge_point(provider, "right"), edge_point(left_login, "left"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(provider, "right"), edge_point(left_big, "left"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(provider, "right"), edge_point(top_oval, "left"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(left_big, "bottom"), edge_point(left_bottom, "top"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(left_login, "right"), edge_point(system, "left"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(system, "top"), edge_point(top_oval, "bottom"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(left_bottom, "right"), edge_point(remote, "left"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(system, "right"), edge_point(right_top, "left"), color="#8d8d8d", dashed=True)
    arrow(draw, edge_point(system, "bottom"), edge_point(center_right, "top"), color="#8bcfe3", dashed=True)
    arrow(draw, edge_point(system, "bottom"), edge_point(right_profile, "left"), color="#8d8d8d", dashed=True)
    arrow(draw, edge_point(center_right, "right"), edge_point(right_profile, "left"), color="#8d8d8d", dashed=True)
    arrow(draw, edge_point(right_top, "bottom"), edge_point(right_profile, "top"), color="#8d8d8d", dashed=True)
    arrow(draw, edge_point(right_profile, "bottom"), edge_point(remote, "right"), color="#8d8d8d", dashed=True)

    draw.text((800, 286), "Response", font=small_font, fill="#555555")
    draw.text((548, 470), "Request", font=small_font, fill="#555555")

    img.save(INTERACTION_PNG)


def main() -> None:
    architecture_flow()
    interaction_flow()
    print(f"Wrote: {ARCH_PNG}")
    print(f"Wrote: {INTERACTION_PNG}")


if __name__ == "__main__":
    main()
