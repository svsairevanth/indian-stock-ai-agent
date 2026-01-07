"""
Pydantic schemas for structured output from stock analysis agents.
These models ensure consistent, validated output from the multi-agent system.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class FundamentalAnalysis(BaseModel):
    """Structured output from fundamental analysis."""

    pe_ratio: Optional[float] = Field(
        default=None,
        description="Price to Earnings ratio"
    )
    forward_pe: Optional[float] = Field(
        default=None,
        description="Forward P/E ratio"
    )
    pb_ratio: Optional[float] = Field(
        default=None,
        description="Price to Book ratio"
    )
    roe: Optional[float] = Field(
        default=None,
        description="Return on Equity percentage"
    )
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Debt to Equity ratio"
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Revenue growth percentage YoY"
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin percentage"
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield percentage"
    )
    market_cap: Optional[float] = Field(
        default=None,
        description="Market capitalization in INR"
    )

    fundamental_score: float = Field(
        ge=0, le=10,
        description="Overall fundamental score from 0-10"
    )
    assessment: str = Field(
        description="Brief assessment of fundamentals"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Key fundamental strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Key fundamental weaknesses"
    )


class TechnicalAnalysis(BaseModel):
    """Structured output from technical analysis."""

    current_price: float = Field(
        description="Current stock price in INR"
    )
    rsi: float = Field(
        ge=0, le=100,
        description="Relative Strength Index value"
    )
    rsi_signal: Literal["Oversold", "Neutral", "Overbought"] = Field(
        description="RSI interpretation"
    )
    macd_value: Optional[float] = Field(
        default=None,
        description="MACD value"
    )
    macd_signal: Literal["Bullish", "Bearish", "Neutral"] = Field(
        description="MACD crossover signal"
    )
    trend: Literal["Strong Uptrend", "Uptrend", "Sideways", "Downtrend", "Strong Downtrend"] = Field(
        description="Overall trend direction"
    )
    trend_strength: Literal["Strong", "Moderate", "Weak"] = Field(
        description="Trend strength"
    )
    support_level: float = Field(
        description="Key support level in INR"
    )
    resistance_level: float = Field(
        description="Key resistance level in INR"
    )
    sma_20: Optional[float] = Field(
        default=None,
        description="20-day Simple Moving Average"
    )
    sma_50: Optional[float] = Field(
        default=None,
        description="50-day Simple Moving Average"
    )
    sma_200: Optional[float] = Field(
        default=None,
        description="200-day Simple Moving Average"
    )

    technical_score: float = Field(
        ge=0, le=10,
        description="Overall technical score from 0-10"
    )
    assessment: str = Field(
        description="Brief assessment of technicals"
    )
    signals: List[str] = Field(
        default_factory=list,
        description="Key technical signals observed"
    )


class SentimentAnalysis(BaseModel):
    """Structured output from sentiment analysis."""

    sentiment_score: float = Field(
        ge=-1, le=1,
        description="Overall sentiment score from -1 (negative) to +1 (positive)"
    )
    sentiment_label: Literal["Strongly Positive", "Positive", "Neutral", "Negative", "Strongly Negative"] = Field(
        description="Sentiment classification"
    )
    news_count: int = Field(
        ge=0,
        description="Number of news articles analyzed"
    )
    positive_count: int = Field(
        ge=0,
        description="Number of positive news articles"
    )
    negative_count: int = Field(
        ge=0,
        description="Number of negative news articles"
    )
    neutral_count: int = Field(
        ge=0,
        description="Number of neutral news articles"
    )

    key_positive_news: List[str] = Field(
        default_factory=list,
        description="Key positive headlines"
    )
    key_negative_news: List[str] = Field(
        default_factory=list,
        description="Key negative headlines"
    )
    assessment: str = Field(
        description="Brief assessment of news sentiment"
    )


class StockRecommendation(BaseModel):
    """
    Complete structured output for stock analysis recommendation.
    This is the final output type for the orchestrator agent.
    """

    # Basic Info
    symbol: str = Field(
        description="Stock symbol (e.g., RELIANCE.NS)"
    )
    company_name: str = Field(
        description="Full company name"
    )
    current_price: float = Field(
        description="Current stock price in INR"
    )
    currency: str = Field(
        default="INR",
        description="Currency"
    )

    # Recommendation
    recommendation: Literal["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"] = Field(
        description="Investment recommendation"
    )
    confidence: float = Field(
        ge=0, le=100,
        description="Confidence level 0-100%"
    )
    target_price: Optional[float] = Field(
        default=None,
        description="Target price for BUY recommendations"
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Recommended stop loss price"
    )
    upside_potential: Optional[float] = Field(
        default=None,
        description="Upside potential percentage"
    )
    time_horizon: Literal["Short-term (1-3 months)", "Medium-term (3-12 months)", "Long-term (1+ years)"] = Field(
        description="Recommended investment time horizon"
    )

    # Analysis Components
    fundamental_analysis: FundamentalAnalysis = Field(
        description="Fundamental analysis results"
    )
    technical_analysis: TechnicalAnalysis = Field(
        description="Technical analysis results"
    )
    sentiment_analysis: SentimentAnalysis = Field(
        description="Sentiment analysis results"
    )

    # Composite Scores
    overall_score: float = Field(
        ge=0, le=10,
        description="Weighted overall score (Fundamental 40% + Technical 35% + Sentiment 25%)"
    )

    # Arguments
    bull_case: str = Field(
        description="Bullish argument - reasons to buy"
    )
    bear_case: str = Field(
        description="Bearish argument - reasons for caution"
    )

    # Key Points
    key_positives: List[str] = Field(
        description="Key positive factors supporting the recommendation"
    )
    key_risks: List[str] = Field(
        description="Key risk factors to consider"
    )

    # Summary
    summary: str = Field(
        description="Executive summary of the analysis and recommendation"
    )

    analysis_date: str = Field(
        description="Date of analysis in YYYY-MM-DD format"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE.NS",
                "company_name": "Reliance Industries Limited",
                "current_price": 2450.50,
                "recommendation": "BUY",
                "confidence": 75.5,
                "target_price": 2800.00,
                "stop_loss": 2300.00,
                "time_horizon": "Medium-term (3-12 months)",
                "overall_score": 7.2,
                "summary": "Reliance shows strong fundamentals with diversified business..."
            }
        }
