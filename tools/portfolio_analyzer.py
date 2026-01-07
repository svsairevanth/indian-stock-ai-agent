"""
Portfolio Analysis Tools - Functions for portfolio-level analysis including
health score, diversification, correlation, and rebalancing recommendations.
Inspired by Liquide's portfolio health tracking feature.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from agents import function_tool
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json


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
def analyze_portfolio_health(holdings_json: str) -> str:
    """Analyze the overall health of a portfolio of Indian stocks.

    Args:
        holdings_json: JSON string with holdings. Format:
                      [{"symbol": "RELIANCE", "quantity": 100, "avg_price": 2500},
                       {"symbol": "TCS", "quantity": 50, "avg_price": 3500}]

    Returns:
        Comprehensive portfolio health analysis including score, diversification, and recommendations.
    """
    try:
        holdings = json.loads(holdings_json)

        if not holdings or len(holdings) == 0:
            return json.dumps({"error": "No holdings provided"})

        portfolio_data = []
        total_investment = 0
        total_current_value = 0
        sectors = {}
        market_caps = {"large": 0, "mid": 0, "small": 0}

        # Analyze each holding
        for holding in holdings:
            symbol = _normalize_symbol(holding["symbol"])
            quantity = holding.get("quantity", 0)
            avg_price = holding.get("avg_price", 0)

            try:
                stock = yf.Ticker(symbol)
                info = stock.info

                current_price = info.get("currentPrice") or info.get("regularMarketPrice", avg_price)
                market_cap = info.get("marketCap", 0)
                sector = info.get("sector", "Unknown")

                investment = quantity * avg_price
                current_value = quantity * current_price
                pnl = current_value - investment
                pnl_pct = (pnl / investment * 100) if investment > 0 else 0

                total_investment += investment
                total_current_value += current_value

                # Sector allocation
                sectors[sector] = sectors.get(sector, 0) + current_value

                # Market cap classification
                if market_cap > 500000000000:  # > 50,000 Cr
                    market_caps["large"] += current_value
                elif market_cap > 50000000000:  # > 5,000 Cr
                    market_caps["mid"] += current_value
                else:
                    market_caps["small"] += current_value

                portfolio_data.append({
                    "symbol": symbol,
                    "name": info.get("shortName", symbol),
                    "sector": sector,
                    "quantity": quantity,
                    "avg_price": round(avg_price, 2),
                    "current_price": round(current_price, 2),
                    "investment": round(investment, 2),
                    "current_value": round(current_value, 2),
                    "pnl": round(pnl, 2),
                    "pnl_percent": round(pnl_pct, 2),
                    "market_cap_category": "Large Cap" if market_cap > 500000000000 else (
                        "Mid Cap" if market_cap > 50000000000 else "Small Cap"
                    ),
                })

            except Exception as e:
                portfolio_data.append({
                    "symbol": symbol,
                    "error": str(e),
                })

        # Calculate portfolio-level metrics
        total_pnl = total_current_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0

        # Weight calculations
        for item in portfolio_data:
            if "current_value" in item:
                item["weight_percent"] = round(item["current_value"] / total_current_value * 100, 2)

        # Sector allocation percentages
        sector_allocation = {
            sector: round(value / total_current_value * 100, 2)
            for sector, value in sectors.items()
        }

        # Market cap allocation
        cap_allocation = {
            cap: round(value / total_current_value * 100, 2)
            for cap, value in market_caps.items()
        }

        # Health Score Calculation (0-100)
        health_score = _calculate_health_score(
            portfolio_data, sector_allocation, cap_allocation, total_pnl_pct
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_investment": round(total_investment, 2),
                "current_value": round(total_current_value, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percent": round(total_pnl_pct, 2),
                "num_holdings": len([h for h in portfolio_data if "error" not in h]),
            },

            "health_score": health_score,

            "holdings": portfolio_data,

            "diversification": {
                "sector_allocation": sector_allocation,
                "market_cap_allocation": cap_allocation,
                "concentration_risk": _assess_concentration(portfolio_data),
            },

            "recommendations": _generate_recommendations(
                portfolio_data, sector_allocation, cap_allocation, health_score
            ),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing portfolio: {str(e)}"})


def _calculate_health_score(
    portfolio_data: List[Dict],
    sector_allocation: Dict,
    cap_allocation: Dict,
    total_pnl_pct: float
) -> Dict:
    """Calculate portfolio health score out of 100."""

    scores = {}

    # 1. Diversification Score (25 points)
    num_stocks = len([h for h in portfolio_data if "error" not in h])
    num_sectors = len(sector_allocation)

    if num_stocks >= 15:
        stock_diversity = 15
    elif num_stocks >= 10:
        stock_diversity = 12
    elif num_stocks >= 5:
        stock_diversity = 8
    else:
        stock_diversity = num_stocks

    if num_sectors >= 5:
        sector_diversity = 10
    elif num_sectors >= 3:
        sector_diversity = 7
    else:
        sector_diversity = num_sectors * 2

    scores["diversification"] = min(stock_diversity + sector_diversity, 25)

    # 2. Concentration Score (25 points)
    weights = [h.get("weight_percent", 0) for h in portfolio_data if "error" not in h]
    max_weight = max(weights) if weights else 0

    if max_weight <= 15:
        concentration_score = 25
    elif max_weight <= 25:
        concentration_score = 20
    elif max_weight <= 35:
        concentration_score = 15
    elif max_weight <= 50:
        concentration_score = 10
    else:
        concentration_score = 5

    scores["concentration"] = concentration_score

    # 3. Market Cap Balance (20 points)
    large_pct = cap_allocation.get("large", 0)
    mid_pct = cap_allocation.get("mid", 0)
    small_pct = cap_allocation.get("small", 0)

    # Ideal: 60% large, 25% mid, 15% small
    cap_score = 20
    if large_pct < 40:
        cap_score -= 5  # Too little in large caps (risky)
    if large_pct > 90:
        cap_score -= 5  # Too much in large caps (low growth)
    if small_pct > 30:
        cap_score -= 5  # Too much in small caps

    scores["market_cap_balance"] = max(cap_score, 5)

    # 4. Performance Score (15 points)
    if total_pnl_pct > 20:
        perf_score = 15
    elif total_pnl_pct > 10:
        perf_score = 12
    elif total_pnl_pct > 0:
        perf_score = 10
    elif total_pnl_pct > -10:
        perf_score = 7
    else:
        perf_score = 3

    scores["performance"] = perf_score

    # 5. Quality Score (15 points) - based on losers/winners ratio
    winners = len([h for h in portfolio_data if h.get("pnl_percent", 0) > 0])
    total = len([h for h in portfolio_data if "error" not in h])
    win_rate = winners / total if total > 0 else 0

    if win_rate >= 0.8:
        quality_score = 15
    elif win_rate >= 0.6:
        quality_score = 12
    elif win_rate >= 0.4:
        quality_score = 8
    else:
        quality_score = 4

    scores["quality"] = quality_score

    total_score = sum(scores.values())

    return {
        "total_score": total_score,
        "grade": _get_grade(total_score),
        "breakdown": scores,
        "interpretation": _interpret_score(total_score),
    }


def _get_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def _interpret_score(score: float) -> str:
    """Interpret health score."""
    if score >= 80:
        return "Excellent - Well-diversified, balanced portfolio"
    elif score >= 60:
        return "Good - Some improvements possible"
    elif score >= 40:
        return "Fair - Consider rebalancing"
    else:
        return "Needs Attention - Significant rebalancing recommended"


def _assess_concentration(portfolio_data: List[Dict]) -> Dict:
    """Assess portfolio concentration risk."""
    weights = sorted(
        [h.get("weight_percent", 0) for h in portfolio_data if "error" not in h],
        reverse=True
    )

    if not weights:
        return {"risk_level": "unknown"}

    top_1 = weights[0]
    top_3 = sum(weights[:3])
    top_5 = sum(weights[:5])

    risk_level = "low"
    if top_1 > 40:
        risk_level = "high"
    elif top_3 > 60:
        risk_level = "medium-high"
    elif top_5 > 80:
        risk_level = "medium"

    return {
        "risk_level": risk_level,
        "top_holding_weight": round(top_1, 2),
        "top_3_weight": round(top_3, 2),
        "top_5_weight": round(top_5, 2),
    }


def _generate_recommendations(
    portfolio_data: List[Dict],
    sector_allocation: Dict,
    cap_allocation: Dict,
    health_score: Dict
) -> List[str]:
    """Generate portfolio improvement recommendations."""
    recommendations = []

    # Concentration recommendations
    weights = sorted(
        [(h.get("symbol"), h.get("weight_percent", 0)) for h in portfolio_data if "error" not in h],
        key=lambda x: x[1],
        reverse=True
    )

    if weights and weights[0][1] > 30:
        recommendations.append(
            f"Consider reducing {weights[0][0]} position (currently {weights[0][1]}% of portfolio)"
        )

    # Sector recommendations
    if len(sector_allocation) < 3:
        recommendations.append("Increase sector diversification - add stocks from different sectors")

    # Market cap recommendations
    large_pct = cap_allocation.get("large", 0)
    small_pct = cap_allocation.get("small", 0)

    if large_pct < 40:
        recommendations.append("Consider adding large-cap stocks for stability")
    if small_pct > 30:
        recommendations.append("High small-cap exposure - consider reducing for lower risk")

    # Number of stocks
    num_stocks = len([h for h in portfolio_data if "error" not in h])
    if num_stocks < 5:
        recommendations.append("Portfolio too concentrated - consider adding more stocks")
    elif num_stocks > 25:
        recommendations.append("Too many holdings - consider consolidating to top picks")

    # Loss-making positions
    losers = [h for h in portfolio_data if h.get("pnl_percent", 0) < -20]
    if losers:
        recommendations.append(
            f"Review deep loss-making positions: {', '.join([l['symbol'] for l in losers])}"
        )

    if not recommendations:
        recommendations.append("Portfolio is well-balanced - maintain current allocation")

    return recommendations


@function_tool
def calculate_portfolio_correlation(symbols_json: str, period: str = "1y") -> str:
    """Calculate correlation matrix between stocks in a portfolio.

    Args:
        symbols_json: JSON list of stock symbols. Format: ["RELIANCE", "TCS", "HDFCBANK"]
        period: Historical period for correlation. Default: 1y

    Returns:
        Correlation matrix and diversification insights.
    """
    try:
        symbols = json.loads(symbols_json)

        if len(symbols) < 2:
            return json.dumps({"error": "Need at least 2 symbols for correlation analysis"})

        # Fetch historical data for all symbols
        price_data = {}

        for symbol in symbols:
            normalized = _normalize_symbol(symbol)
            try:
                stock = yf.Ticker(normalized)
                df = stock.history(period=period)
                if not df.empty:
                    price_data[symbol] = df['Close']
            except:
                continue

        if len(price_data) < 2:
            return json.dumps({"error": "Could not fetch data for enough symbols"})

        # Create DataFrame with aligned dates
        df = pd.DataFrame(price_data)
        df = df.dropna()

        # Calculate returns
        returns = df.pct_change().dropna()

        # Calculate correlation matrix
        correlation_matrix = returns.corr()

        # Convert to serializable format
        corr_dict = {}
        for symbol1 in correlation_matrix.columns:
            corr_dict[symbol1] = {}
            for symbol2 in correlation_matrix.columns:
                corr_dict[symbol1][symbol2] = round(correlation_matrix.loc[symbol1, symbol2], 3)

        # Find high correlations (potential diversification issues)
        high_correlations = []
        for i, sym1 in enumerate(symbols):
            if sym1 not in correlation_matrix.columns:
                continue
            for sym2 in symbols[i+1:]:
                if sym2 not in correlation_matrix.columns:
                    continue
                corr = correlation_matrix.loc[sym1, sym2]
                if abs(corr) > 0.7:
                    high_correlations.append({
                        "pair": f"{sym1}-{sym2}",
                        "correlation": round(corr, 3),
                        "concern": "high" if corr > 0.85 else "moderate",
                    })

        # Calculate average correlation
        correlations = []
        for i, sym1 in enumerate(correlation_matrix.columns):
            for sym2 in list(correlation_matrix.columns)[i+1:]:
                correlations.append(correlation_matrix.loc[sym1, sym2])

        avg_correlation = np.mean(correlations) if correlations else 0

        result = {
            "timestamp": datetime.now().isoformat(),
            "period": period,
            "symbols_analyzed": list(correlation_matrix.columns),

            "correlation_matrix": corr_dict,

            "summary": {
                "average_correlation": round(avg_correlation, 3),
                "diversification_quality": "good" if avg_correlation < 0.5 else (
                    "moderate" if avg_correlation < 0.7 else "poor"
                ),
                "high_correlation_pairs": high_correlations,
            },

            "interpretation": _interpret_correlation(avg_correlation, high_correlations),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating correlations: {str(e)}"})


def _interpret_correlation(avg_corr: float, high_pairs: List) -> str:
    """Interpret correlation analysis."""
    if avg_corr < 0.3:
        quality = "Excellent diversification - stocks move independently"
    elif avg_corr < 0.5:
        quality = "Good diversification - moderate independence"
    elif avg_corr < 0.7:
        quality = "Fair diversification - stocks tend to move together"
    else:
        quality = "Poor diversification - high correlation reduces benefits"

    if high_pairs:
        quality += f". Warning: {len(high_pairs)} highly correlated pairs found."

    return quality


@function_tool
def suggest_rebalancing(holdings_json: str, target_allocation_json: str = None) -> str:
    """Suggest trades to rebalance portfolio towards target allocation.

    Args:
        holdings_json: JSON string with current holdings.
                      Format: [{"symbol": "RELIANCE", "quantity": 100, "avg_price": 2500}]
        target_allocation_json: Optional target allocation.
                               Format: {"RELIANCE": 25, "TCS": 25, "HDFCBANK": 25, "INFY": 25}
                               If not provided, suggests equal weight.

    Returns:
        Rebalancing suggestions with buy/sell recommendations.
    """
    try:
        holdings = json.loads(holdings_json)

        if not holdings:
            return json.dumps({"error": "No holdings provided"})

        # Calculate current allocation
        portfolio_data = []
        total_value = 0

        for holding in holdings:
            symbol = _normalize_symbol(holding["symbol"])
            quantity = holding.get("quantity", 0)
            avg_price = holding.get("avg_price", 0)

            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                current_price = info.get("currentPrice") or info.get("regularMarketPrice", avg_price)
                current_value = quantity * current_price

                portfolio_data.append({
                    "symbol": holding["symbol"].upper(),
                    "quantity": quantity,
                    "current_price": round(current_price, 2),
                    "current_value": round(current_value, 2),
                })
                total_value += current_value
            except:
                continue

        if not portfolio_data:
            return json.dumps({"error": "Could not fetch data for holdings"})

        # Calculate current weights
        for item in portfolio_data:
            item["current_weight"] = round(item["current_value"] / total_value * 100, 2)

        # Determine target allocation
        if target_allocation_json:
            target = json.loads(target_allocation_json)
        else:
            # Equal weight
            equal_weight = 100 / len(portfolio_data)
            target = {item["symbol"]: equal_weight for item in portfolio_data}

        # Calculate rebalancing trades
        trades = []
        for item in portfolio_data:
            symbol = item["symbol"]
            current_weight = item["current_weight"]
            target_weight = target.get(symbol, 0)
            weight_diff = target_weight - current_weight

            target_value = total_value * (target_weight / 100)
            value_diff = target_value - item["current_value"]
            shares_diff = int(value_diff / item["current_price"])

            if abs(weight_diff) > 2:  # Only suggest if > 2% difference
                trades.append({
                    "symbol": symbol,
                    "action": "BUY" if shares_diff > 0 else "SELL",
                    "shares": abs(shares_diff),
                    "approximate_value": round(abs(value_diff), 2),
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "weight_change": round(weight_diff, 2),
                })

        result = {
            "timestamp": datetime.now().isoformat(),
            "portfolio_value": round(total_value, 2),

            "current_allocation": {
                item["symbol"]: item["current_weight"]
                for item in portfolio_data
            },

            "target_allocation": target,

            "rebalancing_trades": trades,

            "summary": {
                "num_trades": len(trades),
                "estimated_turnover": round(
                    sum(t["approximate_value"] for t in trades) / total_value * 100, 2
                ),
            },

            "note": "Consider transaction costs and taxes before executing rebalancing trades",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error suggesting rebalancing: {str(e)}"})


@function_tool
def analyze_portfolio_risk(holdings_json: str, period: str = "1y") -> str:
    """Analyze portfolio risk metrics including VaR, Sharpe Ratio, and max drawdown.

    Args:
        holdings_json: JSON string with holdings.
        period: Historical period for analysis. Default: 1y

    Returns:
        Comprehensive risk analysis of the portfolio.
    """
    try:
        holdings = json.loads(holdings_json)

        if not holdings:
            return json.dumps({"error": "No holdings provided"})

        # Build portfolio returns
        portfolio_data = []
        total_value = 0
        returns_data = {}

        for holding in holdings:
            symbol = _normalize_symbol(holding["symbol"])
            quantity = holding.get("quantity", 0)
            avg_price = holding.get("avg_price", 0)

            try:
                stock = yf.Ticker(symbol)
                df = stock.history(period=period)

                if not df.empty:
                    current_price = df['Close'].iloc[-1]
                    current_value = quantity * current_price

                    portfolio_data.append({
                        "symbol": holding["symbol"].upper(),
                        "current_value": current_value,
                    })
                    total_value += current_value

                    returns_data[holding["symbol"].upper()] = df['Close'].pct_change().dropna()
            except:
                continue

        if not portfolio_data or not returns_data:
            return json.dumps({"error": "Could not fetch data for risk analysis"})

        # Calculate weights
        weights = {
            item["symbol"]: item["current_value"] / total_value
            for item in portfolio_data
        }

        # Build portfolio returns series
        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.dropna()

        # Weight the returns
        portfolio_returns = pd.Series(0, index=returns_df.index)
        for symbol, weight in weights.items():
            if symbol in returns_df.columns:
                portfolio_returns += returns_df[symbol] * weight

        # Calculate risk metrics
        # 1. Volatility
        daily_vol = portfolio_returns.std()
        annual_vol = daily_vol * np.sqrt(252)

        # 2. Value at Risk (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)

        # 3. Maximum Drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # 4. Sharpe Ratio (assuming 6.5% risk-free rate)
        risk_free_daily = 0.065 / 252
        excess_returns = portfolio_returns - risk_free_daily
        sharpe_ratio = (excess_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

        # 5. Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else daily_vol
        sortino_ratio = (portfolio_returns.mean() * 252 - 0.065) / (downside_std * np.sqrt(252))

        # 6. Beta vs Nifty
        try:
            nifty = yf.Ticker("^NSEI")
            nifty_df = nifty.history(period=period)
            nifty_returns = nifty_df['Close'].pct_change().dropna()

            # Align dates
            common_idx = portfolio_returns.index.intersection(nifty_returns.index)
            port_aligned = portfolio_returns.loc[common_idx]
            nifty_aligned = nifty_returns.loc[common_idx]

            covariance = port_aligned.cov(nifty_aligned)
            nifty_variance = nifty_aligned.var()
            beta = covariance / nifty_variance if nifty_variance != 0 else 1.0
        except:
            beta = None

        result = {
            "timestamp": datetime.now().isoformat(),
            "period": period,
            "portfolio_value": round(total_value, 2),

            "volatility": {
                "daily_volatility": round(daily_vol * 100, 3),
                "annualized_volatility": round(annual_vol * 100, 2),
                "interpretation": "high" if annual_vol > 0.25 else (
                    "moderate" if annual_vol > 0.15 else "low"
                ),
            },

            "value_at_risk": {
                "var_95_daily": round(var_95 * 100, 2),
                "var_99_daily": round(var_99 * 100, 2),
                "var_95_amount": round(total_value * abs(var_95), 2),
                "interpretation": f"95% confidence: max daily loss of {round(abs(var_95) * 100, 2)}%",
            },

            "drawdown": {
                "max_drawdown_percent": round(max_drawdown * 100, 2),
                "interpretation": "severe" if max_drawdown < -0.20 else (
                    "significant" if max_drawdown < -0.10 else "manageable"
                ),
            },

            "risk_adjusted_returns": {
                "sharpe_ratio": round(sharpe_ratio, 2),
                "sortino_ratio": round(sortino_ratio, 2) if not np.isnan(sortino_ratio) else None,
                "sharpe_interpretation": "excellent" if sharpe_ratio > 1.5 else (
                    "good" if sharpe_ratio > 1 else (
                        "fair" if sharpe_ratio > 0.5 else "poor"
                    )
                ),
            },

            "market_risk": {
                "beta": round(beta, 2) if beta else None,
                "beta_interpretation": _interpret_beta_risk(beta) if beta else "Unknown",
            },

            "overall_risk_score": _calculate_risk_score(annual_vol, max_drawdown, sharpe_ratio, beta),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing portfolio risk: {str(e)}"})


def _interpret_beta_risk(beta: float) -> str:
    """Interpret beta for risk context."""
    if beta > 1.3:
        return "High market sensitivity - amplifies market moves"
    elif beta > 1.1:
        return "Above-market risk"
    elif beta > 0.9:
        return "Market-neutral"
    elif beta > 0.7:
        return "Defensive - less volatile than market"
    else:
        return "Very defensive - minimal market correlation"


def _calculate_risk_score(vol: float, max_dd: float, sharpe: float, beta: float) -> Dict:
    """Calculate overall risk score."""
    # Lower score = higher risk
    score = 100

    # Volatility penalty
    if vol > 0.30:
        score -= 30
    elif vol > 0.20:
        score -= 15

    # Drawdown penalty
    if max_dd < -0.25:
        score -= 25
    elif max_dd < -0.15:
        score -= 12

    # Sharpe bonus/penalty
    if sharpe > 1.0:
        score += 10
    elif sharpe < 0.5:
        score -= 15

    # Beta adjustment
    if beta and beta > 1.3:
        score -= 10

    score = max(0, min(100, score))

    return {
        "score": round(score),
        "risk_level": "low" if score > 70 else (
            "moderate" if score > 50 else "high"
        ),
        "interpretation": "Conservative portfolio" if score > 70 else (
            "Balanced risk profile" if score > 50 else "Aggressive/high-risk portfolio"
        ),
    }
