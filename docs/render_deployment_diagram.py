from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "deployment-diagram.png"

WIDTH = 2500
HEIGHT = 1650
BG = "#f6f7fb"
TEXT = "#162033"
MUTED = "#516078"
HOST_FILL = "#e9eefb"
CLIENT_FILL = "#eef8ef"
PY_FILL = "#ffffff"
STORE_FILL = "#fff5e8"
CLOUD_FILL = "#eaf7fb"
NODE_OUTLINE = "#6f7f99"
ARROW = "#4c5870"
LABEL_BG = "#ffffff"
LABEL_OUTLINE = "#d5dce8"


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
                "C:/Windows/Fonts/segoeuib.ttf",
            ]
        )
    candidates.extend(
        [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = load_font(48, bold=True)
SECTION_FONT = load_font(30, bold=True)
LABEL_FONT = load_font(23, bold=True)
TEXT_FONT = load_font(19)
SMALL_FONT = load_font(17)


def rounded_box(draw, box, fill, outline=NODE_OUTLINE, radius=24, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, box, text, font, fill=TEXT, spacing=6):
    left, top, right, bottom = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = left + (right - left - text_w) / 2
    y = top + (bottom - top - text_h) / 2
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing, align="center")


def top_left_text(draw, xy, text, font, fill=TEXT, spacing=5):
    draw.multiline_text(xy, text, font=font, fill=fill, spacing=spacing)


def line_with_arrow(draw, start, end, fill=ARROW, width=4, arrow_size=13):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux
    tip = (x2, y2)
    p1 = (x2 - ux * arrow_size - px * arrow_size * 0.7, y2 - uy * arrow_size - py * arrow_size * 0.7)
    p2 = (x2 - ux * arrow_size + px * arrow_size * 0.7, y2 - uy * arrow_size + py * arrow_size * 0.7)
    draw.polygon([tip, p1, p2], fill=fill)


def elbow_with_arrow(draw, points, fill=ARROW, width=4, arrow_size=13):
    for start, end in zip(points, points[1:-1]):
        draw.line([start, end], fill=fill, width=width)
    line_with_arrow(draw, points[-2], points[-1], fill=fill, width=width, arrow_size=arrow_size)


def label_text(draw, anchor, text, center=False):
    bbox = draw.multiline_textbbox((0, 0), text, font=SMALL_FONT, spacing=4, align="center" if center else "left")
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x, y = anchor
    if center:
        x -= w / 2 + 12
    pad_x = 12
    pad_y = 8
    draw.rounded_rectangle(
        (x, y, x + w + pad_x * 2, y + h + pad_y * 2),
        radius=12,
        fill=LABEL_BG,
        outline=LABEL_OUTLINE,
        width=2,
    )
    draw.multiline_text((x + pad_x, y + pad_y), text, font=SMALL_FONT, fill=MUTED, spacing=4, align="center" if center else "left")


img = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(img)

center_text(draw, (0, 24, WIDTH, 110), "Indian Stock AI Agent Deployment Diagram", TITLE_FONT)

# Client area
client_box = (80, 170, 600, 670)
rounded_box(draw, client_box, CLIENT_FILL)
top_left_text(draw, (110, 195), "Client Device", SECTION_FONT)

browser_box = (135, 300, 545, 435)
cli_box = (135, 485, 545, 620)
rounded_box(draw, browser_box, "#ffffff")
rounded_box(draw, cli_box, "#ffffff")
center_text(draw, browser_box, "Browser SPA\nchat.html / index.html", LABEL_FONT)
center_text(draw, cli_box, "CLI Client\npython main.py", LABEL_FONT)

# Host area
host_box = (680, 140, 1810, 1325)
rounded_box(draw, host_box, HOST_FILL)
top_left_text(draw, (720, 170), "Application Host", SECTION_FONT)
top_left_text(draw, (720, 212), "Windows / Linux VM or local machine", TEXT_FONT, fill=MUTED)

py_box = (760, 290, 1710, 980)
rounded_box(draw, py_box, PY_FILL)
top_left_text(draw, (795, 320), "Python Runtime", SECTION_FONT)

web_box = (830, 405, 1220, 565)
main_box = (1260, 405, 1640, 565)
pipeline_box = (1005, 655, 1465, 825)
agents_box = (830, 870, 1195, 955)
tools_box = (1275, 850, 1640, 980)
pdf_box = (1015, 1045, 1455, 1175)

for box in [web_box, main_box, pipeline_box, agents_box, tools_box, pdf_box]:
    rounded_box(draw, box, "#fbfcff")

center_text(draw, web_box, "Web Server\nweb_server.py\nThreadingHTTPServer :8000", LABEL_FONT)
center_text(draw, main_box, "CLI Entry Point\nmain.py", LABEL_FONT)
center_text(draw, pipeline_box, "Pipeline Orchestrator\nagents/pipeline_orchestrator.py", LABEL_FONT)
center_text(draw, agents_box, "Agent Layer\n10 specialist agents", LABEL_FONT)
center_text(draw, tools_box, "Tools Layer\nyfinance, ta, requests,\nVADER, TextBlob, BeautifulSoup", LABEL_FONT)
center_text(draw, pdf_box, "PDF Generator\npdf_generator.py", LABEL_FONT)

db_box = (800, 1215, 1100, 1295)
reports_box = (1140, 1215, 1495, 1295)
env_box = (1530, 1215, 1690, 1295)
rounded_box(draw, db_box, STORE_FILL)
rounded_box(draw, reports_box, STORE_FILL)
rounded_box(draw, env_box, STORE_FILL)
center_text(draw, db_box, "SQLite DB\napp_data.db", LABEL_FONT)
center_text(draw, reports_box, "Reports Directory\n/reports/*.pdf", LABEL_FONT)
center_text(draw, env_box, ".env", LABEL_FONT)

# External services
openai_box = (1940, 255, 2375, 390)
exa_box = (1940, 485, 2375, 620)
yahoo_box = (1940, 715, 2375, 865)
news_box = (1940, 960, 2375, 1105)
for box in [openai_box, exa_box, yahoo_box, news_box]:
    rounded_box(draw, box, CLOUD_FILL, radius=42)

center_text(draw, openai_box, "OpenAI Platform", LABEL_FONT)
center_text(draw, exa_box, "Exa MCP HTTP\nEndpoint", LABEL_FONT)
center_text(draw, yahoo_box, "Yahoo Finance / NSE-BSE Data\nvia yfinance", LABEL_FONT)
center_text(draw, news_box, "News / Web Sources\nRSS and scraped pages", LABEL_FONT)

# User line
label_text(draw, (120, 115), "End User / Admin")
line_with_arrow(draw, (210, 150), (280, 300))

# Client to runtime
elbow_with_arrow(draw, [(545, 365), (670, 365), (670, 485), (830, 485)])
label_text(draw, (600, 330), "REST / JSON")

elbow_with_arrow(draw, [(545, 550), (900, 550), (900, 520), (1260, 485)])
label_text(draw, (835, 560), "local execution")

# Internal arrows
elbow_with_arrow(draw, [(1025, 565), (1025, 620), (1120, 620), (1120, 655)])
label_text(draw, (980, 670), "run_full_analysis_with_pdf()")

elbow_with_arrow(draw, [(1450, 565), (1450, 620), (1365, 620), (1365, 655)])
label_text(draw, (1315, 670), "analyze stock query")

elbow_with_arrow(draw, [(1120, 825), (1120, 850), (1015, 850), (1015, 870)])
label_text(draw, (900, 760), "sequential execution")

elbow_with_arrow(draw, [(1350, 825), (1350, 835), (1458, 835), (1458, 850)])
label_text(draw, (1425, 760), "tool calls")

elbow_with_arrow(draw, [(1235, 825), (1235, 935), (1235, 935), (1235, 1045)])
label_text(draw, (1265, 940), "generate report")

# Storage arrows
elbow_with_arrow(draw, [(905, 565), (905, 1155), (950, 1155), (950, 1215)])
label_text(draw, (775, 1095), "users / sessions /\nchat_history / reports")

elbow_with_arrow(draw, [(1235, 1175), (1235, 1195), (1315, 1195), (1315, 1215)])
label_text(draw, (1155, 1185), "write PDF files")

elbow_with_arrow(draw, [(1035, 565), (1035, 1125), (1260, 1125), (1260, 1215)])
label_text(draw, (1065, 1110), "serve PDFs")

elbow_with_arrow(draw, [(1640, 485), (1665, 485), (1665, 1215), (1610, 1215)])
elbow_with_arrow(draw, [(1465, 740), (1600, 740), (1600, 1215), (1610, 1215)])
label_text(draw, (1490, 1005), "config / secrets")

# External arrows routed through corridor
trunk = 1780
elbow_with_arrow(draw, [(1640, 915), (trunk, 915), (trunk, 320), (1940, 320)])
label_text(draw, (1800, 225), "Agents SDK / model calls")

elbow_with_arrow(draw, [(1640, 915), (trunk, 915), (trunk, 552), (1940, 552)])
label_text(draw, (1810, 455), "live company / news research")

elbow_with_arrow(draw, [(1640, 915), (trunk, 915), (trunk, 790), (1940, 790)])
label_text(draw, (1810, 690), "market data / fundamentals")

elbow_with_arrow(draw, [(1640, 915), (trunk, 915), (trunk, 1032), (1940, 1032)])
label_text(draw, (1820, 920), "RSS / scraping fallback")

footer = (
    "Codebase basis: web_server.py, main.py, agents/pipeline_orchestrator.py, "
    "pdf_generator.py, config.py, tools/*"
)
top_left_text(draw, (82, 1588), footer, SMALL_FONT, fill=MUTED)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUTPUT)
print(OUTPUT)
