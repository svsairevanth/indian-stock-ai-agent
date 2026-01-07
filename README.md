# Indian Stock Analyst Agent

An AI-powered **advanced multi-agent** stock analysis system for Indian markets (NSE & BSE) built with OpenAI Agents SDK. This is the most comprehensive stock analysis system available, featuring 10 specialized agents coordinated by an Orchestrator to provide thorough BUY/SELL/HOLD recommendations with professional PDF reports.

## Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │       ORCHESTRATOR AGENT            │
                                    │   Coordinates all analysis phases   │
                                    └─────────────────┬───────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
          ┌─────────▼─────────┐             ┌────────▼────────┐             ┌──────────▼──────────┐
          │   ANALYSIS TEAM   │             │   DEBATE TEAM   │             │    RISK TEAM        │
          └─────────┬─────────┘             └────────┬────────┘             └──────────┬──────────┘
                    │                                │                                 │
    ┌───────────────┼───────────────┐       ┌───────┼───────┐               ┌─────────┼─────────┐
    │       │       │       │       │       │       │       │               │                   │
┌───▼───┐┌──▼──┐┌───▼───┐┌──▼──┐┌───▼───┐┌──▼──┐┌───▼───┐┌──▼──┐      ┌─────▼─────┐    ┌────────▼────────┐
│ FUND  ││TECH ││ SENT  ││MACRO││  DOC  ││BULL ││ BEAR  ││JUDGE│      │   RISK    │    │   PORTFOLIO     │
│ANALYST││ANAL ││ANALYST││ANAL ││ANALYST││ADVOC││ ADVOC ││     │      │  MANAGER  │    │    ANALYST      │
│       ││     ││       ││     ││       ││     ││       ││     │      │           │    │                 │
│P/E,ROE││RSI  ││VADER  ││RBI  ││Q.Res  ││Bull ││Bear   ││Final│      │Position   │    │Health Score     │
│Debt   ││MACD ││TextBlb││FII  ││Peer   ││Case ││Case   ││Verd.│      │Sizing     │    │Diversification  │
│Growth ││Trend││News   ││DII  ││Announce│└─────┘└───────┘└─────┘      │Stop Loss  │    │Correlation      │
└───────┘└─────┘└───────┘└─────┘└───────┘                              │Risk-Reward│    │Rebalancing      │
                                                                       └───────────┘    └─────────────────┘
```

## Features

### Core Analysis
- **10-Agent Architecture**: Comprehensive analysis from multiple specialized perspectives
- **Real-time Stock Data**: Current prices, volumes, and market data from NSE/BSE
- **Fundamental Analysis**: P/E, P/B, ROE, debt, growth, peer comparison
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Support/Resistance, Fibonacci
- **Sentiment Analysis**: VADER + TextBlob combined sentiment scoring

### Advanced Features (NEW)
- **Bull/Bear Debate**: Adversarial agents argue both sides for balanced analysis
- **Macro Analysis**: RBI policy, inflation, FII/DII flows, global context
- **Document Analysis**: Quarterly results, company announcements, peer comparison
- **Risk Management**: Position sizing, ATR-based stop loss, risk-reward assessment
- **Portfolio Analysis**: Health score, diversification, correlation, rebalancing

### Output
- **Professional PDF Reports**: Comprehensive reports with all analysis
- **Weighted Scoring System**: Objective recommendations based on multi-factor scoring
- **Position Sizing**: Exact share quantities for your portfolio size

## Project Structure

```
Stock Agent/
├── main.py                 # Entry point - run this to start
├── agent.py                # Multi-agent system configuration
├── config.py               # Configuration settings
├── pdf_generator.py        # PDF report generation
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
│
├── agents/                 # All 10 specialized agents
│   ├── __init__.py
│   ├── orchestrator.py     # Main orchestrator + quick version
│   ├── fundamental_analyst.py  # Fundamental analysis
│   ├── technical_analyst.py    # Technical analysis
│   ├── sentiment_analyst.py    # News sentiment analysis
│   ├── macro_analyst.py        # Macroeconomic analysis (NEW)
│   ├── document_analyst.py     # Document/filing analysis (NEW)
│   ├── bull_agent.py           # Bull advocate (NEW)
│   ├── bear_agent.py           # Bear advocate (NEW)
│   ├── debate_judge.py         # Debate synthesizer (NEW)
│   ├── risk_manager.py         # Risk management (NEW)
│   └── portfolio_analyst.py    # Portfolio analysis (NEW)
│
├── models/                 # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py          # Structured output models
│
├── tools/                  # 30+ analysis tools
│   ├── __init__.py
│   ├── stock_data.py       # Stock data fetching
│   ├── technical_analysis.py # Technical indicators
│   ├── news_fetcher.py     # News fetching
│   ├── sentiment_analyzer.py # VADER + TextBlob sentiment
│   ├── macro_data.py       # India macro indicators (NEW)
│   ├── portfolio_analyzer.py # Portfolio analysis (NEW)
│   ├── risk_management.py  # Position sizing/stops (NEW)
│   └── document_analyzer.py # Company filings (NEW)
│
├── docs/
│   ├── OPENAI_AGENTS_SDK_REFERENCE.md
│   ├── INDIAN_STOCK_API_REFERENCE.md
│   ├── RESEARCH_ANALYSIS.md
│   └── IMPLEMENTATION_REFERENCE.md
│
└── reports/                # Generated PDF reports
```

## Installation

1. **Clone/Download the project**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key**:
   ```bash
   # Option 1: Environment variable
   export OPENAI_API_KEY=your-api-key-here

   # Option 2: Create .env file
   cp .env.example .env
   # Edit .env and add your API key
   ```

## Usage

### Interactive Mode
```bash
python main.py
```
This starts an interactive session where you can ask questions about stocks.

### Single Query Mode
```bash
python main.py "Should I buy RELIANCE?"
python main.py "Analyze TCS for long-term investment"
python main.py "I own INFY at 1500, should I hold or sell?"
```

### Example Queries

**Stock Analysis:**
- "Should I buy RELIANCE?"
- "Analyze TCS stock fundamentals and technicals"
- "Is HDFCBANK a good buy at current levels?"
- "I bought INFY at 1600, current price is 1450. Should I hold or sell?"

**Portfolio Analysis:**
- "Analyze my portfolio: RELIANCE 100 shares at 2500, TCS 50 shares at 3500"
- "Is my portfolio well diversified?"
- "Suggest rebalancing for my holdings"

**Comparisons:**
- "Compare ICICIBANK and AXISBANK"
- "Which is better: TCS or INFY?"

**Specific Analysis:**
- "What are the support and resistance levels for SBIN?"
- "What is the macro environment for IT stocks?"
- "How did TITAN's quarterly results compare to peers?"

## Analysis Workflow

When you analyze a stock, the system runs through 4 phases:

### Phase 1: Data Gathering
1. **Fundamental Analyst** → Valuation, profitability, growth metrics
2. **Technical Analyst** → Price action, indicators, support/resistance
3. **Sentiment Analyst** → News sentiment from multiple sources
4. **Macro Analyst** → RBI policy, inflation, FII/DII flows
5. **Document Analyst** → Quarterly results, peer comparison

### Phase 2: Debate
6. **Bull Advocate** → Builds the strongest case FOR buying
7. **Bear Advocate** → Builds the strongest case AGAINST buying
8. **Debate Judge** → Evaluates both cases, determines winner

### Phase 3: Risk Assessment
9. **Risk Manager** → Position sizing, stop loss, risk-reward ratio

### Phase 4: Synthesis
10. **Orchestrator** → Combines all inputs, generates final recommendation
11. **PDF Report** → Professional report with all analysis

## Scoring System

The final recommendation uses weighted scoring:

| Factor | Weight | Description |
|--------|--------|-------------|
| Fundamental | 30% | P/E, ROE, debt, growth |
| Technical | 25% | RSI, MACD, trend, support |
| Sentiment | 15% | News sentiment score |
| Macro | 15% | Economic environment |
| Debate | 15% | Bull/Bear winner adjustment |

**Recommendation Thresholds:**
- Score >= 8.0: **STRONG BUY**
- Score >= 6.5: **BUY**
- Score >= 4.5: **HOLD**
- Score >= 3.0: **SELL**
- Score < 3.0: **STRONG SELL**

## Supported Stocks

### NSE Stocks
Use the stock symbol directly (e.g., `RELIANCE`, `TCS`, `INFY`)
The agent auto-adds `.NS` suffix for NSE.

### BSE Stocks
Add `.BO` suffix (e.g., `RELIANCE.BO`, `TCS.BO`)

### Popular Stocks
- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- HINDUNILVR, SBIN, BHARTIARTL, ITC, KOTAKBANK
- LT, AXISBANK, ASIANPAINT, MARUTI, TITAN
- SUNPHARMA, BAJFINANCE, WIPRO, HCLTECH

### Indices
- NIFTY50 (^NSEI)
- SENSEX (^BSESN)
- NIFTY BANK (^NSEBANK)

## API Data Sources

- **Stock Data**: Yahoo Finance via yfinance library (free, no API key needed)
- **News**: Google News RSS + Yahoo Finance news
- **Macro Data**: Simulated RBI/government data (extend for real APIs)
- **LLM**: OpenAI GPT-4o (requires API key)

## ⚠️ Data Limitations & Accuracy

> **IMPORTANT**: This system uses a mix of real-time and simulated data. Understand the differences before making investment decisions.

### Real-Time Data (HIGH Reliability)
These data sources fetch **LIVE data** from APIs:

| Data Type | Source | Freshness |
|-----------|--------|-----------|
| Stock Prices | Yahoo Finance | Real-time (15-min delay) |
| Technical Indicators | Calculated from yfinance | Real-time |
| Nifty/Sensex Benchmark | Yahoo Finance | Real-time |
| Sector Indices | Yahoo Finance | Real-time |
| Global Markets (US, Gold, Oil) | Yahoo Finance | Real-time |
| Stock Fundamentals (P/E, ROE) | Yahoo Finance | Quarterly updated |

### Simulated Data (FOR DEMONSTRATION ONLY)
These data sources use **HARDCODED REFERENCE DATA** and may be outdated:

| Data Type | Last Updated | What to Use Instead |
|-----------|--------------|---------------------|
| India Macro Indicators (RBI rates, inflation) | 2024-12-06 | [RBI Website](https://www.rbi.org.in), [MOSPI](https://www.mospi.gov.in) |
| FII/DII Activity | 2024-12-06 | [NSE FII/DII Reports](https://www.nseindia.com/reports/fii-dii) |
| Company Announcements | 2024-12-06 | [BSE Announcements](https://www.bseindia.com/corporates/ann.html) |
| Management Commentary | 2024-12-06 | Company quarterly earnings calls |
| Peer Comparison Mappings | 2024-12-06 | [Screener.in](https://www.screener.in), [Trendlyne](https://trendlyne.com) |

### How to Identify Simulated Data
All simulated data outputs include a disclaimer block:
```json
{
  "disclaimer": {
    "warning": "SIMULATED DATA - For demonstration only",
    "message": "...",
    "recommendation": "Verify with official sources..."
  }
}
```

### Data Version Tracking
See `config/data_versions.json` for complete tracking of all data sources and their freshness.

### Upgrading to Real Data
To replace simulated data with real APIs:
1. **FII/DII**: Scrape NSE daily reports or use paid data providers
2. **Macro Data**: Integrate RBI API or Trading Economics API
3. **Announcements**: Use BSE/NSE corporate filing APIs

## Configuration

Edit `config.py` to customize:
- Model settings (temperature, max turns)
- Technical analysis parameters
- PDF output directory

## Requirements

- Python 3.10+
- OpenAI API key (with GPT-4o access recommended)
- Internet connection for real-time data

## What Makes This Better Than Others

Based on research of leading platforms (Liquide, TradingAgents, MarketSenseAI):

| Feature | Liquide | TradingAgents | This System |
|---------|---------|---------------|-------------|
| Multi-Agent | No | Yes | Yes (10 agents) |
| Bull/Bear Debate | No | Yes | Yes |
| Portfolio Health | Yes | No | Yes |
| Macro Analysis | No | No | Yes |
| Risk Management | Basic | Yes | Yes (comprehensive) |
| Document Analysis | No | No | Yes |
| Peer Comparison | Basic | No | Yes |
| PDF Reports | No | No | Yes |

## Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. Stock investments are subject to market risks. Always consult a qualified financial advisor before making investment decisions.

## License

MIT License
