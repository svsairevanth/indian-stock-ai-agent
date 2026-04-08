from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path(__file__).resolve().parent / "indian_stock_ai_agent_sample_style.png"


@dataclass
class Box:
    title: str
    x: int
    y: int
    w: int
    methods: list[str]
    members: list[str]
    h: int = 0


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


FONT_TITLE = load_font(22, bold=True)
FONT_LABEL = load_font(18, bold=True)
FONT_TEXT = load_font(14)
FONT_SMALL = load_font(13)


def estimate_height(draw: ImageDraw.ImageDraw, box: Box) -> int:
    line_h = draw.textbbox((0, 0), "Ag", font=FONT_TEXT)[3] + 4
    title_h = 36

    methods_lines = 0
    for item in box.methods:
        methods_lines += max(1, len(wrap(item, width=max(20, box.w // 9))))
    members_lines = 0
    for item in box.members:
        members_lines += max(1, len(wrap(item, width=max(20, box.w // 9))))

    methods_h = 22 + methods_lines * line_h + 12
    members_h = 22 + members_lines * line_h + 16
    return title_h + methods_h + members_h


def draw_box(draw: ImageDraw.ImageDraw, box: Box) -> None:
    border = "#4b6e92"
    fill = "#48c7ea"
    title_fill = "#9fb8df"
    text_color = "#0f2438"

    box.h = estimate_height(draw, box)
    title_h = 36
    methods_h = box.h - title_h

    draw.rectangle((box.x, box.y, box.x + box.w, box.y + box.h), outline=border, width=2, fill=fill)
    draw.rectangle((box.x, box.y, box.x + box.w, box.y + title_h), outline=border, width=2, fill=title_fill)
    draw.text((box.x + box.w / 2, box.y + 10), box.title, anchor="ma", font=FONT_TITLE, fill="#17324c")

    current_y = box.y + title_h + 10
    methods_label_y = current_y
    draw.text((box.x - 48, methods_label_y), "Methods", anchor="ra", font=FONT_LABEL, fill="#333333")
    max_width = max(20, box.w // 9)
    for item in box.methods:
        for line in wrap(item, width=max_width):
            draw.text((box.x + 10, current_y), line, font=FONT_TEXT, fill=text_color)
            current_y += 18

    divider_y = current_y + 4
    draw.line((box.x, divider_y, box.x + box.w, divider_y), fill=border, width=2)

    current_y = divider_y + 10
    draw.text((box.x - 48, current_y), "Members", anchor="ra", font=FONT_LABEL, fill="#333333")
    for item in box.members:
        for line in wrap(item, width=max_width):
            draw.text((box.x + 10, current_y), line, font=FONT_TEXT, fill=text_color)
            current_y += 18


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#c54a4a", width: int = 3) -> None:
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    size = 10
    if abs(x2 - x1) > abs(y2 - y1):
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 14, y2 - size), (x2 - 14, y2 + size)]
        else:
            pts = [(x2, y2), (x2 + 14, y2 - size), (x2 + 14, y2 + size)]
    else:
        if y2 >= y1:
            pts = [(x2, y2), (x2 - size, y2 - 14), (x2 + size, y2 - 14)]
        else:
            pts = [(x2, y2), (x2 - size, y2 + 14), (x2 + size, y2 + 14)]
    draw.polygon(pts, fill=color)


def main() -> None:
    img = Image.new("RGB", (1600, 980), "white")
    draw = ImageDraw.Draw(img)

    top = Box(
        title="Indian Stock AI Agent Platform",
        x=170,
        y=30,
        w=980,
        methods=[
            "analyze_stock(), analyze_stock_sync(), analyze_stock_streaming(), interactive_session()",
            "run_stock_analysis_pipeline(), run_full_analysis_with_pdf(), fetch_raw_stock_data(), determine_recommendation()",
            "_handle_register(), _handle_login(), _handle_chat(), _handle_reports(), _handle_admin_stats(), _handle_logout()",
            "generate_stock_report(), create_stock_report(), extract_citations(), extract_risk_metrics()",
        ],
        members=[
            "agents_run, raw_data, fundamental, technical, sentiment, news_intelligence, macro, document",
            "bull_case, bear_case, debate_verdict, risk_assessment, portfolio_analysis, final_recommendation",
            "users, sessions, chat_history, reports, stock_symbol, user_query, StockReportData, StockRecommendation",
        ],
    )

    left = Box(
        title="CLI / Query Interface",
        x=280,
        y=360,
        w=280,
        methods=[
            "extract_stock_symbol()",
            "analyze_stock()",
            "interactive_session()",
        ],
        members=[
            "query, stock_symbol, use_multi_agent",
            "single-agent fallback, command-line usage",
        ],
    )

    right = Box(
        title="Web App / Auth API",
        x=820,
        y=360,
        w=320,
        methods=[
            "_handle_register()",
            "_handle_login()",
            "_handle_chat()",
            "_handle_logout(), _handle_reports(), _handle_admin_stats()",
        ],
        members=[
            "users, sessions, chat_history, reports",
            "session_cookie, DB_PATH, jobs",
            "admin/user role support, report history",
        ],
    )

    bottom = Box(
        title="Stock Analysis Engine / Reports Layer",
        x=200,
        y=680,
        w=1120,
        methods=[
            "invoke Fundamental, Technical, Sentiment, News Intelligence, Macro, Document agents",
            "invoke Bull Advocate, Bear Advocate, Debate Judge, Risk Manager, Portfolio Analyst",
            "collect tool outputs, compute recommendation, build PDF report, persist chat/report data",
        ],
        members=[
            "fundamental_analyst_agent, technical_analyst_agent, sentiment_analyst_agent, news_intelligence_agent",
            "macro_analyst_agent, document_analyst_agent, bull_agent, bear_agent, debate_judge_agent",
            "risk_manager_agent, portfolio_analyst_agent, StockRecommendation, FundamentalAnalysis, TechnicalAnalysis, SentimentAnalysis",
            "tools: stock_data, technical_analysis, news_fetcher, sentiment_analyzer, exa_research, macro_data, document_analyzer, risk_management, portfolio_analyzer",
        ],
    )

    for box in (top, left, right, bottom):
        draw_box(draw, box)

    draw.text((420, 332), "CLI Entry", anchor="ma", font=FONT_LABEL, fill="#222222")
    draw.text((980, 332), "Web APIs", anchor="ma", font=FONT_LABEL, fill="#222222")
    draw.text((780, 652), "Stock Analysis Pipeline", anchor="ma", font=FONT_LABEL, fill="#222222")

    arrow(draw, (560, 235), (420, 360))
    arrow(draw, (830, 235), (980, 360))
    arrow(draw, (680, 235), (760, 680))
    arrow(draw, (420, left.y + left.h), (420, 680))
    arrow(draw, (980, right.y + right.h), (1020, 680))

    draw.text((25, 18), "Component Diagram", font=FONT_SMALL, fill="#666666")
    img.save(OUT_PATH)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
