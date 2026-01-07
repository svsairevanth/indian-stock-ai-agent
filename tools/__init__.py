"""
Tools package for the Indian Stock Analyst Agent.
Contains all function tools for stock data, analysis, and news.
"""

from .stock_data import (
    get_stock_price,
    get_stock_info,
    get_historical_data,
    get_fundamentals,
)

from .technical_analysis import (
    get_technical_indicators,
    get_support_resistance,
    analyze_trend,
)

from .news_fetcher import (
    get_stock_news,
    get_market_news,
)

__all__ = [
    # Stock Data
    "get_stock_price",
    "get_stock_info",
    "get_historical_data",
    "get_fundamentals",
    # Technical Analysis
    "get_technical_indicators",
    "get_support_resistance",
    "analyze_trend",
    # News
    "get_stock_news",
    "get_market_news",
]
