# Indian Stock Market API Reference

## Overview

This document covers the best free APIs for fetching Indian stock market data including NSE (National Stock Exchange) and BSE (Bombay Stock Exchange).

---

## Recommended: yfinance

**yfinance** is the most reliable free option for Indian stocks. It uses Yahoo Finance data.

### Installation
```bash
pip install yfinance
```

### Stock Symbol Format
- **NSE stocks:** Add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`)
- **BSE stocks:** Add `.BO` suffix (e.g., `RELIANCE.BO`, `TCS.BO`)

### Common Indian Stock Symbols
```python
# Large Cap
RELIANCE = "RELIANCE.NS"    # Reliance Industries
TCS = "TCS.NS"              # Tata Consultancy Services
HDFCBANK = "HDFCBANK.NS"    # HDFC Bank
INFY = "INFY.NS"            # Infosys
ICICIBANK = "ICICIBANK.NS"  # ICICI Bank
HINDUNILVR = "HINDUNILVR.NS" # Hindustan Unilever
SBIN = "SBIN.NS"            # State Bank of India
BHARTIARTL = "BHARTIARTL.NS" # Bharti Airtel
ITC = "ITC.NS"              # ITC Limited
KOTAKBANK = "KOTAKBANK.NS"  # Kotak Mahindra Bank

# Indices
NIFTY50 = "^NSEI"           # Nifty 50
SENSEX = "^BSESN"           # BSE Sensex
NIFTY_BANK = "^NSEBANK"     # Nifty Bank
NIFTY_IT = "^CNXIT"         # Nifty IT
```

---

## yfinance Usage Examples

### Get Current Stock Price

```python
import yfinance as yf

def get_current_price(symbol: str) -> dict:
    """Get current stock price and basic info."""
    stock = yf.Ticker(symbol)
    info = stock.info

    return {
        "symbol": symbol,
        "name": info.get("longName", "N/A"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "open": info.get("open") or info.get("regularMarketOpen"),
        "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
        "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
        "volume": info.get("volume") or info.get("regularMarketVolume"),
        "market_cap": info.get("marketCap"),
        "currency": info.get("currency", "INR"),
    }

# Usage
price_data = get_current_price("RELIANCE.NS")
print(f"Reliance Price: ₹{price_data['current_price']}")
```

### Get Historical Data

```python
import yfinance as yf
import pandas as pd

def get_historical_data(
    symbol: str,
    period: str = "1y",      # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: str = "1d"      # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
) -> pd.DataFrame:
    """Get historical OHLCV data."""
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval=interval)
    return df

# Usage
hist = get_historical_data("TCS.NS", period="6mo", interval="1d")
print(hist.tail())

# Output columns: Open, High, Low, Close, Volume, Dividends, Stock Splits
```

### Get Historical Data by Date Range

```python
def get_history_by_dates(
    symbol: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Get historical data between specific dates."""
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date)
    return df

# Usage
hist = get_history_by_dates("INFY.NS", "2025-01-01", "2025-12-31")
```

### Get Company Fundamentals

```python
def get_fundamentals(symbol: str) -> dict:
    """Get company fundamental data."""
    stock = yf.Ticker(symbol)
    info = stock.info

    return {
        "symbol": symbol,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),

        # Valuation
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),

        # Profitability
        "profit_margin": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),

        # Growth
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),

        # Dividends
        "dividend_yield": info.get("dividendYield"),
        "dividend_rate": info.get("dividendRate"),
        "payout_ratio": info.get("payoutRatio"),

        # Financial Health
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),

        # Per Share Data
        "eps": info.get("trailingEps"),
        "book_value": info.get("bookValue"),
        "revenue_per_share": info.get("revenuePerShare"),

        # Analyst Data
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
        "target_mean_price": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
        "num_analysts": info.get("numberOfAnalystOpinions"),

        # Company Info
        "website": info.get("website"),
        "employees": info.get("fullTimeEmployees"),
        "description": info.get("longBusinessSummary"),
    }

# Usage
fundamentals = get_fundamentals("HDFCBANK.NS")
print(f"P/E Ratio: {fundamentals['pe_ratio']}")
print(f"Recommendation: {fundamentals['recommendation']}")
```

### Get Financial Statements

```python
def get_financials(symbol: str) -> dict:
    """Get financial statements."""
    stock = yf.Ticker(symbol)

    return {
        "income_statement": stock.income_stmt,
        "quarterly_income": stock.quarterly_income_stmt,
        "balance_sheet": stock.balance_sheet,
        "quarterly_balance": stock.quarterly_balance_sheet,
        "cash_flow": stock.cashflow,
        "quarterly_cashflow": stock.quarterly_cashflow,
    }

# Usage
financials = get_financials("RELIANCE.NS")
print(financials["income_statement"])
```

### Get Actions (Dividends, Splits)

```python
def get_corporate_actions(symbol: str) -> dict:
    """Get dividends and stock splits."""
    stock = yf.Ticker(symbol)

    return {
        "dividends": stock.dividends,
        "splits": stock.splits,
        "actions": stock.actions,  # Combined
    }

# Usage
actions = get_corporate_actions("TCS.NS")
print("Recent Dividends:")
print(actions["dividends"].tail())
```

### Get Major Holders

```python
def get_holders(symbol: str) -> dict:
    """Get major shareholders information."""
    stock = yf.Ticker(symbol)

    return {
        "major_holders": stock.major_holders,
        "institutional_holders": stock.institutional_holders,
        "mutual_fund_holders": stock.mutualfund_holders,
    }
```

---

## News Fetching

### Using yfinance News

```python
def get_stock_news(symbol: str) -> list:
    """Get recent news for a stock."""
    stock = yf.Ticker(symbol)
    news = stock.news

    return [
        {
            "title": item.get("title"),
            "publisher": item.get("publisher"),
            "link": item.get("link"),
            "published": item.get("providerPublishTime"),
            "type": item.get("type"),
        }
        for item in news
    ]

# Usage
news = get_stock_news("RELIANCE.NS")
for article in news[:5]:
    print(f"- {article['title']}")
```

### Using Google News RSS (Free Alternative)

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def get_google_news(query: str, num_results: int = 10) -> list:
    """Fetch news from Google News RSS feed."""
    encoded_query = quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "xml")

    news = []
    for item in soup.find_all("item")[:num_results]:
        news.append({
            "title": item.title.text if item.title else "",
            "link": item.link.text if item.link else "",
            "published": item.pubDate.text if item.pubDate else "",
            "source": item.source.text if item.source else "",
        })

    return news

# Usage
news = get_google_news("Reliance Industries stock")
```

---

## Technical Analysis with TA Library

```bash
pip install ta
```

### Calculate Technical Indicators

```python
import yfinance as yf
import ta
import pandas as pd

def calculate_indicators(symbol: str, period: str = "1y") -> dict:
    """Calculate technical indicators for a stock."""
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)

    # Trend Indicators
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['MACD'] = ta.trend.macd(df['Close'])
    df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
    df['MACD_Hist'] = ta.trend.macd_diff(df['Close'])
    df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])

    # Momentum Indicators
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
    df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
    df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'])
    df['ROC'] = ta.momentum.roc(df['Close'])

    # Volatility Indicators
    df['BB_High'] = ta.volatility.bollinger_hband(df['Close'])
    df['BB_Low'] = ta.volatility.bollinger_lband(df['Close'])
    df['BB_Mid'] = ta.volatility.bollinger_mavg(df['Close'])
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

    # Volume Indicators
    df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    df['VWAP'] = ta.volume.volume_weighted_average_price(
        df['High'], df['Low'], df['Close'], df['Volume']
    )

    # Get latest values
    latest = df.iloc[-1]

    return {
        "symbol": symbol,
        "price": latest['Close'],
        "date": df.index[-1].strftime("%Y-%m-%d"),

        # Trend
        "sma_20": round(latest['SMA_20'], 2) if pd.notna(latest['SMA_20']) else None,
        "sma_50": round(latest['SMA_50'], 2) if pd.notna(latest['SMA_50']) else None,
        "sma_200": round(latest['SMA_200'], 2) if pd.notna(latest['SMA_200']) else None,
        "ema_20": round(latest['EMA_20'], 2) if pd.notna(latest['EMA_20']) else None,
        "macd": round(latest['MACD'], 2) if pd.notna(latest['MACD']) else None,
        "macd_signal": round(latest['MACD_Signal'], 2) if pd.notna(latest['MACD_Signal']) else None,
        "adx": round(latest['ADX'], 2) if pd.notna(latest['ADX']) else None,

        # Momentum
        "rsi": round(latest['RSI'], 2) if pd.notna(latest['RSI']) else None,
        "stoch_k": round(latest['Stoch_K'], 2) if pd.notna(latest['Stoch_K']) else None,
        "stoch_d": round(latest['Stoch_D'], 2) if pd.notna(latest['Stoch_D']) else None,
        "williams_r": round(latest['Williams_R'], 2) if pd.notna(latest['Williams_R']) else None,

        # Volatility
        "bb_high": round(latest['BB_High'], 2) if pd.notna(latest['BB_High']) else None,
        "bb_low": round(latest['BB_Low'], 2) if pd.notna(latest['BB_Low']) else None,
        "atr": round(latest['ATR'], 2) if pd.notna(latest['ATR']) else None,

        # Volume
        "obv": latest['OBV'] if pd.notna(latest['OBV']) else None,

        # Signals
        "price_vs_sma20": "above" if latest['Close'] > latest['SMA_20'] else "below",
        "price_vs_sma50": "above" if latest['Close'] > latest['SMA_50'] else "below",
        "rsi_signal": "oversold" if latest['RSI'] < 30 else ("overbought" if latest['RSI'] > 70 else "neutral"),
        "macd_signal_type": "bullish" if latest['MACD'] > latest['MACD_Signal'] else "bearish",

        # Raw dataframe for further analysis
        "dataframe": df,
    }

# Usage
indicators = calculate_indicators("RELIANCE.NS")
print(f"RSI: {indicators['rsi']} ({indicators['rsi_signal']})")
print(f"MACD: {indicators['macd_signal_type']}")
```

---

## Support and Resistance Levels

```python
def calculate_support_resistance(symbol: str, period: str = "3mo") -> dict:
    """Calculate support and resistance levels."""
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)

    current_price = df['Close'].iloc[-1]

    # Pivot Points (Standard)
    high = df['High'].iloc[-1]
    low = df['Low'].iloc[-1]
    close = df['Close'].iloc[-1]

    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)

    # Recent highs and lows
    recent_high = df['High'].tail(20).max()
    recent_low = df['Low'].tail(20).min()

    # 52-week data
    year_data = stock.history(period="1y")
    week_52_high = year_data['High'].max()
    week_52_low = year_data['Low'].min()

    return {
        "current_price": round(current_price, 2),
        "pivot_point": round(pivot, 2),

        "resistance_1": round(r1, 2),
        "resistance_2": round(r2, 2),
        "resistance_3": round(r3, 2),

        "support_1": round(s1, 2),
        "support_2": round(s2, 2),
        "support_3": round(s3, 2),

        "recent_high_20d": round(recent_high, 2),
        "recent_low_20d": round(recent_low, 2),

        "52_week_high": round(week_52_high, 2),
        "52_week_low": round(week_52_low, 2),

        "distance_from_52w_high": round((week_52_high - current_price) / current_price * 100, 2),
        "distance_from_52w_low": round((current_price - week_52_low) / week_52_low * 100, 2),
    }

# Usage
levels = calculate_support_resistance("TCS.NS")
print(f"Support 1: ₹{levels['support_1']}")
print(f"Resistance 1: ₹{levels['resistance_1']}")
```

---

## Complete Data Fetching Module

```python
# stock_data.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

class IndianStockData:
    """Comprehensive Indian stock data fetcher."""

    def __init__(self, symbol: str):
        """Initialize with stock symbol.

        Args:
            symbol: Stock symbol (add .NS for NSE, .BO for BSE)
        """
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
        self._info = None

    @property
    def info(self) -> dict:
        """Cached stock info."""
        if self._info is None:
            self._info = self.stock.info
        return self._info

    def get_current_data(self) -> dict:
        """Get current price and basic data."""
        info = self.info
        return {
            "symbol": self.symbol,
            "name": info.get("longName", "N/A"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange"),
            "change_percent": info.get("regularMarketChangePercent"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
        }

    def get_history(
        self,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical OHLCV data."""
        return self.stock.history(period=period, interval=interval)

    def get_fundamentals(self) -> dict:
        """Get fundamental analysis data."""
        info = self.info
        return {
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": info.get("returnOnEquity"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "recommendation": info.get("recommendationKey"),
        }

    def get_news(self) -> list:
        """Get recent news."""
        return self.stock.news

    def refresh(self):
        """Refresh cached data."""
        self._info = None
        self.stock = yf.Ticker(self.symbol)

# Usage
stock = IndianStockData("RELIANCE.NS")
print(stock.get_current_data())
print(stock.get_fundamentals())
```

---

## Important Notes

1. **Rate Limits:** yfinance may have rate limits. Add delays between requests if fetching many stocks.

2. **Market Hours:** NSE/BSE trade 9:15 AM - 3:30 PM IST, Monday-Friday. Real-time data only during market hours.

3. **Data Delays:** Free data may be delayed by 15-20 minutes.

4. **Symbol Accuracy:** Always verify symbol format (.NS or .BO suffix).

5. **Error Handling:** Always handle network errors and missing data gracefully.

```python
def safe_get_price(symbol: str) -> Optional[dict]:
    """Safely get stock price with error handling."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        if not info or 'regularMarketPrice' not in info:
            return None
        return {
            "symbol": symbol,
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None
```
