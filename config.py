"""
Configuration settings for the Indian Stock Analyst Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Exa MCP HTTP (no API key required when endpoint is already provisioned)
EXA_MCP_HTTP_URL = os.getenv(
    "EXA_MCP_HTTP_URL",
    "https://mcp.exa.ai/mcp?tools=web_search_exa,get_code_context_exa,crawling_exa,company_research_exa,linkedin_search_exa,deep_researcher_start,deep_researcher_check",
)
EXA_HTTP_TIMEOUT_SECONDS = _env_int("EXA_HTTP_TIMEOUT_SECONDS", 25)
EXA_DEEP_RESEARCH_TIMEOUT_SECONDS = _env_int("EXA_DEEP_RESEARCH_TIMEOUT_SECONDS", 120)
EXA_DEEP_RESEARCH_POLL_INTERVAL_SECONDS = _env_int("EXA_DEEP_RESEARCH_POLL_INTERVAL_SECONDS", 6)

# Stock Exchange Configuration
NSE_SUFFIX = ".NS"
BSE_SUFFIX = ".BO"

# Common Indian Indices
INDICES = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY_BANK": "^NSEBANK",
    "NIFTY_IT": "^CNXIT",
    "NIFTY_PHARMA": "^CNXPHARMA",
    "NIFTY_AUTO": "^CNXAUTO",
}

# Popular NSE Stocks (for quick reference)
POPULAR_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "MARUTI": "MARUTI.NS",
    "TITAN": "TITAN.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "WIPRO": "WIPRO.NS",
    "HCLTECH": "HCLTECH.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
}

# Technical Analysis Settings
TA_SETTINGS = {
    "RSI_PERIOD": 14,
    "RSI_OVERSOLD": 30,
    "RSI_OVERBOUGHT": 70,
    "SMA_SHORT": 20,
    "SMA_MEDIUM": 50,
    "SMA_LONG": 200,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BB_PERIOD": 20,
    "BB_STD": 2,
    "ATR_PERIOD": 14,
}

# PDF Settings
PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# Agent Settings
MAX_TURNS = 25  # Increased for multi-agent system (10 agents + orchestrator coordination)
AGENT_TEMPERATURE = 0.3
