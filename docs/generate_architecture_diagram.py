from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


OUTPUT_SVG = Path(__file__).resolve().parent / "indian_stock_ai_agent_architecture.svg"
OUTPUT_PNG = Path(__file__).resolve().parent / "indian_stock_ai_agent_architecture.png"


@dataclass
class Node:
    key: str
    title: str
    x: int
    y: int
    w: int
    h: int
    fill: str
    stroke: str = "#23405f"
    lines: list[str] = field(default_factory=list)
    title_fill: str = "#153047"
    title_color: str = "#ffffff"
    body_color: str = "#12263a"


@dataclass
class Edge:
    src: str
    dst: str
    color: str = "#6c7a89"
    label: str = ""
    src_side: str = "bottom"
    dst_side: str = "top"
    mid_x: int | None = None
    mid_y: int | None = None


def anchor(node: Node, side: str) -> tuple[int, int]:
    if side == "top":
        return node.x + node.w // 2, node.y
    if side == "bottom":
        return node.x + node.w // 2, node.y + node.h
    if side == "left":
        return node.x, node.y + node.h // 2
    if side == "right":
        return node.x + node.w, node.y + node.h // 2
    raise ValueError(f"Unsupported side: {side}")


def edge_path(edge: Edge, nodes: dict[str, Node]) -> str:
    src = nodes[edge.src]
    dst = nodes[edge.dst]
    x1, y1 = anchor(src, edge.src_side)
    x2, y2 = anchor(dst, edge.dst_side)

    if edge.mid_x is not None:
        return f"M {x1},{y1} L {edge.mid_x},{y1} L {edge.mid_x},{y2} L {x2},{y2}"
    if edge.mid_y is not None:
        return f"M {x1},{y1} L {x1},{edge.mid_y} L {x2},{edge.mid_y} L {x2},{y2}"

    if edge.src_side in {"top", "bottom"} and edge.dst_side in {"top", "bottom"}:
        mid_y = (y1 + y2) // 2
        return f"M {x1},{y1} L {x1},{mid_y} L {x2},{mid_y} L {x2},{y2}"

    if edge.src_side in {"left", "right"} and edge.dst_side in {"left", "right"}:
        mid_x = (x1 + x2) // 2
        return f"M {x1},{y1} L {mid_x},{y1} L {mid_x},{y2} L {x2},{y2}"

    return f"M {x1},{y1} L {x2},{y2}"


def render_node(node: Node) -> str:
    title_h = 34
    body_y = node.y + title_h
    body_h = node.h - title_h
    text_y = body_y + 24

    body_lines: list[str] = []
    for raw in node.lines:
        body_lines.extend(wrap(raw, width=max(28, node.w // 8)) or [""])

    body_svg = []
    for idx, line in enumerate(body_lines[:16]):
        y = text_y + idx * 18
        body_svg.append(
            f'<text x="{node.x + 14}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="13" fill="{node.body_color}">{escape(line)}</text>'
        )

    return "\n".join(
        [
            f'<rect x="{node.x}" y="{node.y}" rx="16" ry="16" width="{node.w}" height="{node.h}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"/>',
            f'<rect x="{node.x}" y="{node.y}" rx="16" ry="16" width="{node.w}" height="{title_h}" fill="{node.title_fill}" />',
            f'<rect x="{node.x}" y="{body_y}" width="{node.w}" height="{body_h}" fill="{node.fill}" />',
            f'<line x1="{node.x}" y1="{body_y}" x2="{node.x + node.w}" y2="{body_y}" stroke="{node.stroke}" stroke-width="2"/>',
            f'<text x="{node.x + node.w / 2}" y="{node.y + 22}" text-anchor="middle" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="16" fill="{node.title_color}">{escape(node.title)}</text>',
            *body_svg,
        ]
    )


def render_group_label(text: str, x: int, y: int, w: int, h: int, stroke: str = "#9fb6cc") -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" rx="22" ry="22" width="{w}" height="{h}" fill="none" stroke="{stroke}" stroke-width="2" stroke-dasharray="10 8"/>',
            f'<text x="{x + 18}" y="{y + 28}" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="18" fill="#35516e">{escape(text)}</text>',
        ]
    )


def render_edge(edge: Edge, nodes: dict[str, Node]) -> str:
    src = nodes[edge.src]
    dst = nodes[edge.dst]
    x1, y1 = anchor(src, edge.src_side)
    x2, y2 = anchor(dst, edge.dst_side)
    label_x = (x1 + x2) // 2
    label_y = (y1 + y2) // 2 - 8
    if edge.mid_x is not None:
        label_x = edge.mid_x + 8
    if edge.mid_y is not None:
        label_y = edge.mid_y - 8

    parts = [
        f'<path d="{edge_path(edge, nodes)}" fill="none" stroke="{edge.color}" stroke-width="2.5" marker-end="url(#arrow)"/>'
    ]
    if edge.label:
        parts.append(
            f'<text x="{label_x}" y="{label_y}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="12" fill="{edge.color}" text-anchor="middle">{escape(edge.label)}</text>'
        )
    return "\n".join(parts)


def build_data() -> tuple[dict[str, Node], list[Edge]]:
    nodes = {
        "main": Node(
            key="main",
            title="main.py / agent.py",
            x=170,
            y=70,
            w=320,
            h=130,
            fill="#edf5ff",
            lines=[
                "CLI entrypoint and legacy single-agent compatibility.",
                "extract_stock_symbol(), analyze_stock(), interactive_session().",
            ],
        ),
        "web": Node(
            key="web",
            title="web_server.py",
            x=620,
            y=70,
            w=380,
            h=160,
            fill="#eefcf7",
            title_fill="#17543b",
            stroke="#2a6d52",
            lines=[
                "StockChatHandler with auth, job polling, report serving, admin APIs.",
                "Routes: register, login, chat, reports, admin stats.",
            ],
        ),
        "sdk": Node(
            key="sdk",
            title="openai_sdk.py",
            x=1120,
            y=70,
            w=330,
            h=130,
            fill="#fff6e7",
            title_fill="#7d4e12",
            stroke="#96611f",
            lines=[
                "Namespace-safe wrapper around OpenAI Agents SDK.",
                "Provides Agent, Runner, ModelSettings, function_tool.",
            ],
        ),
        "pipeline": Node(
            key="pipeline",
            title="agents/pipeline_orchestrator.py",
            x=470,
            y=300,
            w=680,
            h=200,
            fill="#f4efff",
            title_fill="#4f378b",
            stroke="#6950a1",
            lines=[
                "Sequential multi-agent runner with guaranteed execution order.",
                "fetch_raw_stock_data(), run_stock_analysis_pipeline(),",
                "run_full_analysis_with_pdf().",
                "Collects raw market data, agent outputs, citations, risk metrics, and final recommendation.",
            ],
        ),
        "fundamental": Node(
            key="fundamental",
            title="Fundamental Analyst",
            x=80,
            y=610,
            w=250,
            h=145,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=["Valuation, ROE, debt, growth, profitability."],
        ),
        "technical": Node(
            key="technical",
            title="Technical Analyst",
            x=360,
            y=610,
            w=250,
            h=145,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=["RSI, MACD, moving averages, trend, support and resistance."],
        ),
        "sentiment": Node(
            key="sentiment",
            title="Sentiment Analyst",
            x=640,
            y=610,
            w=250,
            h=145,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=["News fetch, VADER/TextBlob sentiment scoring, market mood."],
        ),
        "newsintel": Node(
            key="newsintel",
            title="News Intelligence Agent",
            x=920,
            y=610,
            w=250,
            h=165,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=[
                "Exa live research, event detection, impact scoring, sector news.",
            ],
        ),
        "macro": Node(
            key="macro",
            title="Macro Analyst",
            x=1200,
            y=610,
            w=250,
            h=145,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=["India macro data, FII/DII flows, benchmark and sector context."],
        ),
        "document": Node(
            key="document",
            title="Document Analyst",
            x=1480,
            y=610,
            w=250,
            h=145,
            fill="#dff3ff",
            title_fill="#20638d",
            stroke="#2c6f98",
            lines=["Quarterly results, announcements, management commentary, peer comparison."],
        ),
        "bull": Node(
            key="bull",
            title="Bull Advocate",
            x=510,
            y=850,
            w=240,
            h=145,
            fill="#e4fbec",
            title_fill="#1c6b3a",
            stroke="#2f7f4f",
            lines=["Builds strongest bullish thesis from analysis context."],
        ),
        "bear": Node(
            key="bear",
            title="Bear Advocate",
            x=810,
            y=850,
            w=240,
            h=145,
            fill="#ffe7e7",
            title_fill="#8b2c2c",
            stroke="#a04040",
            lines=["Builds strongest bearish thesis and downside case."],
        ),
        "judge": Node(
            key="judge",
            title="Debate Judge",
            x=1110,
            y=850,
            w=240,
            h=145,
            fill="#fff2dd",
            title_fill="#8a5b12",
            stroke="#a06e20",
            lines=["Scores both sides and returns balanced verdict."],
        ),
        "risk": Node(
            key="risk",
            title="Risk Manager",
            x=1410,
            y=850,
            w=250,
            h=165,
            fill="#fff5df",
            title_fill="#8a5b12",
            stroke="#a06e20",
            lines=[
                "Position sizing, ATR/support stop-loss, risk-reward, allocation limits."
            ],
        ),
        "portfolio": Node(
            key="portfolio",
            title="Portfolio Analyst",
            x=1710,
            y=850,
            w=250,
            h=165,
            fill="#fff5df",
            title_fill="#8a5b12",
            stroke="#a06e20",
            lines=["Portfolio health, correlation, risk metrics, rebalancing."],
        ),
        "stocktools": Node(
            key="stocktools",
            title="tools/stock_data.py",
            x=60,
            y=1120,
            w=280,
            h=175,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "get_stock_price()",
                "get_stock_info()",
                "get_historical_data()",
                "get_fundamentals()",
            ],
        ),
        "technicaltools": Node(
            key="technicaltools",
            title="tools/technical_analysis.py",
            x=370,
            y=1120,
            w=280,
            h=175,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "get_technical_indicators()",
                "get_support_resistance()",
                "analyze_trend()",
            ],
        ),
        "newstools": Node(
            key="newstools",
            title="News / Sentiment Tools",
            x=680,
            y=1120,
            w=280,
            h=195,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "news_fetcher.py",
                "sentiment_analyzer.py",
                "news_intelligence.py",
                "get_stock_news(), analyze_news_sentiment(),",
                "fetch_comprehensive_news(), analyze_news_with_events()",
            ],
        ),
        "exatools": Node(
            key="exatools",
            title="tools/exa_research.py",
            x=990,
            y=1120,
            w=280,
            h=175,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "exa_web_search_stock_news()",
                "exa_company_snapshot()",
                "exa_deep_stock_research()",
                "exa_live_company_intelligence()",
            ],
        ),
        "macrotools": Node(
            key="macrotools",
            title="tools/macro_data.py",
            x=1300,
            y=1120,
            w=280,
            h=175,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "India macro indicators, benchmark comparison,",
                "sector performance, FII/DII activity, global context.",
            ],
        ),
        "documenttools": Node(
            key="documenttools",
            title="tools/document_analyzer.py",
            x=1610,
            y=1120,
            w=280,
            h=175,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "Announcements, quarterly results, document search,",
                "management commentary, peer comparison.",
            ],
        ),
        "risktools": Node(
            key="risktools",
            title="Risk / Portfolio Tools",
            x=1920,
            y=1120,
            w=280,
            h=195,
            fill="#eef7ff",
            title_fill="#355c7d",
            stroke="#4b6d89",
            lines=[
                "risk_management.py",
                "portfolio_analyzer.py",
                "calculate_position_size(),",
                "calculate_stop_loss_levels(),",
                "analyze_portfolio_health(), suggest_rebalancing()",
            ],
        ),
        "schemas": Node(
            key="schemas",
            title="models/schemas.py",
            x=1710,
            y=300,
            w=400,
            h=210,
            fill="#f0edff",
            title_fill="#4f378b",
            stroke="#6950a1",
            lines=[
                "Pydantic output models:",
                "FundamentalAnalysis, TechnicalAnalysis, SentimentAnalysis, StockRecommendation.",
            ],
        ),
        "pdf": Node(
            key="pdf",
            title="pdf_generator.py",
            x=1710,
            y=560,
            w=400,
            h=210,
            fill="#fff3ea",
            title_fill="#8d4b1c",
            stroke="#b96d33",
            lines=[
                "StockReportData and generate_stock_report().",
                "Builds final professional PDF report from authoritative raw data + synthesized analysis.",
            ],
        ),
        "db": Node(
            key="db",
            title="SQLite app_data.db",
            x=60,
            y=300,
            w=320,
            h=210,
            fill="#eefcf7",
            title_fill="#17543b",
            stroke="#2a6d52",
            lines=[
                "Tables: users, sessions, chat_history, reports.",
                "Used by web layer for auth, persistence, and report history.",
            ],
        ),
        "output": Node(
            key="output",
            title="Outputs",
            x=980,
            y=1430,
            w=560,
            h=170,
            fill="#effaf0",
            title_fill="#1f6f43",
            stroke="#348456",
            lines=[
                "BUY / HOLD / SELL recommendation, confidence score, citations, PDF report,",
                "saved chat and report metadata available through the web app and CLI.",
            ],
        ),
    }

    edges = [
        Edge("main", "pipeline", color="#516579", label="analyze request"),
        Edge("main", "sdk", color="#8a6c2d", label="imports wrapper", src_side="right", dst_side="left"),
        Edge("web", "pipeline", color="#2a6d52", label="chat job", src_side="bottom", dst_side="top"),
        Edge("web", "db", color="#2a6d52", label="auth / history", src_side="left", dst_side="right", mid_y=245),
        Edge("pipeline", "sdk", color="#8a6c2d", label="Runner.run()", src_side="top", dst_side="bottom", mid_x=1285),
        Edge("pipeline", "fundamental", color="#4d87ad", label="1", src_side="bottom", dst_side="top", mid_x=205),
        Edge("pipeline", "technical", color="#4d87ad", label="2", src_side="bottom", dst_side="top", mid_x=485),
        Edge("pipeline", "sentiment", color="#4d87ad", label="3", src_side="bottom", dst_side="top", mid_x=765),
        Edge("pipeline", "newsintel", color="#4d87ad", label="3b", src_side="bottom", dst_side="top", mid_x=1045),
        Edge("pipeline", "macro", color="#4d87ad", label="4", src_side="bottom", dst_side="top", mid_x=1325),
        Edge("pipeline", "document", color="#4d87ad", label="5", src_side="bottom", dst_side="top", mid_x=1605),
        Edge("pipeline", "bull", color="#2f7f4f", label="6", src_side="bottom", dst_side="top", mid_x=630),
        Edge("pipeline", "bear", color="#a04040", label="7", src_side="bottom", dst_side="top", mid_x=930),
        Edge("pipeline", "judge", color="#a06e20", label="8", src_side="bottom", dst_side="top", mid_x=1230),
        Edge("pipeline", "risk", color="#a06e20", label="9", src_side="bottom", dst_side="top", mid_x=1535),
        Edge("pipeline", "portfolio", color="#a06e20", label="portfolio mode", src_side="right", dst_side="top", mid_x=1835),
        Edge("fundamental", "stocktools", color="#4b6d89"),
        Edge("technical", "stocktools", color="#4b6d89", src_side="bottom", dst_side="top", mid_x=235),
        Edge("technical", "technicaltools", color="#4b6d89"),
        Edge("sentiment", "newstools", color="#4b6d89"),
        Edge("newsintel", "newstools", color="#4b6d89", src_side="bottom", dst_side="top", mid_x=815),
        Edge("newsintel", "exatools", color="#4b6d89"),
        Edge("macro", "macrotools", color="#4b6d89"),
        Edge("document", "documenttools", color="#4b6d89"),
        Edge("risk", "risktools", color="#4b6d89"),
        Edge("portfolio", "risktools", color="#4b6d89", src_side="bottom", dst_side="top", mid_x=2060),
        Edge("pipeline", "schemas", color="#6950a1", label="structured outputs", src_side="right", dst_side="left", mid_y=405),
        Edge("pipeline", "pdf", color="#b96d33", label="StockReportData", src_side="right", dst_side="left", mid_y=650),
        Edge("schemas", "pdf", color="#8d58b2", label="validated model shape", src_side="bottom", dst_side="top"),
        Edge("pdf", "output", color="#348456", label="final PDF", src_side="bottom", dst_side="top", mid_x=1400),
        Edge("pipeline", "output", color="#348456", label="final recommendation", src_side="bottom", dst_side="top", mid_x=1050),
        Edge("web", "output", color="#2a6d52", label="serve reports / history", src_side="bottom", dst_side="top", mid_x=860),
    ]

    return nodes, edges


def build_svg(nodes: dict[str, Node], edges: list[Edge]) -> str:
    width = 2280
    height = 1660

    group_layers = [
        render_group_label("Application Entry + Interface Layer", 40, 30, 1440, 240),
        render_group_label("Core Orchestration Layer", 430, 260, 760, 270),
        render_group_label("Specialist Agents", 40, 570, 1725, 230),
        render_group_label("Debate + Risk Layer", 470, 810, 1510, 250),
        render_group_label("Tooling Layer", 30, 1080, 2190, 270),
        render_group_label("Models / Reporting", 1660, 260, 490, 540),
        render_group_label("Persistent Storage", 35, 260, 360, 280),
        render_group_label("User-Facing Outputs", 930, 1390, 660, 220),
    ]

    background = """
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fbfdff"/>
        <stop offset="100%" stop-color="#eef5fb"/>
      </linearGradient>
      <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
        <path d="M 0 0 L 12 6 L 0 12 z" fill="#62758a"/>
      </marker>
    </defs>
    <rect x="0" y="0" width="100%" height="100%" fill="url(#bg)"/>
    """

    title = """
    <text x="1140" y="32" text-anchor="middle" font-family="Segoe UI Semibold, Arial, sans-serif" font-size="28" fill="#16324a">
      Indian Stock AI Agent - Full Project Architecture
    </text>
    <text x="1140" y="58" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#50667d">
      Sequential multi-agent stock analysis pipeline, tool dependencies, reporting, web APIs, and persistence
    </text>
    """

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        background,
        title,
        *group_layers,
        *[render_edge(edge, nodes) for edge in edges],
        *[render_node(node) for node in nodes.values()],
        "</svg>",
    ]
    return "\n".join(svg_parts)


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


def rgba(hex_color: str) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Unsupported color: {hex_color}")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (255,)


def multiline(draw, x: int, y: int, lines: list[str], font, fill, line_gap: int = 6) -> None:
    cursor = y
    for line in lines:
        draw.text((x, cursor), line, font=font, fill=fill)
        bbox = draw.textbbox((x, cursor), line, font=font)
        cursor = bbox[3] + line_gap


def draw_arrowhead(draw, end: tuple[int, int], prev: tuple[int, int], color) -> None:
    x2, y2 = end
    x1, y1 = prev
    size = 10
    if x2 == x1 and y2 >= y1:
        points = [(x2, y2), (x2 - size, y2 - size * 1.4), (x2 + size, y2 - size * 1.4)]
    elif x2 == x1 and y2 < y1:
        points = [(x2, y2), (x2 - size, y2 + size * 1.4), (x2 + size, y2 + size * 1.4)]
    elif y2 == y1 and x2 >= x1:
        points = [(x2, y2), (x2 - size * 1.4, y2 - size), (x2 - size * 1.4, y2 + size)]
    else:
        points = [(x2, y2), (x2 + size * 1.4, y2 - size), (x2 + size * 1.4, y2 + size)]
    draw.polygon(points, fill=color)


def polyline_points(edge: Edge, nodes: dict[str, Node]) -> list[tuple[int, int]]:
    src = nodes[edge.src]
    dst = nodes[edge.dst]
    x1, y1 = anchor(src, edge.src_side)
    x2, y2 = anchor(dst, edge.dst_side)

    if edge.mid_x is not None:
        return [(x1, y1), (edge.mid_x, y1), (edge.mid_x, y2), (x2, y2)]
    if edge.mid_y is not None:
        return [(x1, y1), (x1, edge.mid_y), (x2, edge.mid_y), (x2, y2)]
    if edge.src_side in {"top", "bottom"} and edge.dst_side in {"top", "bottom"}:
        mid_y = (y1 + y2) // 2
        return [(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)]
    if edge.src_side in {"left", "right"} and edge.dst_side in {"left", "right"}:
        mid_x = (x1 + x2) // 2
        return [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]
    return [(x1, y1), (x2, y2)]


def render_png(nodes: dict[str, Node], edges: list[Edge], out_path: Path) -> None:
    from PIL import Image, ImageDraw

    width = 2280
    height = 1660
    img = Image.new("RGBA", (width, height), rgba("#f8fbfe"))
    draw = ImageDraw.Draw(img)

    # Soft background accents
    draw.rounded_rectangle((0, 0, width, height), radius=0, fill=rgba("#f8fbfe"))
    draw.ellipse((-300, -150, 600, 450), fill=(234, 242, 250, 255))
    draw.ellipse((1650, 1180, 2480, 1880), fill=(232, 243, 236, 255))

    title_font = load_font(28, bold=True)
    subtitle_font = load_font(14)
    group_font = load_font(18, bold=True)
    node_title_font = load_font(16, bold=True)
    node_body_font = load_font(13)
    edge_font = load_font(12)

    draw.text((1140, 16), "Indian Stock AI Agent - Full Project Architecture", anchor="ma", font=title_font, fill=rgba("#16324a"))
    draw.text(
        (1140, 44),
        "Sequential multi-agent stock analysis pipeline, tool dependencies, reporting, web APIs, and persistence",
        anchor="ma",
        font=subtitle_font,
        fill=rgba("#50667d"),
    )

    groups = [
        ("Application Entry + Interface Layer", 40, 30, 1440, 240),
        ("Core Orchestration Layer", 430, 260, 760, 270),
        ("Specialist Agents", 40, 570, 1725, 230),
        ("Debate + Risk Layer", 470, 810, 1510, 250),
        ("Tooling Layer", 30, 1080, 2190, 270),
        ("Models / Reporting", 1660, 260, 490, 540),
        ("Persistent Storage", 35, 260, 360, 280),
        ("User-Facing Outputs", 930, 1390, 660, 220),
    ]
    for text, x, y, w, h in groups:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=22, outline=rgba("#9fb6cc"), width=2)
        draw.text((x + 18, y + 12), text, font=group_font, fill=rgba("#35516e"))

    for edge in edges:
        points = polyline_points(edge, nodes)
        color = rgba(edge.color)
        draw.line(points, fill=color, width=3, joint="curve")
        draw_arrowhead(draw, points[-1], points[-2], color)
        if edge.label:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            label_x = edge.mid_x + 8 if edge.mid_x is not None else (min(xs) + max(xs)) // 2
            label_y = edge.mid_y - 8 if edge.mid_y is not None else (min(ys) + max(ys)) // 2 - 8
            bbox = draw.textbbox((label_x, label_y), edge.label, font=edge_font, anchor="mm")
            pad = 4
            draw.rounded_rectangle(
                (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad),
                radius=6,
                fill=(248, 251, 254, 230),
            )
            draw.text((label_x, label_y), edge.label, font=edge_font, fill=color, anchor="mm")

    for node in nodes.values():
        title_h = 34
        draw.rounded_rectangle((node.x, node.y, node.x + node.w, node.y + node.h), radius=16, fill=rgba(node.fill), outline=rgba(node.stroke), width=2)
        draw.rounded_rectangle((node.x, node.y, node.x + node.w, node.y + title_h), radius=16, fill=rgba(node.title_fill))
        draw.rectangle((node.x, node.y + title_h, node.x + node.w, node.y + node.h), fill=rgba(node.fill))
        draw.line((node.x, node.y + title_h, node.x + node.w, node.y + title_h), fill=rgba(node.stroke), width=2)
        draw.text((node.x + node.w // 2, node.y + 18), node.title, font=node_title_font, fill=rgba(node.title_color), anchor="mm")

        body_lines: list[str] = []
        for raw in node.lines:
            body_lines.extend(wrap(raw, width=max(28, node.w // 8)) or [""])
        multiline(
            draw,
            node.x + 14,
            node.y + title_h + 10,
            body_lines[:16],
            node_body_font,
            rgba(node.body_color),
            line_gap=3,
        )

    img.save(out_path)


def main() -> None:
    nodes, edges = build_data()
    svg = build_svg(nodes, edges)
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    render_png(nodes, edges, OUTPUT_PNG)
    print(f"Architecture diagram written to: {OUTPUT_SVG}")
    print(f"Architecture diagram written to: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
