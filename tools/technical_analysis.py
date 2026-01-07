"""
Technical Analysis Tools - Functions to calculate technical indicators,
support/resistance levels, and trend analysis for Indian stocks.
"""

import yfinance as yf
import ta
import pandas as pd
from agents import function_tool
from typing import Optional
import json
import math


def _normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to include exchange suffix."""
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO") or symbol.startswith("^"):
        return symbol
    return f"{symbol}.NS"


def _safe_round(value, decimals=2):
    """Safely round a value, handling None and NaN."""
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return round(value, decimals)


@function_tool
def get_technical_indicators(symbol: str, period: str = "6mo") -> str:
    """Calculate comprehensive technical indicators for a stock including RSI, MACD, Moving Averages, Bollinger Bands, and more.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.
        period: Historical data period - 1mo, 3mo, 6mo, 1y, 2y. Default: 6mo

    Returns:
        Technical indicators with current values and signals interpretation.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)

        if df.empty or len(df) < 50:
            return json.dumps({
                "error": f"Insufficient data for {symbol}. Need at least 50 data points.",
                "symbol": symbol
            })

        # Calculate all indicators
        # Trend Indicators
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_Hist'] = ta.trend.macd_diff(df['Close'])
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])

        # Momentum Indicators
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'])
        df['ROC'] = ta.momentum.roc(df['Close'], window=10)
        df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])

        # Volatility Indicators
        df['BB_High'] = ta.volatility.bollinger_hband(df['Close'])
        df['BB_Low'] = ta.volatility.bollinger_lband(df['Close'])
        df['BB_Mid'] = ta.volatility.bollinger_mavg(df['Close'])
        df['BB_Width'] = ta.volatility.bollinger_wband(df['Close'])
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

        # Volume Indicators
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        df['VWAP'] = ta.volume.volume_weighted_average_price(
            df['High'], df['Low'], df['Close'], df['Volume']
        )

        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price = latest['Close']

        # Determine signals
        def get_rsi_signal(rsi):
            if rsi is None:
                return "unknown"
            if rsi < 30:
                return "oversold (bullish)"
            elif rsi > 70:
                return "overbought (bearish)"
            elif rsi < 40:
                return "approaching oversold"
            elif rsi > 60:
                return "approaching overbought"
            return "neutral"

        def get_macd_signal(macd, signal):
            if macd is None or signal is None:
                return "unknown"
            if macd > signal:
                return "bullish"
            return "bearish"

        def get_trend_signal(price, sma20, sma50, sma200):
            signals = []
            if sma20 and price > sma20:
                signals.append("above SMA20")
            if sma50 and price > sma50:
                signals.append("above SMA50")
            if sma200 and price > sma200:
                signals.append("above SMA200")

            if len(signals) == 3:
                return "strong uptrend"
            elif len(signals) >= 2:
                return "uptrend"
            elif len(signals) == 1:
                return "mixed"
            return "downtrend"

        def get_bb_signal(price, bb_high, bb_low):
            if bb_high is None or bb_low is None:
                return "unknown"
            if price >= bb_high:
                return "at upper band (overbought)"
            elif price <= bb_low:
                return "at lower band (oversold)"
            return "within bands"

        rsi_val = _safe_round(latest['RSI'])
        macd_val = _safe_round(latest['MACD'])
        macd_sig = _safe_round(latest['MACD_Signal'])
        sma20 = _safe_round(latest['SMA_20'])
        sma50 = _safe_round(latest['SMA_50'])
        sma200 = _safe_round(latest['SMA_200'])

        result = {
            "symbol": symbol,
            "current_price": _safe_round(price),
            "analysis_date": df.index[-1].strftime("%Y-%m-%d"),
            "data_points_analyzed": len(df),

            "trend_indicators": {
                "sma_20": sma20,
                "sma_50": sma50,
                "sma_200": sma200,
                "ema_12": _safe_round(latest['EMA_12']),
                "ema_26": _safe_round(latest['EMA_26']),
                "macd": macd_val,
                "macd_signal": macd_sig,
                "macd_histogram": _safe_round(latest['MACD_Hist']),
                "adx": _safe_round(latest['ADX']),
            },

            "momentum_indicators": {
                "rsi_14": rsi_val,
                "stochastic_k": _safe_round(latest['Stoch_K']),
                "stochastic_d": _safe_round(latest['Stoch_D']),
                "williams_r": _safe_round(latest['Williams_R']),
                "roc_10": _safe_round(latest['ROC']),
                "mfi": _safe_round(latest['MFI']),
            },

            "volatility_indicators": {
                "bollinger_upper": _safe_round(latest['BB_High']),
                "bollinger_middle": _safe_round(latest['BB_Mid']),
                "bollinger_lower": _safe_round(latest['BB_Low']),
                "bollinger_width": _safe_round(latest['BB_Width']),
                "atr_14": _safe_round(latest['ATR']),
            },

            "volume_indicators": {
                "obv": _safe_round(latest['OBV'], 0),
                "vwap": _safe_round(latest['VWAP']),
                "volume": int(latest['Volume']),
                "avg_volume_20": int(df['Volume'].tail(20).mean()),
            },

            "signals": {
                "rsi_signal": get_rsi_signal(rsi_val),
                "macd_signal": get_macd_signal(macd_val, macd_sig),
                "trend_signal": get_trend_signal(price, sma20, sma50, sma200),
                "bollinger_signal": get_bb_signal(price, latest['BB_High'], latest['BB_Low']),
                "volume_signal": "high" if latest['Volume'] > df['Volume'].tail(20).mean() * 1.5 else "normal",
            },

            "price_vs_indicators": {
                "vs_sma20": _safe_round(((price - sma20) / sma20 * 100) if sma20 else None),
                "vs_sma50": _safe_round(((price - sma50) / sma50 * 100) if sma50 else None),
                "vs_sma200": _safe_round(((price - sma200) / sma200 * 100) if sma200 else None),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error calculating indicators for {symbol}: {str(e)}",
            "symbol": symbol
        })


@function_tool
def get_support_resistance(symbol: str, period: str = "3mo") -> str:
    """Calculate support and resistance levels using pivot points and historical price analysis.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.
        period: Historical data period for calculation. Default: 3mo

    Returns:
        Multiple support and resistance levels with pivot points.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)

        if df.empty:
            return json.dumps({"error": f"No data for {symbol}"})

        # Get latest OHLC for pivot calculation
        latest = df.iloc[-1]
        high = latest['High']
        low = latest['Low']
        close = latest['Close']

        # Standard Pivot Points
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)

        # Fibonacci Retracement Levels (from period high/low)
        period_high = df['High'].max()
        period_low = df['Low'].min()
        diff = period_high - period_low

        fib_236 = period_high - (diff * 0.236)
        fib_382 = period_high - (diff * 0.382)
        fib_500 = period_high - (diff * 0.5)
        fib_618 = period_high - (diff * 0.618)
        fib_786 = period_high - (diff * 0.786)

        # Recent significant levels
        recent_high_5d = df['High'].tail(5).max()
        recent_low_5d = df['Low'].tail(5).min()
        recent_high_20d = df['High'].tail(20).max()
        recent_low_20d = df['Low'].tail(20).min()

        # 52-week data
        year_df = stock.history(period="1y")
        week_52_high = year_df['High'].max() if not year_df.empty else None
        week_52_low = year_df['Low'].min() if not year_df.empty else None

        result = {
            "symbol": symbol,
            "current_price": _safe_round(close),
            "analysis_date": df.index[-1].strftime("%Y-%m-%d"),

            "pivot_points": {
                "pivot": _safe_round(pivot),
                "resistance_1": _safe_round(r1),
                "resistance_2": _safe_round(r2),
                "resistance_3": _safe_round(r3),
                "support_1": _safe_round(s1),
                "support_2": _safe_round(s2),
                "support_3": _safe_round(s3),
            },

            "fibonacci_levels": {
                "level_236": _safe_round(fib_236),
                "level_382": _safe_round(fib_382),
                "level_500": _safe_round(fib_500),
                "level_618": _safe_round(fib_618),
                "level_786": _safe_round(fib_786),
                "period_high": _safe_round(period_high),
                "period_low": _safe_round(period_low),
            },

            "recent_levels": {
                "5_day_high": _safe_round(recent_high_5d),
                "5_day_low": _safe_round(recent_low_5d),
                "20_day_high": _safe_round(recent_high_20d),
                "20_day_low": _safe_round(recent_low_20d),
            },

            "52_week": {
                "high": _safe_round(week_52_high),
                "low": _safe_round(week_52_low),
                "from_high_percent": _safe_round(((week_52_high - close) / close * 100) if week_52_high else None),
                "from_low_percent": _safe_round(((close - week_52_low) / week_52_low * 100) if week_52_low else None),
            },

            "key_levels_summary": {
                "immediate_resistance": _safe_round(min([l for l in [r1, recent_high_5d] if l and l > close], default=r1)),
                "immediate_support": _safe_round(max([l for l in [s1, recent_low_5d] if l and l < close], default=s1)),
                "major_resistance": _safe_round(r2),
                "major_support": _safe_round(s2),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating support/resistance for {symbol}: {str(e)}"})


@function_tool
def analyze_trend(symbol: str, period: str = "6mo") -> str:
    """Perform comprehensive trend analysis including trend direction, strength, and momentum.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.
        period: Analysis period - 3mo, 6mo, 1y, 2y. Default: 6mo

    Returns:
        Detailed trend analysis with direction, strength, and recommendations.
    """
    try:
        symbol = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)

        if df.empty or len(df) < 50:
            return json.dumps({"error": f"Insufficient data for {symbol}"})

        # Calculate indicators for trend analysis
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])

        latest = df.iloc[-1]
        price = latest['Close']

        # Calculate returns for different periods
        returns_1w = ((price - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100) if len(df) >= 5 else None
        returns_1m = ((price - df['Close'].iloc[-22]) / df['Close'].iloc[-22] * 100) if len(df) >= 22 else None
        returns_3m = ((price - df['Close'].iloc[-66]) / df['Close'].iloc[-66] * 100) if len(df) >= 66 else None

        # Determine trend direction
        sma20 = latest['SMA_20']
        sma50 = latest['SMA_50']
        sma200 = latest['SMA_200'] if pd.notna(latest['SMA_200']) else None

        trend_scores = 0
        if pd.notna(sma20) and price > sma20:
            trend_scores += 1
        if pd.notna(sma50) and price > sma50:
            trend_scores += 1
        if sma200 and price > sma200:
            trend_scores += 1
        if pd.notna(sma20) and pd.notna(sma50) and sma20 > sma50:
            trend_scores += 1

        if trend_scores >= 3:
            trend_direction = "strong_uptrend"
        elif trend_scores == 2:
            trend_direction = "uptrend"
        elif trend_scores == 1:
            trend_direction = "neutral"
        else:
            trend_direction = "downtrend"

        # Trend strength from ADX
        adx = latest['ADX']
        if pd.notna(adx):
            if adx > 50:
                trend_strength = "very_strong"
            elif adx > 25:
                trend_strength = "strong"
            elif adx > 20:
                trend_strength = "moderate"
            else:
                trend_strength = "weak"
        else:
            trend_strength = "unknown"

        # Momentum analysis
        rsi = latest['RSI']
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']

        momentum_signals = []
        if pd.notna(rsi):
            if rsi < 30:
                momentum_signals.append("RSI oversold - potential reversal up")
            elif rsi > 70:
                momentum_signals.append("RSI overbought - potential reversal down")
            elif rsi > 50:
                momentum_signals.append("RSI bullish")
            else:
                momentum_signals.append("RSI bearish")

        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal:
                momentum_signals.append("MACD bullish crossover")
            else:
                momentum_signals.append("MACD bearish")

        # Generate overall assessment
        bullish_factors = []
        bearish_factors = []

        if trend_direction in ["strong_uptrend", "uptrend"]:
            bullish_factors.append(f"Price in {trend_direction}")
        else:
            bearish_factors.append(f"Price in {trend_direction}")

        if trend_strength in ["strong", "very_strong"]:
            bullish_factors.append(f"Trend strength is {trend_strength}")

        if pd.notna(rsi) and rsi < 40:
            bullish_factors.append("RSI suggests upside potential")
        elif pd.notna(rsi) and rsi > 60:
            bearish_factors.append("RSI suggests caution")

        if returns_1m and returns_1m > 0:
            bullish_factors.append(f"Positive 1-month return ({_safe_round(returns_1m)}%)")
        elif returns_1m and returns_1m < 0:
            bearish_factors.append(f"Negative 1-month return ({_safe_round(returns_1m)}%)")

        result = {
            "symbol": symbol,
            "current_price": _safe_round(price),
            "analysis_date": df.index[-1].strftime("%Y-%m-%d"),

            "trend_analysis": {
                "direction": trend_direction,
                "strength": trend_strength,
                "adx_value": _safe_round(adx),
            },

            "moving_averages": {
                "sma_20": _safe_round(sma20),
                "sma_50": _safe_round(sma50),
                "sma_200": _safe_round(sma200),
                "ema_20": _safe_round(latest['EMA_20']),
                "price_vs_sma20": "above" if pd.notna(sma20) and price > sma20 else "below",
                "price_vs_sma50": "above" if pd.notna(sma50) and price > sma50 else "below",
                "price_vs_sma200": "above" if sma200 and price > sma200 else "below",
                "golden_cross": pd.notna(sma50) and sma200 and sma50 > sma200,
                "death_cross": pd.notna(sma50) and sma200 and sma50 < sma200,
            },

            "momentum": {
                "rsi": _safe_round(rsi),
                "macd": _safe_round(macd),
                "macd_signal": _safe_round(macd_signal),
                "signals": momentum_signals,
            },

            "returns": {
                "1_week": _safe_round(returns_1w),
                "1_month": _safe_round(returns_1m),
                "3_month": _safe_round(returns_3m),
            },

            "assessment": {
                "bullish_factors": bullish_factors,
                "bearish_factors": bearish_factors,
                "overall_bias": "bullish" if len(bullish_factors) > len(bearish_factors) else (
                    "bearish" if len(bearish_factors) > len(bullish_factors) else "neutral"
                ),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing trend for {symbol}: {str(e)}"})
