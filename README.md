# Indian Stock Analyst Agent

An AI-powered stock analysis agent for Indian markets (NSE & BSE) built with OpenAI Agents SDK. The agent analyzes stocks using real-time data, fundamental analysis, technical indicators, and news sentiment to provide BUY/SELL/HOLD recommendations with professional PDF reports.

## Features

- **Real-time Stock Data**: Fetches current prices, volumes, and market data from NSE/BSE
- **Fundamental Analysis**: Analyzes P/E ratio, P/B ratio, ROE, debt levels, growth metrics
- **Technical Analysis**: Calculates RSI, MACD, Moving Averages, Bollinger Bands, Support/Resistance
- **News Sentiment**: Gathers and analyzes recent news affecting the stock
- **PDF Reports**: Generates professional PDF reports with recommendations
- **Interactive Chat**: Conversational interface for stock analysis

## Project Structure

```
Stock Agent/
├── main.py                 # Entry point - run this to start
├── agent.py                # Main agent definition
├── config.py               # Configuration settings
├── pdf_generator.py        # PDF report generation
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── tools/
│   ├── __init__.py
│   ├── stock_data.py       # Stock data fetching tools
│   ├── technical_analysis.py # Technical indicators
│   └── news_fetcher.py     # News fetching tools
├── docs/
│   ├── OPENAI_AGENTS_SDK_REFERENCE.md
│   └── INDIAN_STOCK_API_REFERENCE.md
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
- "Should I buy RELIANCE?"
- "Analyze TCS stock fundamentals and technicals"
- "Is HDFCBANK a good buy at current levels?"
- "I bought INFY at 1600, current price is 1450. Should I hold or sell?"
- "Compare ICICIBANK and AXISBANK"
- "What are the support and resistance levels for SBIN?"
- "Give me a complete analysis of TITAN with PDF report"

## Supported Stock Symbols

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
- **LLM**: OpenAI GPT-4o (requires API key)

## Analysis Components

### Fundamental Analysis
- P/E Ratio (Trailing & Forward)
- P/B Ratio
- Market Cap
- ROE, ROA
- Debt to Equity
- Dividend Yield
- Revenue & Earnings Growth
- Analyst Recommendations

### Technical Analysis
- RSI (14-period)
- MACD with Signal Line
- Moving Averages (SMA 20, 50, 200)
- Bollinger Bands
- ATR (Volatility)
- Support & Resistance Levels
- Fibonacci Retracement
- Trend Direction & Strength

### PDF Report Contents
- Recommendation (BUY/SELL/HOLD)
- Confidence Score
- Current Price & Targets
- Fundamental Metrics Table
- Technical Indicators Table
- Positive Factors
- Risk Factors
- Detailed Analysis
- Disclaimer

## Configuration

Edit `config.py` to customize:
- Model settings (temperature, max turns)
- Technical analysis parameters
- PDF output directory

## Requirements

- Python 3.10+
- OpenAI API key (with GPT-4o access recommended)
- Internet connection for real-time data

## Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. Stock investments are subject to market risks. Always consult a qualified financial advisor before making investment decisions.

## License

MIT License
