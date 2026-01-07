"""
Risk Management Tools - Functions for position sizing, stop loss calculation,
and risk-adjusted trade recommendations.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from agents import function_tool
from typing import Optional, Dict
from datetime import datetime
import json
import ta


def _normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to include exchange suffix."""
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO") or symbol.startswith("^"):
        return symbol
    return f"{symbol}.NS"


def _safe_round(value, decimals=2):
    """Safely round a value, handling None and NaN."""
    import math
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return round(value, decimals)


@function_tool
def calculate_position_size(
    symbol: str,
    portfolio_value: float,
    risk_tolerance_percent: float = 2.0,
    stop_loss_percent: float = None
) -> str:
    """Calculate recommended position size based on risk tolerance.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        portfolio_value: Total portfolio value in INR
        risk_tolerance_percent: Max % of portfolio to risk per trade. Default: 2%
        stop_loss_percent: Optional custom stop loss %. If not provided, uses ATR-based.

    Returns:
        Position sizing recommendation with different risk scenarios.
    """
    try:
        symbol_normalized = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol_normalized)

        # Get current price
        info = stock.info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        if not current_price:
            return json.dumps({"error": f"Could not fetch price for {symbol}"})

        # Get historical data for volatility calculation
        df = stock.history(period="3mo")

        if df.empty:
            return json.dumps({"error": f"Could not fetch historical data for {symbol}"})

        # Calculate ATR for stop loss if not provided
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        current_atr = df['ATR'].iloc[-1]
        atr_percent = (current_atr / current_price) * 100

        # Calculate volatility
        daily_returns = df['Close'].pct_change().dropna()
        daily_volatility = daily_returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252) * 100

        # Determine stop loss
        if stop_loss_percent:
            stop_loss_pct = stop_loss_percent
        else:
            # Use 2x ATR as default stop loss
            stop_loss_pct = atr_percent * 2

        stop_loss_price = current_price * (1 - stop_loss_pct / 100)

        # Calculate position sizes for different scenarios
        max_risk_amount = portfolio_value * (risk_tolerance_percent / 100)
        risk_per_share = current_price - stop_loss_price

        # Conservative position
        conservative_shares = int(max_risk_amount / risk_per_share)
        conservative_value = conservative_shares * current_price
        conservative_weight = (conservative_value / portfolio_value) * 100

        # Moderate position (1.5x conservative)
        moderate_shares = int(conservative_shares * 1.5)
        moderate_value = moderate_shares * current_price
        moderate_weight = (moderate_value / portfolio_value) * 100

        # Aggressive position (2x conservative)
        aggressive_shares = int(conservative_shares * 2)
        aggressive_value = aggressive_shares * current_price
        aggressive_weight = (aggressive_value / portfolio_value) * 100

        # Kelly Criterion (simplified)
        # Assuming 55% win rate and 1.5:1 risk-reward
        win_prob = 0.55
        loss_prob = 0.45
        win_ratio = 1.5
        kelly_fraction = (win_prob * win_ratio - loss_prob) / win_ratio
        kelly_position = portfolio_value * kelly_fraction
        kelly_shares = int(kelly_position / current_price)

        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol_normalized,
            "current_price": round(current_price, 2),

            "risk_parameters": {
                "portfolio_value": portfolio_value,
                "risk_tolerance_percent": risk_tolerance_percent,
                "max_risk_amount": round(max_risk_amount, 2),
            },

            "volatility_analysis": {
                "daily_volatility_percent": round(daily_volatility * 100, 2),
                "annualized_volatility_percent": round(annualized_volatility, 2),
                "atr_14": round(current_atr, 2),
                "atr_percent": round(atr_percent, 2),
                "volatility_classification": "high" if annualized_volatility > 35 else (
                    "moderate" if annualized_volatility > 20 else "low"
                ),
            },

            "stop_loss": {
                "stop_loss_percent": round(stop_loss_pct, 2),
                "stop_loss_price": round(stop_loss_price, 2),
                "risk_per_share": round(risk_per_share, 2),
            },

            "position_recommendations": {
                "conservative": {
                    "shares": conservative_shares,
                    "investment_value": round(conservative_value, 2),
                    "portfolio_weight_percent": round(conservative_weight, 2),
                    "max_loss_if_stopped": round(max_risk_amount, 2),
                    "risk_profile": "low risk",
                },
                "moderate": {
                    "shares": moderate_shares,
                    "investment_value": round(moderate_value, 2),
                    "portfolio_weight_percent": round(moderate_weight, 2),
                    "max_loss_if_stopped": round(max_risk_amount * 1.5, 2),
                    "risk_profile": "balanced",
                },
                "aggressive": {
                    "shares": aggressive_shares,
                    "investment_value": round(aggressive_value, 2),
                    "portfolio_weight_percent": round(aggressive_weight, 2),
                    "max_loss_if_stopped": round(max_risk_amount * 2, 2),
                    "risk_profile": "high risk",
                },
                "kelly_optimal": {
                    "shares": kelly_shares,
                    "investment_value": round(kelly_shares * current_price, 2),
                    "portfolio_weight_percent": round((kelly_shares * current_price / portfolio_value) * 100, 2),
                    "note": "Theoretical optimal based on edge estimation",
                },
            },

            "recommendation": _get_position_recommendation(
                annualized_volatility, conservative_weight
            ),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating position size: {str(e)}"})


def _get_position_recommendation(volatility: float, conservative_weight: float) -> str:
    """Get position size recommendation based on volatility."""
    if volatility > 40:
        return f"High volatility stock. Use conservative sizing ({conservative_weight:.1f}% max). Consider half positions."
    elif volatility > 25:
        return f"Moderate volatility. Conservative to moderate sizing recommended. Max {conservative_weight * 1.5:.1f}%."
    else:
        return f"Low volatility. Can use larger position sizes up to {conservative_weight * 2:.1f}%."


@function_tool
def calculate_stop_loss_levels(symbol: str, entry_price: float = None) -> str:
    """Calculate multiple stop loss levels using different methodologies.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        entry_price: Optional entry price. If not provided, uses current price.

    Returns:
        Multiple stop loss recommendations with different approaches.
    """
    try:
        symbol_normalized = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol_normalized)

        # Get data
        df = stock.history(period="6mo")
        info = stock.info

        if df.empty:
            return json.dumps({"error": f"Could not fetch data for {symbol}"})

        current_price = df['Close'].iloc[-1]
        if entry_price is None:
            entry_price = current_price

        # Calculate indicators
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['BB_Lower'] = ta.volatility.bollinger_lband(df['Close'])

        latest = df.iloc[-1]
        atr = latest['ATR']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        bb_lower = latest['BB_Lower']

        # Recent lows
        low_5d = df['Low'].tail(5).min()
        low_20d = df['Low'].tail(20).min()

        # Support levels (simplified)
        recent_lows = df['Low'].tail(30).nsmallest(3).mean()

        # Calculate different stop loss levels
        stop_losses = {
            "atr_based": {
                "method": "2x ATR below entry",
                "stop_price": round(entry_price - (2 * atr), 2),
                "distance_percent": round((2 * atr / entry_price) * 100, 2),
                "use_case": "Standard volatility-adjusted stop",
            },
            "atr_tight": {
                "method": "1.5x ATR below entry",
                "stop_price": round(entry_price - (1.5 * atr), 2),
                "distance_percent": round((1.5 * atr / entry_price) * 100, 2),
                "use_case": "Tight stop for momentum trades",
            },
            "atr_wide": {
                "method": "3x ATR below entry",
                "stop_price": round(entry_price - (3 * atr), 2),
                "distance_percent": round((3 * atr / entry_price) * 100, 2),
                "use_case": "Wide stop for volatile stocks",
            },
            "percentage_based": {
                "method": "Fixed 7% below entry",
                "stop_price": round(entry_price * 0.93, 2),
                "distance_percent": 7.0,
                "use_case": "Simple percentage-based",
            },
            "sma_20": {
                "method": "Below 20-day SMA",
                "stop_price": round(sma_20 * 0.98, 2) if sma_20 else None,
                "distance_percent": round(((entry_price - sma_20 * 0.98) / entry_price) * 100, 2) if sma_20 else None,
                "use_case": "Trend-following stop",
            },
            "sma_50": {
                "method": "Below 50-day SMA",
                "stop_price": round(sma_50 * 0.98, 2) if sma_50 else None,
                "distance_percent": round(((entry_price - sma_50 * 0.98) / entry_price) * 100, 2) if sma_50 else None,
                "use_case": "Medium-term position stop",
            },
            "swing_low": {
                "method": "Below recent 5-day low",
                "stop_price": round(low_5d * 0.99, 2),
                "distance_percent": round(((entry_price - low_5d * 0.99) / entry_price) * 100, 2),
                "use_case": "Swing trading stop",
            },
            "support_based": {
                "method": "Below recent support",
                "stop_price": round(recent_lows * 0.98, 2),
                "distance_percent": round(((entry_price - recent_lows * 0.98) / entry_price) * 100, 2),
                "use_case": "Support-based stop",
            },
            "bollinger_band": {
                "method": "Below lower Bollinger Band",
                "stop_price": round(bb_lower * 0.99, 2) if bb_lower else None,
                "distance_percent": round(((entry_price - bb_lower * 0.99) / entry_price) * 100, 2) if bb_lower else None,
                "use_case": "Volatility-envelope stop",
            },
        }

        # Recommend best stop loss based on context
        atr_pct = (atr / current_price) * 100

        if atr_pct > 4:
            recommended = "atr_wide"
            reason = "High volatility requires wider stops"
        elif atr_pct < 2:
            recommended = "atr_tight"
            reason = "Low volatility allows tighter stops"
        else:
            recommended = "atr_based"
            reason = "Standard volatility-adjusted stop"

        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol_normalized,
            "entry_price": round(entry_price, 2),
            "current_price": round(current_price, 2),

            "volatility_context": {
                "atr_14": round(atr, 2),
                "atr_percent": round(atr_pct, 2),
                "volatility_level": "high" if atr_pct > 4 else ("low" if atr_pct < 2 else "normal"),
            },

            "stop_loss_levels": stop_losses,

            "recommendation": {
                "suggested_method": recommended,
                "suggested_stop": stop_losses[recommended]["stop_price"],
                "reason": reason,
            },

            "trailing_stop_guidance": {
                "initial_trailing": f"Trail stop by {round(atr, 2)} (1 ATR) after 5% gain",
                "aggressive_trailing": f"Move to breakeven after 3% gain",
                "conservative_trailing": f"Move stop up by 1 ATR for every 2 ATR of gain",
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating stop loss: {str(e)}"})


@function_tool
def assess_trade_risk_reward(
    symbol: str,
    entry_price: float = None,
    target_price: float = None,
    stop_loss_price: float = None
) -> str:
    """Assess risk-reward ratio for a potential trade.

    Args:
        symbol: Stock symbol
        entry_price: Entry price (uses current if not provided)
        target_price: Target price (uses technical resistance if not provided)
        stop_loss_price: Stop loss price (uses ATR-based if not provided)

    Returns:
        Risk-reward analysis with trade quality assessment.
    """
    try:
        symbol_normalized = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol_normalized)

        df = stock.history(period="6mo")
        info = stock.info

        if df.empty:
            return json.dumps({"error": f"Could not fetch data for {symbol}"})

        current_price = df['Close'].iloc[-1]

        # Default entry to current price
        if entry_price is None:
            entry_price = current_price

        # Calculate ATR
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        atr = df['ATR'].iloc[-1]

        # Default stop loss to 2x ATR below entry
        if stop_loss_price is None:
            stop_loss_price = entry_price - (2 * atr)

        # Default target to resistance or 3:1 risk-reward
        if target_price is None:
            # Find nearest resistance
            recent_high = df['High'].tail(20).max()
            period_high = df['High'].max()

            # Use 3:1 risk-reward minimum
            risk = entry_price - stop_loss_price
            minimum_target = entry_price + (3 * risk)

            # Use higher of resistance or minimum target
            target_price = max(recent_high, minimum_target)

        # Calculate metrics
        risk = entry_price - stop_loss_price
        reward = target_price - entry_price
        risk_reward_ratio = reward / risk if risk > 0 else 0

        risk_percent = (risk / entry_price) * 100
        reward_percent = (reward / entry_price) * 100

        # Win probability estimate based on technical setup
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])

        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]

        # Simplified win probability
        win_prob = 0.50  # Base
        if rsi < 40:
            win_prob += 0.10  # Oversold
        elif rsi > 60:
            win_prob -= 0.05  # Overbought
        if macd > macd_signal:
            win_prob += 0.08  # Bullish MACD
        else:
            win_prob -= 0.05

        # Expected value
        expected_value = (win_prob * reward) - ((1 - win_prob) * risk)
        expected_value_percent = (expected_value / entry_price) * 100

        # Trade quality assessment
        if risk_reward_ratio >= 3 and win_prob >= 0.5:
            trade_quality = "excellent"
        elif risk_reward_ratio >= 2 and win_prob >= 0.45:
            trade_quality = "good"
        elif risk_reward_ratio >= 1.5 and win_prob >= 0.45:
            trade_quality = "fair"
        else:
            trade_quality = "poor"

        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol_normalized,

            "trade_parameters": {
                "entry_price": round(entry_price, 2),
                "target_price": round(target_price, 2),
                "stop_loss_price": round(stop_loss_price, 2),
                "current_price": round(current_price, 2),
            },

            "risk_reward_analysis": {
                "risk_amount": round(risk, 2),
                "reward_amount": round(reward, 2),
                "risk_percent": round(risk_percent, 2),
                "reward_percent": round(reward_percent, 2),
                "risk_reward_ratio": round(risk_reward_ratio, 2),
            },

            "probability_assessment": {
                "estimated_win_probability": round(win_prob, 2),
                "technical_setup": {
                    "rsi": round(rsi, 2),
                    "macd_bullish": macd > macd_signal,
                },
            },

            "expected_value": {
                "expected_value_inr": round(expected_value, 2),
                "expected_value_percent": round(expected_value_percent, 2),
                "interpretation": "positive edge" if expected_value > 0 else "negative edge",
            },

            "trade_quality": {
                "rating": trade_quality,
                "recommendation": _get_trade_recommendation(trade_quality, risk_reward_ratio),
            },

            "position_size_suggestion": {
                "for_1_lakh_portfolio": {
                    "shares": int(100000 * 0.02 / risk),  # 2% risk
                    "investment": round(int(100000 * 0.02 / risk) * entry_price, 2),
                },
                "for_5_lakh_portfolio": {
                    "shares": int(500000 * 0.02 / risk),
                    "investment": round(int(500000 * 0.02 / risk) * entry_price, 2),
                },
                "for_10_lakh_portfolio": {
                    "shares": int(1000000 * 0.02 / risk),
                    "investment": round(int(1000000 * 0.02 / risk) * entry_price, 2),
                },
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error assessing trade: {str(e)}"})


def _get_trade_recommendation(quality: str, rr_ratio: float) -> str:
    """Get trade recommendation based on quality."""
    if quality == "excellent":
        return "Strong trade setup. Consider full position size."
    elif quality == "good":
        return "Good setup. Standard position size recommended."
    elif quality == "fair":
        return "Acceptable but not ideal. Consider smaller position."
    else:
        return f"Poor risk-reward ({rr_ratio:.1f}:1). Wait for better setup or adjust levels."


@function_tool
def calculate_max_allocation(
    symbol: str,
    portfolio_value: float,
    max_single_stock_percent: float = 20.0,
    max_sector_percent: float = 30.0,
    current_sector_allocation: str = None
) -> str:
    """Calculate maximum allowed allocation for a stock based on risk rules.

    Args:
        symbol: Stock symbol
        portfolio_value: Total portfolio value
        max_single_stock_percent: Maximum % for any single stock. Default: 20%
        max_sector_percent: Maximum % for any sector. Default: 30%
        current_sector_allocation: JSON of current sector allocations (optional)

    Returns:
        Maximum allocation recommendation with constraints.
    """
    try:
        symbol_normalized = _normalize_symbol(symbol)
        stock = yf.Ticker(symbol_normalized)
        info = stock.info

        if not info:
            return json.dumps({"error": f"Could not fetch info for {symbol}"})

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        sector = info.get("sector", "Unknown")
        market_cap = info.get("marketCap", 0)

        if not current_price:
            return json.dumps({"error": f"Could not fetch price for {symbol}"})

        # Market cap classification
        if market_cap > 500000000000:  # > 50,000 Cr
            cap_category = "large_cap"
            cap_limit = 25  # Can have higher allocation in large caps
        elif market_cap > 50000000000:  # > 5,000 Cr
            cap_category = "mid_cap"
            cap_limit = 15
        else:
            cap_category = "small_cap"
            cap_limit = 10  # Limit small cap exposure

        # Calculate sector constraint
        if current_sector_allocation:
            sector_alloc = json.loads(current_sector_allocation)
            current_in_sector = sector_alloc.get(sector, 0)
            remaining_sector_room = max_sector_percent - current_in_sector
        else:
            remaining_sector_room = max_sector_percent

        # Determine max allocation
        max_allowed = min(
            max_single_stock_percent,
            cap_limit,
            remaining_sector_room
        )

        max_value = portfolio_value * (max_allowed / 100)
        max_shares = int(max_value / current_price)

        # Volatility adjustment
        df = stock.history(period="3mo")
        if not df.empty:
            daily_returns = df['Close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100

            if volatility > 40:
                volatility_adjusted_max = max_allowed * 0.6
                vol_note = "Reduced due to high volatility"
            elif volatility > 25:
                volatility_adjusted_max = max_allowed * 0.8
                vol_note = "Slightly reduced due to moderate volatility"
            else:
                volatility_adjusted_max = max_allowed
                vol_note = "No volatility adjustment needed"
        else:
            volatility_adjusted_max = max_allowed
            vol_note = "Volatility data not available"
            volatility = None

        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol_normalized,
            "sector": sector,
            "market_cap_category": cap_category,
            "current_price": round(current_price, 2),

            "allocation_rules": {
                "max_single_stock": max_single_stock_percent,
                "max_sector": max_sector_percent,
                "cap_category_limit": cap_limit,
            },

            "calculated_limits": {
                "max_allocation_percent": round(max_allowed, 2),
                "max_value": round(max_value, 2),
                "max_shares": max_shares,
            },

            "volatility_adjustment": {
                "stock_volatility": round(volatility, 2) if volatility else None,
                "adjusted_max_percent": round(volatility_adjusted_max, 2),
                "adjusted_max_value": round(portfolio_value * (volatility_adjusted_max / 100), 2),
                "adjusted_max_shares": int(portfolio_value * (volatility_adjusted_max / 100) / current_price),
                "adjustment_note": vol_note,
            },

            "sector_context": {
                "stock_sector": sector,
                "current_sector_exposure": current_in_sector if current_sector_allocation else "unknown",
                "remaining_sector_room": round(remaining_sector_room, 2),
            },

            "recommendation": {
                "suggested_max_percent": round(volatility_adjusted_max, 2),
                "suggested_max_value": round(portfolio_value * (volatility_adjusted_max / 100), 2),
                "reasoning": _get_allocation_reasoning(cap_category, sector, volatility),
            },
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating max allocation: {str(e)}"})


def _get_allocation_reasoning(cap: str, sector: str, volatility: float) -> str:
    """Generate reasoning for allocation recommendation."""
    reasons = []

    if cap == "small_cap":
        reasons.append("Small cap stocks have higher risk, limiting allocation")
    elif cap == "large_cap":
        reasons.append("Large cap provides stability, allowing higher allocation")

    if volatility and volatility > 30:
        reasons.append("High volatility warrants smaller position")

    if not reasons:
        reasons.append("Standard allocation based on portfolio rules")

    return ". ".join(reasons) + "."
