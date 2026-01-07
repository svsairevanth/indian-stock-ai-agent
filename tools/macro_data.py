"""
Macroeconomic Data Tools - Functions to fetch India macro indicators,
RBI policy rates, inflation data, and market benchmark comparisons.
"""

import yfinance as yf
from agents import function_tool
from typing import Optional
from datetime import datetime, timedelta
import json
import requests
from bs4 import BeautifulSoup


def _safe_get(data: dict, key: str, default=None):
    """Safely get value from dict."""
    import math
    value = data.get(key, default)
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    return value


@function_tool
def get_india_macro_indicators() -> str:
    """Get key macroeconomic indicators for India including RBI repo rate, inflation, GDP growth estimates.

    Returns:
        Current macroeconomic indicators for India including policy rates and inflation data.
    """
    try:
        # IMPORTANT: This is SIMULATED reference data for demonstration purposes
        # In production, integrate with official APIs:
        # - RBI API for monetary policy
        # - MOSPI for inflation/GDP data
        # - NSE/BSE APIs for market data
        DATA_VERSION = "2024-12-06"  # Last manual update

        macro_data = {
            "timestamp": datetime.now().isoformat(),
            "data_version": DATA_VERSION,
            "source": "RBI / Ministry of Finance / Trading Economics",

            # DISCLAIMER - This is critical for users
            "disclaimer": {
                "warning": "SIMULATED DATA - For demonstration only",
                "message": "This macro data is reference/simulated data and may not reflect current market conditions.",
                "recommendation": "Verify all indicators with official sources (RBI, MOSPI, NSE) before making investment decisions.",
                "last_updated": DATA_VERSION,
            },

            "monetary_policy": {
                "repo_rate": 6.50,  # RBI repo rate
                "reverse_repo_rate": 3.35,
                "bank_rate": 6.75,
                "crr": 4.50,  # Cash Reserve Ratio
                "slr": 18.00,  # Statutory Liquidity Ratio
                "policy_stance": "withdrawal of accommodation",
                "last_mpc_date": "2024-12-06",
                "next_mpc_date": "2025-02-05",
            },

            "inflation": {
                "cpi_yoy": 5.48,  # Consumer Price Index YoY
                "wpi_yoy": 1.89,  # Wholesale Price Index YoY
                "core_inflation": 4.10,
                "food_inflation": 9.04,
                "fuel_inflation": -1.10,
                "rbi_target_range": "4% +/- 2%",
                "inflation_outlook": "elevated due to food prices",
            },

            "growth": {
                "gdp_growth_fy24": 8.2,
                "gdp_growth_fy25_estimate": 6.5,
                "iip_growth": 3.1,  # Industrial Production Index
                "pmi_manufacturing": 56.5,
                "pmi_services": 58.4,
                "gst_collection_cr": 182000,  # Monthly GST in crores
            },

            "external_sector": {
                "forex_reserves_bn_usd": 658.0,
                "usd_inr_rate": 84.50,
                "fii_net_investment_cr": -15000,  # Monthly
                "dii_net_investment_cr": 22000,  # Monthly
                "trade_deficit_bn_usd": -23.5,  # Monthly
            },

            "market_sentiment": {
                "india_vix": 14.5,
                "put_call_ratio": 0.85,
                "advance_decline_ratio": 1.2,
            },

            "interpretation": {
                "interest_rate_outlook": "Rates likely to remain stable in near term",
                "inflation_risk": "Elevated food inflation remains a concern",
                "growth_outlook": "Strong domestic demand supporting growth",
                "currency_outlook": "INR under pressure due to FII outflows",
                "overall_macro_score": 6.5,  # 1-10 scale
                "investment_climate": "Cautiously positive for equities",
            }
        }

        return json.dumps(macro_data, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching macro data: {str(e)}"})


@function_tool
def get_nifty_benchmark_data(period: str = "1y") -> str:
    """Get Nifty 50 benchmark data for comparison with individual stocks.

    Args:
        period: Time period - 1mo, 3mo, 6mo, 1y, 2y, 5y. Default: 1y

    Returns:
        Nifty 50 performance data including returns and volatility.
    """
    try:
        nifty = yf.Ticker("^NSEI")
        df = nifty.history(period=period)

        if df.empty:
            return json.dumps({"error": "Could not fetch Nifty data"})

        latest = df.iloc[-1]
        first = df.iloc[0]

        # Calculate returns for different periods
        returns = {}
        if len(df) >= 5:
            returns["1_week"] = round(((latest['Close'] - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100), 2)
        if len(df) >= 22:
            returns["1_month"] = round(((latest['Close'] - df['Close'].iloc[-22]) / df['Close'].iloc[-22] * 100), 2)
        if len(df) >= 66:
            returns["3_month"] = round(((latest['Close'] - df['Close'].iloc[-66]) / df['Close'].iloc[-66] * 100), 2)
        if len(df) >= 130:
            returns["6_month"] = round(((latest['Close'] - df['Close'].iloc[-130]) / df['Close'].iloc[-130] * 100), 2)

        period_return = ((latest['Close'] - first['Close']) / first['Close'] * 100)

        # Calculate volatility (annualized standard deviation)
        daily_returns = df['Close'].pct_change().dropna()
        volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized

        # Year high/low
        year_df = nifty.history(period="1y")
        year_high = year_df['High'].max() if not year_df.empty else None
        year_low = year_df['Low'].min() if not year_df.empty else None

        result = {
            "index": "NIFTY 50",
            "symbol": "^NSEI",
            "current_value": round(latest['Close'], 2),
            "previous_close": round(df['Close'].iloc[-2], 2) if len(df) > 1 else None,
            "day_change_pct": round(((latest['Close'] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100), 2) if len(df) > 1 else None,
            "timestamp": df.index[-1].strftime("%Y-%m-%d"),

            "performance": {
                "period_analyzed": period,
                "period_return_pct": round(period_return, 2),
                "returns": returns,
            },

            "risk_metrics": {
                "annualized_volatility_pct": round(volatility, 2),
                "period_high": round(df['High'].max(), 2),
                "period_low": round(df['Low'].min(), 2),
                "52_week_high": round(year_high, 2) if year_high else None,
                "52_week_low": round(year_low, 2) if year_low else None,
            },

            "market_breadth": {
                "note": "Use get_sector_performance for detailed breadth analysis"
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching Nifty data: {str(e)}"})


@function_tool
def get_sector_performance() -> str:
    """Get performance of major Indian market sectors/indices.

    Returns:
        Performance comparison of Nifty sectoral indices.
    """
    try:
        sectors = {
            "NIFTY_50": "^NSEI",
            "NIFTY_BANK": "^NSEBANK",
            "NIFTY_IT": "^CNXIT",
            "NIFTY_PHARMA": "^CNXPHARMA",
            "NIFTY_AUTO": "^CNXAUTO",
            "NIFTY_FMCG": "^CNXFMCG",
            "NIFTY_METAL": "^CNXMETAL",
            "NIFTY_REALTY": "^CNXREALTY",
            "NIFTY_ENERGY": "^CNXENERGY",
            "NIFTY_INFRA": "^CNXINFRA",
            "NIFTY_PSU_BANK": "^CNXPSUBANK",
            "NIFTY_PRIVATE_BANK": "^NIFTYPVTBANK",
        }

        sector_data = []

        for name, symbol in sectors.items():
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="1mo")

                if not df.empty:
                    current = df['Close'].iloc[-1]

                    # 1-week return
                    week_return = None
                    if len(df) >= 5:
                        week_return = round(((current - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100), 2)

                    # 1-month return
                    month_return = round(((current - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100), 2)

                    sector_data.append({
                        "sector": name,
                        "symbol": symbol,
                        "current_value": round(current, 2),
                        "1_week_return": week_return,
                        "1_month_return": month_return,
                    })
            except:
                continue

        # Sort by 1-month return
        sector_data.sort(key=lambda x: x.get("1_month_return", 0) or 0, reverse=True)

        # Identify leaders and laggards
        leaders = sector_data[:3] if len(sector_data) >= 3 else sector_data
        laggards = sector_data[-3:] if len(sector_data) >= 3 else []

        result = {
            "timestamp": datetime.now().isoformat(),
            "sectors": sector_data,
            "analysis": {
                "top_performers": [s["sector"] for s in leaders],
                "bottom_performers": [s["sector"] for s in laggards],
                "market_rotation": _analyze_rotation(sector_data),
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching sector data: {str(e)}"})


def _analyze_rotation(sector_data: list) -> str:
    """Analyze sector rotation pattern."""
    if not sector_data:
        return "Insufficient data"

    # Check if defensive sectors are leading
    defensive = ["NIFTY_FMCG", "NIFTY_PHARMA", "NIFTY_IT"]
    cyclical = ["NIFTY_AUTO", "NIFTY_METAL", "NIFTY_REALTY", "NIFTY_INFRA"]

    top_3 = [s["sector"] for s in sector_data[:3]]

    defensive_leading = sum(1 for s in top_3 if s in defensive)
    cyclical_leading = sum(1 for s in top_3 if s in cyclical)

    if defensive_leading >= 2:
        return "Defensive rotation - Risk-off sentiment"
    elif cyclical_leading >= 2:
        return "Cyclical rotation - Risk-on sentiment"
    elif "NIFTY_BANK" in top_3 or "NIFTY_PRIVATE_BANK" in top_3:
        return "Financials leading - Credit cycle strength"
    else:
        return "Mixed rotation - No clear theme"


@function_tool
def compare_stock_vs_benchmark(symbol: str, period: str = "1y") -> str:
    """Compare a stock's performance against Nifty 50 benchmark.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        period: Comparison period - 1mo, 3mo, 6mo, 1y. Default: 1y

    Returns:
        Comparative analysis of stock vs Nifty 50 including alpha and beta.
    """
    try:
        # Normalize symbol
        symbol_normalized = symbol.upper().strip()
        if not symbol_normalized.endswith(".NS") and not symbol_normalized.endswith(".BO"):
            symbol_normalized = f"{symbol_normalized}.NS"

        # Fetch stock data
        stock = yf.Ticker(symbol_normalized)
        stock_df = stock.history(period=period)

        # Fetch Nifty data
        nifty = yf.Ticker("^NSEI")
        nifty_df = nifty.history(period=period)

        if stock_df.empty or nifty_df.empty:
            return json.dumps({"error": "Could not fetch data for comparison"})

        # Align dates
        common_dates = stock_df.index.intersection(nifty_df.index)
        stock_aligned = stock_df.loc[common_dates]['Close']
        nifty_aligned = nifty_df.loc[common_dates]['Close']

        # Calculate returns
        stock_daily_returns = stock_aligned.pct_change().dropna()
        nifty_daily_returns = nifty_aligned.pct_change().dropna()

        # Period returns
        stock_period_return = ((stock_aligned.iloc[-1] - stock_aligned.iloc[0]) / stock_aligned.iloc[0] * 100)
        nifty_period_return = ((nifty_aligned.iloc[-1] - nifty_aligned.iloc[0]) / nifty_aligned.iloc[0] * 100)

        # Alpha (outperformance)
        alpha = stock_period_return - nifty_period_return

        # Beta calculation
        if len(stock_daily_returns) > 20:
            covariance = stock_daily_returns.cov(nifty_daily_returns)
            nifty_variance = nifty_daily_returns.var()
            beta = covariance / nifty_variance if nifty_variance != 0 else 1.0
        else:
            beta = None

        # Volatility comparison
        stock_volatility = stock_daily_returns.std() * (252 ** 0.5) * 100
        nifty_volatility = nifty_daily_returns.std() * (252 ** 0.5) * 100

        # Correlation
        correlation = stock_daily_returns.corr(nifty_daily_returns) if len(stock_daily_returns) > 5 else None

        # Sharpe-like ratio (simplified, using 6% risk-free rate)
        risk_free = 6.5  # Approximate risk-free rate
        stock_excess = (stock_period_return * (252 / len(stock_aligned))) - risk_free
        stock_sharpe = stock_excess / stock_volatility if stock_volatility > 0 else 0

        result = {
            "stock": symbol_normalized,
            "benchmark": "NIFTY 50",
            "period": period,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),

            "returns_comparison": {
                "stock_return_pct": round(stock_period_return, 2),
                "nifty_return_pct": round(nifty_period_return, 2),
                "alpha_pct": round(alpha, 2),
                "outperformed": alpha > 0,
            },

            "risk_metrics": {
                "beta": round(beta, 2) if beta else None,
                "stock_volatility_pct": round(stock_volatility, 2),
                "nifty_volatility_pct": round(nifty_volatility, 2),
                "relative_volatility": round(stock_volatility / nifty_volatility, 2) if nifty_volatility > 0 else None,
                "correlation": round(correlation, 2) if correlation else None,
            },

            "risk_adjusted": {
                "sharpe_estimate": round(stock_sharpe, 2),
                "interpretation": _interpret_beta(beta) if beta else "Insufficient data",
            },

            "current_prices": {
                "stock_price": round(stock_aligned.iloc[-1], 2),
                "nifty_value": round(nifty_aligned.iloc[-1], 2),
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error comparing {symbol} vs benchmark: {str(e)}"})


def _interpret_beta(beta: float) -> str:
    """Interpret beta value."""
    if beta is None:
        return "Unknown"
    if beta > 1.5:
        return "High beta - Very volatile, amplifies market moves"
    elif beta > 1.1:
        return "Above-market beta - More volatile than market"
    elif beta > 0.9:
        return "Market-neutral beta - Moves with the market"
    elif beta > 0.5:
        return "Low beta - Less volatile, defensive"
    else:
        return "Very low beta - Minimal market correlation"


@function_tool
def get_fii_dii_activity(period_days: int = 30) -> str:
    """Get Foreign Institutional Investor (FII) and Domestic Institutional Investor (DII) activity data.

    Args:
        period_days: Number of days to analyze. Default: 30

    Returns:
        FII/DII buying and selling activity summary.
    """
    try:
        # IMPORTANT: This is SIMULATED reference data for demonstration purposes
        # In production, scrape NSE/SEBI FII/DII daily data:
        # - NSE: https://www.nseindia.com/reports/fii-dii
        # - SEBI: https://www.sebi.gov.in/statistics.html
        DATA_VERSION = "2024-12-06"  # Last manual update

        result = {
            "timestamp": datetime.now().isoformat(),
            "data_version": DATA_VERSION,
            "period_days": period_days,
            "source": "NSE / SEBI",

            # DISCLAIMER - Critical for users
            "disclaimer": {
                "warning": "SIMULATED DATA - For demonstration only",
                "message": "FII/DII data shown is reference/sample data and may not reflect actual institutional activity.",
                "recommendation": "Check NSE FII/DII daily reports for accurate institutional flow data.",
                "last_updated": DATA_VERSION,
            },

            "fii_activity": {
                "net_value_cr": -15234,  # Negative = selling
                "buy_value_cr": 125000,
                "sell_value_cr": 140234,
                "trend": "net_seller",
                "trend_strength": "moderate",
                "month_trend": "continued selling pressure",
            },

            "dii_activity": {
                "net_value_cr": 22500,  # Positive = buying
                "buy_value_cr": 145000,
                "sell_value_cr": 122500,
                "trend": "net_buyer",
                "trend_strength": "strong",
                "month_trend": "absorbing FII selling",
            },

            "analysis": {
                "market_support": "DIIs providing strong support",
                "fii_reason": "Global risk-off, US bond yields attractive",
                "dii_reason": "SIP flows strong, domestic optimism",
                "net_institutional": 7266,  # DII + FII
                "market_impact": "Neutral to mildly negative short-term",
            },

            "historical_context": {
                "fii_ytd_cr": -45000,
                "dii_ytd_cr": 180000,
                "net_ytd_cr": 135000,
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching FII/DII data: {str(e)}"})


@function_tool
def get_global_market_context() -> str:
    """Get global market indicators that affect Indian markets.

    Returns:
        Global market data including US markets, crude oil, dollar index.
    """
    try:
        # Fetch global indices
        global_symbols = {
            "S&P_500": "^GSPC",
            "NASDAQ": "^IXIC",
            "DOW_JONES": "^DJI",
            "US_10Y_YIELD": "^TNX",
            "DOLLAR_INDEX": "DX-Y.NYB",
            "CRUDE_OIL_WTI": "CL=F",
            "GOLD": "GC=F",
            "VIX": "^VIX",
        }

        global_data = {}

        for name, symbol in global_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="5d")
                if not df.empty:
                    current = df['Close'].iloc[-1]
                    prev = df['Close'].iloc[-2] if len(df) > 1 else current
                    change_pct = ((current - prev) / prev * 100) if prev else 0

                    global_data[name] = {
                        "value": round(current, 2),
                        "change_pct": round(change_pct, 2),
                    }
            except:
                continue

        # Analysis
        us_positive = global_data.get("S&P_500", {}).get("change_pct", 0) > 0
        vix_level = global_data.get("VIX", {}).get("value", 15)
        oil_price = global_data.get("CRUDE_OIL_WTI", {}).get("value", 75)

        sentiment = "positive" if us_positive and vix_level < 20 else (
            "negative" if not us_positive or vix_level > 25 else "neutral"
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "global_markets": global_data,

            "india_impact_analysis": {
                "us_market_sentiment": "positive" if us_positive else "negative",
                "vix_interpretation": "low fear" if vix_level < 15 else (
                    "moderate fear" if vix_level < 25 else "high fear"
                ),
                "oil_impact": "negative for India" if oil_price > 85 else (
                    "positive for India" if oil_price < 70 else "neutral"
                ),
                "global_sentiment_score": 7 if sentiment == "positive" else (
                    3 if sentiment == "negative" else 5
                ),
            },

            "key_risks": [
                "US Federal Reserve policy direction",
                "China economic slowdown concerns",
                "Geopolitical tensions",
                "Crude oil price volatility",
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching global market data: {str(e)}"})
