"""
Stock Data Tools - Functions to fetch real-time and historical stock data
for Indian stocks from NSE and BSE using yfinance.
"""

import yfinance as yf
from agents import function_tool
from typing import Optional
from datetime import datetime
import json


def _normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to include exchange suffix."""
    symbol = symbol.upper().strip()
    # Already has suffix
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol
    # Index symbols
    if symbol.startswith("^"):
        return symbol
    # Default to NSE
    return f"{symbol}.NS"


def _safe_get(info: dict, key: str, default=None):
    """Safely get value from dict, handling None and NaN."""
    import math
    value = info.get(key, default)
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    return value


@function_tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price and basic trading information for an Indian stock.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS, INFY). Will auto-add .NS suffix for NSE stocks.

    Returns:
        Current price, change, volume and other real-time data.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info or "regularMarketPrice" not in info and "currentPrice" not in info:
            return json.dumps({
                "error": f"Could not fetch data for {symbol}. Please verify the symbol.",
                "symbol": symbol
            })

        current_price = _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice", 0)
        prev_close = _safe_get(info, "previousClose", 0)
        change = current_price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        result = {
            "symbol": symbol,
            "name": _safe_get(info, "longName", "N/A"),
            "current_price": round(current_price, 2),
            "previous_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "day_open": round(_safe_get(info, "open", 0) or _safe_get(info, "regularMarketOpen", 0), 2),
            "day_high": round(_safe_get(info, "dayHigh", 0) or _safe_get(info, "regularMarketDayHigh", 0), 2),
            "day_low": round(_safe_get(info, "dayLow", 0) or _safe_get(info, "regularMarketDayLow", 0), 2),
            "volume": _safe_get(info, "volume") or _safe_get(info, "regularMarketVolume", 0),
            "avg_volume": _safe_get(info, "averageVolume", 0),
            "bid": _safe_get(info, "bid", 0),
            "ask": _safe_get(info, "ask", 0),
            "52_week_high": round(_safe_get(info, "fiftyTwoWeekHigh", 0), 2),
            "52_week_low": round(_safe_get(info, "fiftyTwoWeekLow", 0), 2),
            "market_cap": _safe_get(info, "marketCap", 0),
            "currency": _safe_get(info, "currency", "INR"),
            "exchange": _safe_get(info, "exchange", "NSE"),
            "timestamp": datetime.now().isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error fetching price for {symbol}: {str(e)}",
            "symbol": symbol
        })


@function_tool
def get_stock_info(symbol: str) -> str:
    """Get comprehensive company information including sector, industry, and business description.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS, INFY). Will auto-add .NS suffix for NSE stocks.

    Returns:
        Detailed company information including business summary.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info:
            return json.dumps({"error": f"Could not fetch info for {symbol}"})

        result = {
            "symbol": symbol,
            "name": _safe_get(info, "longName", "N/A"),
            "short_name": _safe_get(info, "shortName", "N/A"),
            "sector": _safe_get(info, "sector", "N/A"),
            "industry": _safe_get(info, "industry", "N/A"),
            "website": _safe_get(info, "website", "N/A"),
            "employees": _safe_get(info, "fullTimeEmployees", "N/A"),
            "country": _safe_get(info, "country", "India"),
            "city": _safe_get(info, "city", "N/A"),
            "business_summary": _safe_get(info, "longBusinessSummary", "No description available"),
            "market_cap": _safe_get(info, "marketCap", 0),
            "enterprise_value": _safe_get(info, "enterpriseValue", 0),
            "shares_outstanding": _safe_get(info, "sharesOutstanding", 0),
            "float_shares": _safe_get(info, "floatShares", 0),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching info for {symbol}: {str(e)}"})


@function_tool
def get_historical_data(
    symbol: str,
    period: str = "3mo",
    interval: str = "1d"
) -> str:
    """Get historical OHLCV (Open, High, Low, Close, Volume) data for a stock.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.
        period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. Default: 3mo
        interval: Data interval - 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo. Default: 1d

    Returns:
        Historical price data with OHLCV values and summary statistics.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            return json.dumps({"error": f"No historical data for {symbol}"})

        # Calculate summary statistics
        latest = df.iloc[-1]
        first = df.iloc[0]
        period_return = ((latest['Close'] - first['Close']) / first['Close']) * 100

        # Get recent data (last 10 entries)
        recent_data = []
        for idx, row in df.tail(10).iterrows():
            recent_data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume']),
            })

        result = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(df),
            "start_date": df.index[0].strftime("%Y-%m-%d"),
            "end_date": df.index[-1].strftime("%Y-%m-%d"),
            "summary": {
                "start_price": round(first['Close'], 2),
                "end_price": round(latest['Close'], 2),
                "period_return_percent": round(period_return, 2),
                "highest_price": round(df['High'].max(), 2),
                "lowest_price": round(df['Low'].min(), 2),
                "average_price": round(df['Close'].mean(), 2),
                "average_volume": int(df['Volume'].mean()),
                "total_volume": int(df['Volume'].sum()),
                "volatility": round(df['Close'].std(), 2),
            },
            "recent_data": recent_data,
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching history for {symbol}: {str(e)}"})


@function_tool
def get_fundamentals(symbol: str) -> str:
    """Get fundamental analysis data including valuation ratios, profitability metrics, and analyst recommendations.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.

    Returns:
        Comprehensive fundamental data for investment analysis.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info:
            return json.dumps({"error": f"Could not fetch fundamentals for {symbol}"})

        result = {
            "symbol": symbol,
            "name": _safe_get(info, "longName", "N/A"),

            # Current Price Info
            "current_price": _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice"),
            "52_week_high": _safe_get(info, "fiftyTwoWeekHigh"),
            "52_week_low": _safe_get(info, "fiftyTwoWeekLow"),

            # Valuation Ratios
            "valuation": {
                "market_cap": _safe_get(info, "marketCap"),
                "enterprise_value": _safe_get(info, "enterpriseValue"),
                "pe_ratio_trailing": _safe_get(info, "trailingPE"),
                "pe_ratio_forward": _safe_get(info, "forwardPE"),
                "peg_ratio": _safe_get(info, "pegRatio"),
                "price_to_book": _safe_get(info, "priceToBook"),
                "price_to_sales": _safe_get(info, "priceToSalesTrailing12Months"),
                "ev_to_revenue": _safe_get(info, "enterpriseToRevenue"),
                "ev_to_ebitda": _safe_get(info, "enterpriseToEbitda"),
            },

            # Profitability
            "profitability": {
                "profit_margin": _safe_get(info, "profitMargins"),
                "operating_margin": _safe_get(info, "operatingMargins"),
                "gross_margin": _safe_get(info, "grossMargins"),
                "return_on_equity": _safe_get(info, "returnOnEquity"),
                "return_on_assets": _safe_get(info, "returnOnAssets"),
            },

            # Growth
            "growth": {
                "revenue_growth": _safe_get(info, "revenueGrowth"),
                "earnings_growth": _safe_get(info, "earningsGrowth"),
                "earnings_quarterly_growth": _safe_get(info, "earningsQuarterlyGrowth"),
            },

            # Per Share Data
            "per_share": {
                "eps_trailing": _safe_get(info, "trailingEps"),
                "eps_forward": _safe_get(info, "forwardEps"),
                "book_value": _safe_get(info, "bookValue"),
                "revenue_per_share": _safe_get(info, "revenuePerShare"),
            },

            # Dividends
            "dividends": {
                "dividend_rate": _safe_get(info, "dividendRate"),
                "dividend_yield": _safe_get(info, "dividendYield"),
                "payout_ratio": _safe_get(info, "payoutRatio"),
                "ex_dividend_date": _safe_get(info, "exDividendDate"),
            },

            # Financial Health
            "financial_health": {
                "total_cash": _safe_get(info, "totalCash"),
                "total_debt": _safe_get(info, "totalDebt"),
                "debt_to_equity": _safe_get(info, "debtToEquity"),
                "current_ratio": _safe_get(info, "currentRatio"),
                "quick_ratio": _safe_get(info, "quickRatio"),
            },

            # Analyst Recommendations
            "analyst_data": {
                "recommendation": _safe_get(info, "recommendationKey", "N/A"),
                "recommendation_mean": _safe_get(info, "recommendationMean"),
                "num_analysts": _safe_get(info, "numberOfAnalystOpinions"),
                "target_high_price": _safe_get(info, "targetHighPrice"),
                "target_low_price": _safe_get(info, "targetLowPrice"),
                "target_mean_price": _safe_get(info, "targetMeanPrice"),
                "target_median_price": _safe_get(info, "targetMedianPrice"),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching fundamentals for {symbol}: {str(e)}"})
