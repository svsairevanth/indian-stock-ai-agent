"""
Configuration settings for the Indian Stock Analyst Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

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
MAX_TURNS = 15
AGENT_TEMPERATURE = 0.3
