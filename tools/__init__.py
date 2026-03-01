"""
Tools package for the Indian Stock Analyst Agent.
Contains all function tools for stock data, analysis, news, and specialized capabilities.

Tool Categories:
1. Stock Data: Price, fundamentals, historical data
2. Technical Analysis: Indicators, support/resistance, trends
3. News & Sentiment: News fetching, sentiment analysis
4. Macro Data: India macro indicators, sector performance
5. Portfolio Analysis: Health score, correlation, rebalancing
6. Risk Management: Position sizing, stop loss, risk-reward
7. Document Analysis: Company filings, quarterly results, peer comparison
"""

# Stock Data Tools
from .stock_data import (
    get_stock_price,
    get_stock_info,
    get_historical_data,
    get_fundamentals,
)

# Technical Analysis Tools
from .technical_analysis import (
    get_technical_indicators,
    get_support_resistance,
    analyze_trend,
)

# News & Sentiment Tools
from .news_fetcher import (
    get_stock_news,
    get_market_news,
)

from .sentiment_analyzer import (
    analyze_news_sentiment,
    get_sentiment_score,
)

# News Intelligence Tools (Advanced Multi-Source Analysis)
from .news_intelligence import (
    fetch_comprehensive_news,
    analyze_news_with_events,
    get_sector_news,
    get_market_mood_index,
)
from .exa_research import (
    exa_web_search_stock_news,
    exa_company_snapshot,
    exa_deep_stock_research,
    exa_live_company_intelligence,
)

# Macro Data Tools
from .macro_data import (
    get_india_macro_indicators,
    get_nifty_benchmark_data,
    get_sector_performance,
    compare_stock_vs_benchmark,
    get_fii_dii_activity,
    get_global_market_context,
)

# Portfolio Analysis Tools
from .portfolio_analyzer import (
    analyze_portfolio_health,
    calculate_portfolio_correlation,
    suggest_rebalancing,
    analyze_portfolio_risk,
)

# Risk Management Tools
from .risk_management import (
    calculate_position_size,
    calculate_stop_loss_levels,
    assess_trade_risk_reward,
    calculate_max_allocation,
)

# Document Analysis Tools
from .document_analyzer import (
    fetch_company_announcements,
    analyze_quarterly_results,
    search_company_documents,
    get_management_commentary,
    get_peer_comparison,
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
    # News & Sentiment
    "get_stock_news",
    "get_market_news",
    "analyze_news_sentiment",
    "get_sentiment_score",
    # News Intelligence (Advanced)
    "fetch_comprehensive_news",
    "analyze_news_with_events",
    "get_sector_news",
    "get_market_mood_index",
    "exa_web_search_stock_news",
    "exa_company_snapshot",
    "exa_deep_stock_research",
    "exa_live_company_intelligence",
    # Macro Data
    "get_india_macro_indicators",
    "get_nifty_benchmark_data",
    "get_sector_performance",
    "compare_stock_vs_benchmark",
    "get_fii_dii_activity",
    "get_global_market_context",
    # Portfolio Analysis
    "analyze_portfolio_health",
    "calculate_portfolio_correlation",
    "suggest_rebalancing",
    "analyze_portfolio_risk",
    # Risk Management
    "calculate_position_size",
    "calculate_stop_loss_levels",
    "assess_trade_risk_reward",
    "calculate_max_allocation",
    # Document Analysis
    "fetch_company_announcements",
    "analyze_quarterly_results",
    "search_company_documents",
    "get_management_commentary",
    "get_peer_comparison",
]
