# FINAL YEAR PROJECT DOCUMENTATION

---

## TITLE

# Indian Stock Intelligence Studio: A Multi-Agent AI System for Real-Time NSE/BSE Stock Analysis and Investment Decision Support

---
**Department:** Computer Science and Engineering  
**Project Type:** Final Year B.E. / B.Tech Project  
**Technology Stack:** Python, OpenAI Agents SDK, GPT-4o-mini, yfinance, ReportLab, SQLite  
**Academic Year:** 2025–2026  

---

## TABLE OF CONTENTS

1. Abstract  
2. Introduction  
3. Existing System  
4. Proposed System  
5. Modules  
6. Development Stages (5 Phases)  
7. Design and Implementation  
8. System Requirements  
9. Use Case Diagram  
10. Results and Discussion  

---

## 1. ABSTRACT

The Indian Stock Intelligence Studio is an AI-powered multi-agent stock analysis platform designed to assist retail investors in making informed investment decisions for stocks listed on the National Stock Exchange (NSE) and Bombay Stock Exchange (BSE). The system employs a pipeline of ten specialized AI agents — Fundamental Analyst, Technical Analyst, News Intelligence Analyst, Sentiment Analyst, Macro Analyst, Document Analyst, Bull Advocate, Bear Advocate, Debate Judge, and Risk Manager — each contributing a unique analytical perspective on a given stock.

The platform integrates real-time market data from Yahoo Finance (yfinance), news intelligence via Exa MCP web research, and sentiment scoring using VADER and TextBlob. A pipeline orchestrator sequentially runs all agents, aggregates their outputs, conducts a structured bull-vs-bear debate, and produces a final BUY/SELL/HOLD recommendation with a confidence score. The complete analysis is packaged into a professionally formatted PDF report generated using ReportLab.

A full-stack web application with user authentication, session management, chat history, and an admin dashboard is provided via a built-in Python HTTP server serving a single-page application (SPA) frontend. The system demonstrates how large language models (LLMs) can be orchestrated in a multi-agent architecture to replicate the collaborative reasoning of a professional equity research team, making institutional-grade analysis accessible to individual investors.

---

## 2. INTRODUCTION

### 2.1 Background

The Indian stock market, comprising the NSE and BSE, has seen unprecedented retail participation in recent years — with over 150 million registered investors as of 2025 and 9+ crore active demat accounts. Despite this surge, the majority of retail investors lack access to the structured, multi-dimensional analysis that institutional investors routinely obtain from research desks.

Traditional retail investing decisions are often driven by tips, social media speculation, or at best, a cursory glance at a stock's price history. Professional equity research — which synthesises fundamental health, technical chart signals, macro-economic context, news sentiment, and risk-adjusted trade setups — is expensive and inaccessible to the average investor.

Artificial Intelligence, specifically the emergence of large language models (LLMs) and the OpenAI Agents SDK, now makes it possible to automate and democratise this institutional-grade research process. A well-designed multi-agent system can assign each analytical dimension to a specialist agent, run them concurrently or sequentially, and synthesise a holistic, data-driven recommendation — all within minutes.

### 2.2 Motivation

The primary motivation behind this project is to bridge the information gap between institutional and retail investors in India. The key motivating factors are:

- **Complexity of stock analysis:** A thorough equity analysis requires expertise across fundamentals, technicals, macroeconomics, news, and risk — skills rarely combined in a single individual.
- **Accessibility:** Institutional research reports (e.g., from Goldman Sachs, Morgan Stanley) are reserved for HNI and institutional clients. Retail investors deserve equivalent depth.
- **Speed:** Manual research can take days; the system completes a full 10-agent analysis in minutes.
- **Objectivity:** AI agents do not suffer from emotional biases (fear, greed) that plague human investors.
- **Structured debate:** By having dedicated Bull and Bear agents argue opposing cases before a Judge delivers a verdict, the system avoids single-perspective bias.

### 2.3 Objectives

The objectives of this project are:

1. To design and implement a multi-agent AI architecture for comprehensive Indian stock analysis.
2. To integrate real-time data sources (yfinance, Exa MCP) for live market data and news.
3. To implement ten specialist AI agents covering all key dimensions of equity research.
4. To automate PDF report generation with professional formatting and actionable trade parameters.
5. To build a secure web application with user authentication, chat history, and admin management.
6. To produce actionable investment signals (BUY/SELL/HOLD) with quantified confidence scores.

### 2.4 Scope

- Covers all NSE stocks (suffix `.NS`) and BSE stocks (suffix `.BO`).
- Analyses Indian equity indices: NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT, etc.
- Generates professional PDF research reports downloadable by registered users.
- Provides a web-based chat interface accessible from any modern browser.
- Includes an admin panel for user and activity management.

---

## 3. EXISTING SYSTEM

### 3.1 Overview of Current Solutions

Several tools exist for stock market analysis in India, including platforms like Zerodha Kite, Moneycontrol, Screener.in, TradingView, and Tickertape. While each offers partial capabilities, none provides a fully integrated, AI-driven, multi-agent analysis pipeline.

### 3.2 Limitations of Existing Systems

| Feature | Zerodha / Brokers | Screener.in | TradingView | Moneycontrol |
|---|---|---|---|---|
| Fundamental Analysis | Basic | ✅ Good | ❌ No | Basic |
| Technical Indicators | Basic | ❌ No | ✅ Excellent | Basic |
| News Sentiment AI | ❌ No | ❌ No | ❌ No | Manual |
| Macro Context | ❌ No | ❌ No | ❌ No | ❌ No |
| Bull vs Bear Debate | ❌ No | ❌ No | ❌ No | ❌ No |
| Risk Management | Basic | ❌ No | Manual | ❌ No |
| PDF Report Generation | ❌ No | ❌ No | ❌ No | ❌ No |
| AI Recommendation | ❌ No | ❌ No | ❌ No | ❌ No |
| Multi-Agent System | ❌ No | ❌ No | ❌ No | ❌ No |

**Key drawbacks of existing systems:**

1. **Siloed analysis:** Fundamental and technical analysis are presented in isolation; no system integrates both with news sentiment and macroeconomics in a single unified output.
2. **No AI reasoning:** Existing platforms display raw data but do not reason over it to produce actionable conclusions.
3. **No debate mechanism:** No platform implements a structured bull-vs-bear argument to stress-test investment theses from both perspectives.
4. **Manual synthesis required:** Users must manually read multiple tools and synthesise insights — a time-consuming, error-prone process.
5. **No automated PDF reports:** Professional formatted reports must be manually created; no automated generation for retail investors exists.
6. **No personalisation:** Tools are generic and do not incorporate user context (e.g., "I hold this stock at ₹1,500 — should I exit?").
7. **No risk quantification:** Stop-loss levels, target prices, position sizing, and risk-reward ratios are not automatically computed in an integrated fashion.

---

## 4. PROPOSED SYSTEM

### 4.1 Overview

The Indian Stock Intelligence Studio is a **10-agent sequential pipeline** powered by the OpenAI Agents SDK. Users submit a natural language query (e.g., *"Should I buy RELIANCE? I have a medium-term horizon."*) through a web chat interface. The system:

1. Detects the stock symbol from the query.
2. Fetches authoritative real-time data from yfinance.
3. Runs 10 specialist agents sequentially across 3 phases.
4. Synthesises all outputs into a final recommendation with a confidence score.
5. Generates and stores a professional PDF research report.
6. Returns the analysis to the user via the chat interface with a PDF download link.

### 4.2 Key Innovations

- **Multi-Agent Pipeline Architecture:** Ten dedicated AI agents, each a domain expert, run in a guaranteed sequential order — eliminating the unreliability of LLM-based handoffs.
- **Adversarial Debate Mechanism:** A Bull Agent and Bear Agent argue opposing investment theses; a Debate Judge delivers the final verdict, replicating institutional research debate processes.
- **Data Authority Separation:** Numerical data (price, P/E, ROE, 52-week ranges) is fetched directly from yfinance and is never modified by the LLM, preventing hallucination of financial figures.
- **Exa MCP Web Research Integration:** The News Intelligence Agent uses live Exa web search for real-time, citation-backed news with source URLs.
- **Automated PDF Generation:** Every analysis produces a professionally formatted PDF with metrics tables, trade setup, bull/bear cases, and source citations.
- **Dual Sentiment Analysis:** VADER (rule-based) and TextBlob (ML-based) sentiment scoring are combined for robust news sentiment quantification.
- **Full-Stack Web App:** Secure login/register, session cookies, chat history persistence in SQLite, admin dashboard, and per-user report storage.

### 4.3 Advantages Over Existing Systems

1. End-to-end analysis in a single interface — no tool-switching required.
2. AI reasoning over data, not just data display.
3. Adversarial validation eliminates single-perspective bias.
4. Downloadable PDF research reports for every query.
5. Quantified confidence scores and risk-reward ratios.
6. Personalised analysis based on user's natural language context.
7. Admin panel for multi-user deployment.

---

## 5. MODULES

The system is organised into the following six major modules:

### Module 1: Data Acquisition Module (`tools/`)

Responsible for fetching real-time and historical financial data from external sources.

**Sub-components:**
- `stock_data.py` — Fetches live prices, fundamentals (P/E, P/B, ROE, market cap, debt-to-equity, dividend yield), and historical OHLCV data from Yahoo Finance via yfinance.
- `technical_analysis.py` — Computes technical indicators: RSI (14), MACD (12/26/9), SMA (20/50/200), Bollinger Bands, ATR (14), support and resistance levels using pivot points and Fibonacci retracements, and trend direction.
- `news_fetcher.py` — Scrapes news headlines from financial portals using BeautifulSoup and the `requests` library.
- `news_intelligence.py` — Advanced news processing with event detection (earnings, management changes, regulatory actions) and impact scoring.
- `sentiment_analyzer.py` — Sentiment scoring using VADER (rule-based) and TextBlob (ML-based) on fetched news headlines.
- `macro_data.py` — Retrieves macroeconomic indicators: RBI repo rate, inflation (CPI), index performance (NIFTY 50, SENSEX), and sector benchmarks.
- `exa_research.py` — Interfaces with Exa MCP HTTP API for live web research with citation URLs.
- `portfolio_analyzer.py` — Portfolio-level analysis: diversification scoring, concentration risk, and sector allocation.
- `risk_management.py` — Quantitative risk tools: ATR-based stop-loss calculation, position sizing (2% risk rule), risk-reward ratio, and max allocation.
- `document_analyzer.py` — Processes structured quarterly result data and peer comparison metrics.

---

### Module 2: Multi-Agent Intelligence Module (`agents/`)

The core AI reasoning layer. Each agent is an independent specialised GPT-4o-mini instance with custom system instructions and a curated tool set.

**Agents:**

| # | Agent | Role | Key Tools |
|---|---|---|---|
| 1 | Fundamental Analyst | P/E, P/B, ROE, debt, growth, dividend analysis | `get_fundamentals`, `get_stock_info` |
| 2 | Technical Analyst | RSI, MACD, trend, support/resistance | `get_technical_indicators`, `get_support_resistance`, `analyze_trend` |
| 3 | News Intelligence Analyst | Live Exa web news, event detection, impact scoring | `exa_live_company_intelligence`, `fetch_comprehensive_news`, `analyze_news_with_events` |
| 4 | Sentiment Analyst | VADER + TextBlob dual sentiment scoring | `analyze_sentiment`, `fetch_news_headlines` |
| 5 | Macro Analyst | RBI policy, inflation, index benchmarking, sector context | `get_macro_indicators`, `get_sector_performance` |
| 6 | Document Analyst | Quarterly results, earnings surprises, peer comparison | `analyze_quarterly_results`, `get_peer_comparison` |
| 7 | Bull Advocate | Constructs the strongest possible bullish investment thesis | None (reasoning agent) |
| 8 | Bear Advocate | Constructs the strongest possible bearish counter-thesis | None (reasoning agent) |
| 9 | Debate Judge | Weighs bull vs. bear arguments; delivers BUY/SELL/HOLD verdict + confidence % | None (reasoning agent) |
| 10 | Risk Manager | Position sizing, stop-loss levels, risk-reward ratios, allocation limits | `calculate_position_size`, `calculate_stop_loss_levels`, `assess_trade_risk_reward` |

---

### Module 3: Pipeline Orchestrator Module (`agents/pipeline_orchestrator.py`)

The orchestrator manages sequential execution of all agents across three phases, handles progress callbacks for the frontend, extracts validated metrics from agent outputs, and coordinates PDF generation.

**Phases:**
- **Phase 0:** Raw data fetch (yfinance) — authoritative price and fundamental data.
- **Phase 1:** Data gathering — Fundamental, Technical, News Intelligence, Sentiment, Macro, Document agents.
- **Phase 2:** Bull vs. Bear debate — Bull Agent, Bear Agent, Debate Judge.
- **Phase 3:** Risk assessment — Risk Manager.
- **Final Step:** PDF generation using validated, authoritative data.

---

### Module 4: PDF Report Generation Module (`pdf_generator.py`)

Generates professional A4 PDF reports using ReportLab.

**Report Contents:**
- Header with company name, symbol, and recommendation badge (colour-coded: green=BUY, red=SELL, orange=HOLD).
- Live price metrics: current price, day change, 52-week high/low.
- Fundamental metrics table: P/E, P/B, ROE, Debt/Equity, Market Cap, Dividend Yield.
- Technical signals table: RSI, MACD signal, trend direction, support, resistance.
- Trade setup card: entry price, target, stop-loss, risk-reward ratio, win probability, expected edge %.
- Positive factors and risk factors (bullet lists from Bull and Bear agents).
- Detailed analysis narrative (500-word executive summary).
- News summary with source citations (URLs).
- Confidence score and investment horizon.
- Footer with generation timestamp and disclaimer.

---

### Module 5: Web Application Module (`web_server.py` + `chat.html`)

A full-stack web application built on Python's standard `http.server` (ThreadingHTTPServer) serving a single-page application.

**Backend API Endpoints:**

| Method | Endpoint | Function |
|---|---|---|
| GET | `/` | Serve the SPA (chat.html) |
| POST | `/api/register` | User registration (PBKDF2-SHA256 password hashing) |
| POST | `/api/login` | Login with session cookie (7-day expiry) |
| POST | `/api/logout` | Invalidate session |
| GET | `/api/me` | Get current user info |
| POST | `/api/chat/start` | Start async analysis job (background thread) |
| GET | `/api/chat/status?job_id=` | Poll job progress and events |
| GET | `/api/chats` | Get user's chat history |
| GET | `/api/reports` | Get user's generated reports |
| GET | `/reports/<filename>` | Serve PDF file (authenticated) |
| GET | `/api/admin/stats` | Admin dashboard stats |
| GET | `/api/admin/users` | Admin user management table |
| GET | `/health` | Server health check (API key status, Exa config) |

**Frontend Features (chat.html):**
- Login/Register card with tab switching.
- Chat workspace with message thread and real-time progress log.
- Accuracy Builder: stock symbol, investment horizon, risk profile, report style selectors.
- Quality pills: live status indicators for symbol detection, Exa connectivity, risk profile, citations.
- Sidebar with three panes: Prompt Ideas (clickable chips), Chat History, Generated Reports.
- Admin Panel tab (admin role only): stats cards + user management table.
- Responsive design (mobile, tablet, desktop).

---

### Module 6: Database and Session Module (SQLite — `app_data.db`)

Persistent storage layer using SQLite3 with four tables:

| Table | Purpose |
|---|---|
| `users` | Stores username, PBKDF2-SHA256 password hash, salt, role (user/admin), timestamps |
| `sessions` | Session tokens with user binding and 7-day expiry |
| `chat_history` | Each query, response, stock symbol, recommendation, confidence, PDF filename, timestamp |
| `reports` | PDF metadata: filename, path, stock symbol, recommendation, confidence, owner, timestamp |

---

## 6. DEVELOPMENT STAGES

The project was developed across five structured stages following an iterative development methodology:

---

### Stage 1: Research and Requirements Analysis (Weeks 1–3)

**Activities:**
- Literature review on multi-agent AI systems, LLM orchestration patterns (ReAct, Plan-and-Execute, Handoff), and OpenAI Agents SDK documentation.
- Analysis of existing Indian stock market platforms (Zerodha, Screener.in, TradingView, Moneycontrol) to identify feature gaps.
- Identification of relevant Python libraries: yfinance, ta (Technical Analysis), VADER, TextBlob, ReportLab, BeautifulSoup.
- Definition of functional requirements (10 agents, PDF output, web UI, auth) and non-functional requirements (response time, data accuracy, scalability).
- Finalised system architecture: sequential pipeline over handoff-based orchestration for guaranteed agent execution.

**Deliverables:**
- Software Requirements Specification (SRS) document.
- System architecture diagram.
- Technology stack selection.

---

### Stage 2: Data Layer and Tool Development (Weeks 4–7)

**Activities:**
- Implemented `tools/stock_data.py`: yfinance integration for live prices, fundamentals, and historical OHLCV data.
- Implemented `tools/technical_analysis.py`: RSI, MACD, SMA (20/50/200), Bollinger Bands, ATR, support/resistance via pivot points and Fibonacci levels, trend detection.
- Implemented `tools/news_fetcher.py` and `tools/news_intelligence.py`: web scraping, event detection, impact scoring.
- Implemented `tools/sentiment_analyzer.py`: VADER + TextBlob dual-scorer with compound sentiment score.
- Implemented `tools/macro_data.py`: RBI rate, inflation, NIFTY/SENSEX performance, sector indices.
- Implemented `tools/risk_management.py`: ATR-based stop loss, 2% risk rule position sizing, risk-reward assessor.
- Integrated Exa MCP HTTP API (`tools/exa_research.py`) for live web research.
- Unit tested all tools with real NSE stock symbols (RELIANCE, TCS, ITC).

**Deliverables:**
- Fully functional data and tools layer.
- Unit test suite for all tools.

---

### Stage 3: Multi-Agent Implementation (Weeks 8–12)

**Activities:**
- Implemented all 10 specialist agents using the OpenAI Agents SDK (`Agent`, `Runner`, `ModelSettings`).
- Wrote detailed system instruction prompts for each agent covering their domain expertise, analysis framework, and output format.
- Assigned curated tool sets to each agent (e.g., Technical Analyst gets `get_technical_indicators`, `get_support_resistance`, `analyze_trend`).
- Implemented `agents/pipeline_orchestrator.py`: sequential runner with Phase 0 (raw data), Phase 1 (data agents), Phase 2 (debate), Phase 3 (risk), and Final Step (PDF).
- Implemented `determine_recommendation()`: regex-based extraction of BUY/SELL/HOLD + confidence from debate verdict.
- Implemented `extract_technical_metrics()` and `extract_risk_metrics()`: hybrid extraction using structured tool outputs first, with text regex fallback.
- Implemented `extract_citations()`: URL extraction from news intelligence output for PDF source citations.
- Tested pipeline end-to-end with multiple stocks; resolved agent prompt engineering issues.

**Deliverables:**
- All 10 agent implementations.
- Working end-to-end pipeline (CLI mode: `python main.py "Analyze RELIANCE"`).

---

### Stage 4: PDF Report Generation and Web Application (Weeks 13–17)

**Activities:**
- Implemented `pdf_generator.py` using ReportLab: A4 layout, colour-coded recommendation badge, metrics tables, trade setup card, bull/bear factor lists, news summary, citations, footer disclaimer.
- Designed `StockReportData` Pydantic model for type-safe report data.
- Implemented `web_server.py`: ThreadingHTTPServer, REST API endpoints, async job queue with background threads, per-job progress event streaming.
- Implemented SQLite schema (`ensure_schema()`): users, sessions, chat_history, reports tables with admin bootstrap.
- Implemented secure authentication: PBKDF2-SHA256 password hashing (240,000 iterations), session tokens (secrets.token_urlsafe), 7-day HttpOnly cookies.
- Designed and implemented the single-page application (`chat.html`): auth card, chat workspace, accuracy builder, sidebar, admin panel, responsive CSS grid layout.
- Implemented frontend polling (`setInterval`, `pollJobStatus`) for real-time progress updates during analysis.

**Deliverables:**
- Professional PDF report generator.
- Full-stack web application (server + frontend SPA).
- Secure authentication and session system.
- Admin dashboard.

---

### Stage 5: Testing, Optimisation, and Documentation (Weeks 18–20)

**Activities:**
- End-to-end integration testing with 10+ Indian stocks across sectors (Banking: HDFCBANK, SBIN; IT: TCS, INFY; FMCG: ITC, HINDUNILVR; Energy: RELIANCE, ONGC; Pharma: SUNPHARMA).
- Identified and fixed LLM hallucination of numerical data → resolved by fetching authoritative yfinance data in Phase 0 and using it directly in PDF generation.
- Fixed stop-loss validation: added check `if stop_loss >= current_price: discard` to prevent logically impossible stops.
- Optimised PDF layout for readability and professional appearance; generated 14+ sample reports (visible in `reports/` folder).
- Stress tested the web server with concurrent users; confirmed thread-safety of `JOBS` dictionary with `threading.Lock()`.
- Tested admin panel: stats aggregation, user management, report access controls.
- Wrote project documentation and user guide.
- Added `test_api.py` for API validation testing.

**Deliverables:**
- Tested and optimised system.
- 14+ sample PDF reports in `reports/` directory.
- Complete project documentation.

---

## 7. DESIGN AND IMPLEMENTATION

### 7.1 System Architecture

The system follows a **layered pipeline architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEB FRONTEND (SPA)                          │
│            chat.html  —  Vanilla JS, CSS Grid, Fetch API           │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP REST (JSON)
┌───────────────────────────▼─────────────────────────────────────────┐
│                   WEB SERVER (web_server.py)                        │
│       ThreadingHTTPServer  |  REST API  |  Auth  |  SQLite DB       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ asyncio.run()
┌───────────────────────────▼─────────────────────────────────────────┐
│              PIPELINE ORCHESTRATOR (pipeline_orchestrator.py)       │
│                                                                     │
│  Phase 0: yfinance Raw Data Fetch (Authoritative)                  │
│                          │                                          │
│  Phase 1: ┌──────────────┼──────────────────────────────┐          │
│           │ Fundamental  │ Technical  │ News Intel        │          │
│           │ Sentiment    │ Macro      │ Document          │          │
│           └──────────────┴──────────────────────────────┘          │
│                          │                                          │
│  Phase 2:         Bull Agent ◄──► Bear Agent                       │
│                          │                                          │
│                    Debate Judge                                     │
│                          │                                          │
│  Phase 3:          Risk Manager                                    │
│                          │                                          │
│  Final:           PDF Generator                                    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                     TOOLS LAYER (tools/)                            │
│  yfinance | ta library | VADER | TextBlob | BeautifulSoup | Exa MCP │
└─────────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                   EXTERNAL DATA SOURCES                             │
│         NSE/BSE (via Yahoo Finance)  |  Exa Web Search              │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Data Flow

```
User Query (natural language)
        │
        ▼
Symbol Extraction (regex + keyword matching)
        │
        ▼
Phase 0: yfinance fetch → raw_data dict (price, P/E, ROE, 52W H/L …)
        │
        ▼
Phase 1: 6 Data Agents → textual analysis outputs
        │
        ▼
Phase 2: Bull + Bear build cases → Judge delivers verdict
        │
        ▼
Phase 3: Risk Manager → stop-loss, target, position sizing
        │
        ▼
Metric Extraction (tools first → regex fallback)
        │
        ▼
StockReportData assembly (raw_data overrides LLM for numbers)
        │
        ▼
PDF Generation (ReportLab) → saved to reports/
        │
        ▼
Response to user: Formatted text + PDF URL
```

### 7.3 Agent Design Pattern

Each agent follows the **ReAct (Reasoning + Acting)** pattern:

```
Agent receives task prompt
        │
        ▼
LLM reasons about what data it needs
        │
        ▼
Calls tool(s) → receives structured JSON response
        │
        ▼
LLM analyses tool output
        │
        ▼
Calls additional tools if needed (up to MAX_TURNS = 25)
        │
        ▼
LLM generates final textual analysis
        │
        ▼
final_output returned to pipeline
```

### 7.4 Authentication Design

```
Client                    Server
  │                         │
  │──POST /api/login ──────►│
  │  {username, password}   │
  │                         │ PBKDF2-SHA256(password, salt, 240000 iter)
  │                         │ Compare with stored hash
  │                         │ Generate session token (secrets.token_urlsafe)
  │                         │ Store in sessions table (7-day expiry)
  │◄── 200 OK ──────────────│
  │    Set-Cookie: stock_session=<token>; HttpOnly; SameSite=Lax
  │                         │
  │──GET /api/me ──────────►│
  │  Cookie: stock_session=<token>
  │                         │ Validate token + expiry from DB
  │◄── {authenticated: true, user: {...}}
```

### 7.5 Async Job System

Analysis takes 2–5 minutes. To avoid HTTP timeout, the system uses an async job pattern:

```
POST /api/chat/start  →  Creates job (UUID), spawns background thread, returns job_id
                                │
GET /api/chat/status?job_id=X   │  ← Client polls every 1.8 seconds
        │                       │
        │       Progress events appended by callback
        │                       │
        ▼                       ▼
Status: queued → running → done / failed
```

---

## 8. SYSTEM REQUIREMENTS

### 8.1 Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| Processor | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 or better |
| RAM | 4 GB | 8 GB or more |
| Storage | 2 GB free space | 5 GB free space |
| Network | 5 Mbps internet | 20 Mbps or better |
| Display | 1280 × 720 | 1920 × 1080 |

### 8.2 Software Requirements

| Component | Requirement |
|---|---|
| Operating System | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| Python | 3.11 or higher |
| Browser | Chrome 90+, Firefox 90+, Edge 90+, Safari 15+ |

### 8.3 Python Dependencies

| Package | Version | Purpose |
|---|---|---|
| `openai-agents` | ≥ 0.6.0 | Multi-agent orchestration SDK |
| `openai` | ≥ 1.0.0 | GPT-4o-mini LLM API |
| `yfinance` | ≥ 0.2.40 | Real-time NSE/BSE stock data |
| `pandas` | ≥ 2.0.0 | Data manipulation |
| `numpy` | ≥ 1.24.0 | Numerical computation |
| `ta` | ≥ 0.11.0 | Technical analysis indicators |
| `requests` | ≥ 2.31.0 | HTTP client for news fetching |
| `beautifulsoup4` | ≥ 4.12.0 | HTML parsing for news scraping |
| `lxml` | ≥ 5.0.0 | XML/HTML parser backend |
| `reportlab` | ≥ 4.0.0 | PDF generation |
| `python-dotenv` | ≥ 1.0.0 | Environment variable management |
| `vaderSentiment` | ≥ 3.3.2 | Rule-based sentiment analysis |
| `textblob` | ≥ 0.17.1 | ML-based sentiment analysis |
| `pydantic` | ≥ 2.0.0 | Data validation and schemas |
| `python-dateutil` | ≥ 2.8.0 | Date parsing |

### 8.4 API Requirements

| Service | Requirement |
|---|---|
| OpenAI API Key | Required — set as `OPENAI_API_KEY` in `.env` |
| Model Access | GPT-4o-mini (configurable via `MODEL_NAME`) |
| Exa MCP | Optional — configurable via `EXA_MCP_HTTP_URL` |
| Yahoo Finance | No API key required (public data via yfinance) |

### 8.5 Network Requirements

- Outbound HTTPS access to `api.openai.com` (OpenAI API).
- Outbound HTTPS access to `query2.finance.yahoo.com` (yfinance).
- Outbound HTTPS access to `mcp.exa.ai` (Exa MCP, optional).
- Port 8000 available for the local web server.

---

## 9. USE CASE DIAGRAM

### 9.1 Actors

| Actor | Description |
|---|---|
| **Guest** | Unauthenticated user visiting the web application |
| **User** | Registered and logged-in investor using the platform |
| **Admin** | Privileged user with access to user management and system stats |
| **AI Pipeline** | The automated 10-agent analysis pipeline (system actor) |

---

### 9.2 Use Case Diagram (Text Representation)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    INDIAN STOCK INTELLIGENCE STUDIO                         ║
║                         USE CASE DIAGRAM                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────┐        ┌──────────────────────────────────────────────────────┐
  │  GUEST  │        │                    SYSTEM BOUNDARY                   │
  └────┬────┘        │                                                      │
       │             │  ┌─────────────────────────────────┐                 │
       ├────────────►│  │  UC-01: Register Account        │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-02: Login                   │                 │
       │             │  └─────────────────────────────────┘                 │
       │             └──────────────────────────────────────────────────────┘
       │
  ┌────▼────┐        ┌──────────────────────────────────────────────────────┐
  │  USER   │        │                    SYSTEM BOUNDARY                   │
  └────┬────┘        │                                                      │
       │             │  ┌─────────────────────────────────┐                 │
       ├────────────►│  │  UC-03: Submit Stock Query      │◄── extends ──┐  │
       │             │  └─────────────────────────────────┘              │  │
       │             │                    │                               │  │
       │             │                    │ includes                      │  │
       │             │                    ▼                               │  │
       │             │  ┌─────────────────────────────────┐              │  │
       │             │  │  UC-04: Run 10-Agent Pipeline   │              │  │
       │             │  │  (AI Pipeline Actor)            │              │  │
       │             │  └─────────────────────────────────┘              │  │
       │             │                    │                               │  │
       │             │          ┌─────────┼─────────┐                    │  │
       │             │          ▼         ▼         ▼                    │  │
       │             │  ┌──────────┐ ┌────────┐ ┌────────┐              │  │
       │             │  │UC-05:    │ │UC-06:  │ │UC-07:  │              │  │
       │             │  │Fundamental│ │Techni- │ │News &  │              │  │
       │             │  │Analysis  │ │cal     │ │Sentiment│              │  │
       │             │  └──────────┘ │Analysis│ │Analysis│              │  │
       │             │               └────────┘ └────────┘              │  │
       │             │          ┌─────────┼─────────┐                    │  │
       │             │          ▼         ▼         ▼                    │  │
       │             │  ┌──────────┐ ┌────────┐ ┌────────┐              │  │
       │             │  │UC-08:    │ │UC-09:  │ │UC-10:  │              │  │
       │             │  │Macro     │ │Bull vs │ │Risk    │              │  │
       │             │  │Analysis  │ │Bear    │ │Mgmt    │              │  │
       │             │  └──────────┘ │Debate  │ └────────┘              │  │
       │             │               └────────┘                          │  │
       │             │                    │                               │  │
       │             │                    ▼                               │  │
       │             │  ┌─────────────────────────────────┐              │  │
       ├────────────►│  │  UC-11: Download PDF Report     │──────────────┘  │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-12: View Chat History       │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-13: View My Reports         │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-14: Logout                  │                 │
       │             │  └─────────────────────────────────┘                 │
       │             └──────────────────────────────────────────────────────┘
       │
  ┌────▼────┐        ┌──────────────────────────────────────────────────────┐
  │  ADMIN  │        │                    SYSTEM BOUNDARY                   │
  └────┬────┘        │                                                      │
       │             │  ┌─────────────────────────────────┐                 │
       ├────────────►│  │  UC-15: View Admin Dashboard    │                 │
       │             │  │  (Users, Reports, Chats stats)  │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-16: Manage Users            │                 │
       │             │  │  (View roles, login history)    │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-17: View All Reports        │                 │
       │             │  │  (Across all users)             │                 │
       │             │  └─────────────────────────────────┘                 │
       │             │                                                      │
       ├────────────►│  ┌─────────────────────────────────┐                 │
       │             │  │  UC-18: Check System Health     │                 │
       │             │  │  (API key, Exa status)          │                 │
       │             │  └─────────────────────────────────┘                 │
       │             └──────────────────────────────────────────────────────┘
```

---

### 9.3 Use Case Descriptions

| Use Case ID | Name | Actor | Description |
|---|---|---|---|
| UC-01 | Register Account | Guest | User provides username (3-32 alphanumeric chars) and password (≥ 8 chars). Password hashed with PBKDF2-SHA256 and stored. Session created automatically. |
| UC-02 | Login | Guest | User submits credentials. Server verifies PBKDF2 hash. Session token issued via HttpOnly cookie. |
| UC-03 | Submit Stock Query | User | User types natural language query in chat box. System extracts stock symbol using regex + keyword matching. |
| UC-04 | Run 10-Agent Pipeline | AI Pipeline | Pipeline orchestrator executes all 10 agents sequentially across 3 phases. Progress events emitted via callback. |
| UC-05 | Fundamental Analysis | AI Pipeline | Fundamental Analyst fetches and analyses P/E, P/B, ROE, debt, growth, dividend metrics. |
| UC-06 | Technical Analysis | AI Pipeline | Technical Analyst computes RSI, MACD, MAs, Bollinger Bands, ATR, support/resistance, trend. |
| UC-07 | News & Sentiment Analysis | AI Pipeline | News Intelligence + Sentiment Agents fetch live news, detect events, score sentiment (VADER + TextBlob). |
| UC-08 | Macro Analysis | AI Pipeline | Macro Analyst evaluates RBI policy, inflation, NIFTY/SENSEX performance, sector context. |
| UC-09 | Bull vs. Bear Debate | AI Pipeline | Bull and Bear Agents argue opposing cases; Debate Judge delivers BUY/SELL/HOLD verdict + confidence %. |
| UC-10 | Risk Management | AI Pipeline | Risk Manager calculates stop-loss (ATR-based), target price, position sizing, risk-reward ratio. |
| UC-11 | Download PDF Report | User | User clicks PDF link in chat response to view/download the generated research report. |
| UC-12 | View Chat History | User | User browses previous queries and analysis results in the sidebar. |
| UC-13 | View My Reports | User | User views list of all generated PDF reports with stock symbol, recommendation, and timestamp. |
| UC-14 | Logout | User | Session invalidated (deleted from DB); user returned to login screen. |
| UC-15 | View Admin Dashboard | Admin | Admin sees aggregate stats: total users, admins, reports, chats, active users (7 days). |
| UC-16 | Manage Users | Admin | Admin views all registered users with role, report count, chat count, and last login time. |
| UC-17 | View All Reports | Admin | Admin views all PDF reports generated across all users with ownership info. |
| UC-18 | Check System Health | Admin | Admin checks `/health` endpoint: OpenAI key status, Exa MCP configuration, DB path. |

---

## 10. RESULTS AND DISCUSSION

### 10.1 System Performance

The system was tested with 15+ Indian stocks across 7 sectors:

| Stock | Sector | Recommendation | Confidence | PDF Generated | Time (approx.) |
|---|---|---|---|---|---|
| RELIANCE | Energy / Conglom. | SELL | 72% | ✅ | ~3 min |
| ITC | FMCG | SELL | 68% | ✅ | ~3 min |
| SILVER (GROWWSLVR) | Commodity ETF | SELL | 65% | ✅ | ~2.5 min |
| HDFCBANK | Banking | HOLD | 60% | ✅ | ~3 min |

*(Sample results — recommendations depend on market conditions at time of analysis)*

### 10.2 PDF Report Quality

Generated reports (14+ stored in `reports/`) include:
- Colour-coded recommendation badges (BUY = green, SELL = red, HOLD = orange).
- Complete metrics tables with live yfinance data.
- Trade setup cards with entry, target, stop-loss, risk-reward, and win probability.
- Structured bull and bear factor lists from the debate.
- News summary with clickable Exa source citations.
- Professional A4 layout suitable for sharing with advisors or team members.

### 10.3 Data Accuracy

A key achievement of this project is **zero LLM hallucination of numerical financial data**. By:
1. Fetching all price and fundamental data from yfinance in Phase 0 before any LLM invocation.
2. Storing this as `raw_data` (authoritative).
3. Using `raw_data` values directly in `StockReportData` for PDF generation, overriding any LLM-extracted numbers.
4. Validating stop-loss (must be < current price) and 52-week ranges (high ≥ price ≥ low).

The system guarantees that all numerical values in the PDF (price, P/E, ROE, 52W H/L) are sourced directly from the exchange — not generated by the LLM.

### 10.4 Agent Participation Rate

In all successful runs, **9 out of 10 agents** completed successfully (News Intelligence + Sentiment counted separately). The pipeline raises a `RuntimeError` if 0 agents succeed, preventing misleading reports from being generated.

### 10.5 Security Assessment

- Passwords are hashed with PBKDF2-SHA256 at 240,000 iterations — meeting NIST SP 800-132 recommendations.
- Session tokens are cryptographically random (32-byte URL-safe base64 via `secrets.token_urlsafe`).
- Report files are served only after ownership verification (user can only access their own reports; admin can access all).
- Path traversal is prevented by resolving PDF paths within the `REPORTS_DIR` and rejecting any path that escapes.
- Session cookies are HttpOnly and SameSite=Lax, preventing XSS-based session theft.

### 10.6 Comparative Analysis (Proposed vs. Existing)

| Feature | Existing Systems | Proposed System |
|---|---|---|
| Analysis Dimensions | 1–2 (siloed) | 6 (integrated pipeline) |
| AI Reasoning | ❌ None | ✅ 10 specialist agents |
| Bull vs. Bear Debate | ❌ None | ✅ Adversarial debate + judge |
| PDF Report Generation | ❌ None | ✅ Professional A4 PDF |
| Data Accuracy Guarantee | N/A | ✅ yfinance authoritative source |
| Real-time News with Citations | ❌ None | ✅ Exa MCP live research |
| Confidence Score | ❌ None | ✅ 0–100% with rationale |
| Risk-Reward Quantification | ❌ None | ✅ ATR-based, position sizing |
| User Auth + History | ❌ None | ✅ SQLite-backed, 7-day sessions |
| Admin Panel | ❌ None | ✅ Multi-user management |
| Natural Language Input | ❌ None | ✅ Free-form queries |

### 10.7 Limitations and Future Work

**Current Limitations:**
1. Analysis time of 2–5 minutes may feel slow for high-frequency traders.
2. GPT-4o-mini may occasionally generate generic analysis when tool data is unavailable (e.g., stocks with limited yfinance coverage).
3. Exa MCP is optional; without it, news quality depends on BeautifulSoup scraping.
4. No portfolio tracking — users cannot manage an actual portfolio with P&L tracking.
5. No charting — the web UI does not display interactive price charts.

**Future Enhancements:**
1. **Real-time WebSocket streaming** — Replace polling with WebSocket for instant progress updates.
2. **Interactive charts** — Integrate TradingView Lightweight Charts or Chart.js for price and indicator visualisation.
3. **Portfolio management** — Track holdings, average cost, unrealised P&L, and portfolio-level risk.
4. **Watchlist and alerts** — Email/SMS alerts when a stock triggers a BUY/SELL signal.
5. **Historical backtesting** — Validate agent recommendations against historical price movements.
6. **Mobile app** — React Native or Flutter app for on-the-go access.
7. **Voice interface** — Speech-to-text for query submission.
8. **Parallel agent execution** — Run Phase 1 agents concurrently with `asyncio.gather()` to reduce analysis time to ~1 minute.

---

## CONCLUSION

The Indian Stock Intelligence Studio successfully demonstrates the viability of multi-agent AI architectures for democratising institutional-grade equity research. By deploying ten specialist AI agents in a structured sequential pipeline, the system replicates the collaborative reasoning of a professional equity research team — covering fundamentals, technicals, news sentiment, macroeconomics, document analysis, adversarial debate, and risk management — in a fully automated, accessible web application.

The system's key contributions are:
1. A novel **adversarial debate mechanism** (Bull Agent vs. Bear Agent → Judge) that stress-tests investment theses from opposing perspectives.
2. A **data authority separation** strategy that guarantees numerical accuracy by sourcing all financial figures directly from Yahoo Finance, insulating the analysis from LLM hallucination.
3. A **production-ready full-stack web application** with secure authentication, chat persistence, admin management, and automated PDF report generation.

The project proves that with the right architecture, AI can serve as a powerful equaliser in financial markets — giving retail investors in India access to the same quality of analysis that has historically been exclusive to institutional participants.

---

*This document was prepared as part of the Final Year B.E./B.Tech Project in Computer Science and Engineering.*  
*Academic Year: 2025–2026*

