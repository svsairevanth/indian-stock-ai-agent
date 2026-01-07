"""
Indian Stock Analyst Agent - Multi-Agent Implementation using OpenAI Agents SDK.

This module provides a multi-agent system for comprehensive stock analysis:
- Orchestrator Agent: Coordinates analysis and synthesizes recommendations
- Fundamental Analyst: Analyzes company financials and valuation
- Technical Analyst: Analyzes price action and indicators
- Sentiment Analyst: Analyzes news sentiment and market mood

The system provides BUY/SELL/HOLD recommendations with professional PDF reports.
"""

from openai_sdk import Agent, Runner, ModelSettings
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import the multi-agent system
from agents.orchestrator import stock_orchestrator_agent
from agents.fundamental_analyst import fundamental_analyst_agent
from agents.technical_analyst import technical_analyst_agent
from agents.sentiment_analyst import sentiment_analyst_agent

# Import all tools (for backward compatibility and single-agent mode)
from tools.stock_data import (
    get_stock_price,
    get_stock_info,
    get_historical_data,
    get_fundamentals,
)
from tools.technical_analysis import (
    get_technical_indicators,
    get_support_resistance,
    analyze_trend,
)
from tools.news_fetcher import (
    get_stock_news,
    get_market_news,
)
from tools.sentiment_analyzer import (
    analyze_news_sentiment,
    get_sentiment_score,
)
from pdf_generator import create_stock_report

from config import MODEL_NAME, AGENT_TEMPERATURE, MAX_TURNS


# ============================================================================
# LEGACY SINGLE-AGENT (kept for backward compatibility)
# ============================================================================

# Structured output for stock analysis (legacy)
class StockAnalysisResult(BaseModel):
    """Structured output for stock analysis."""
    symbol: str = Field(description="Stock symbol analyzed")
    company_name: str = Field(description="Company name")
    recommendation: str = Field(description="BUY, SELL, or HOLD recommendation")
    confidence: float = Field(description="Confidence score 0-100")
    current_price: float = Field(description="Current stock price")
    target_price: Optional[float] = Field(description="Target price if BUY")
    stop_loss: Optional[float] = Field(description="Stop loss price")
    time_horizon: str = Field(description="Short-term, Medium-term, or Long-term")
    key_reasons: List[str] = Field(description="Key reasons for the recommendation")
    risk_factors: List[str] = Field(description="Key risk factors to consider")
    summary: str = Field(description="Brief summary of the analysis")


# Legacy single-agent instructions (kept for reference)
LEGACY_STOCK_ANALYST_INSTRUCTIONS = """
You are an expert Indian Stock Market Analyst AI specializing in NSE and BSE stocks.
Your role is to provide comprehensive stock analysis and actionable recommendations.

## Your Capabilities:
1. **Real-time Data**: Fetch current stock prices, trading volumes, and market data
2. **Fundamental Analysis**: Analyze P/E ratios, P/B ratios, ROE, debt levels, growth metrics
3. **Technical Analysis**: Calculate RSI, MACD, Moving Averages, Bollinger Bands, support/resistance
4. **News & Sentiment Analysis**: Gather and analyze recent news with sentiment scoring
5. **Report Generation**: Create professional PDF reports with recommendations

## Analysis Framework:
When analyzing a stock, you MUST:
1. First get the current stock price and basic info
2. Fetch fundamental data (P/E, P/B, market cap, etc.)
3. Calculate technical indicators (RSI, MACD, trend)
4. Get support and resistance levels
5. Fetch recent news and analyze sentiment
6. Synthesize all information into a recommendation

## Recommendation Criteria:

### BUY Signal (Strong):
- RSI < 40 (approaching oversold)
- Price near support levels
- Positive MACD crossover
- Strong fundamentals (reasonable P/E, good ROE)
- Uptrend confirmed
- Positive news sentiment

### SELL Signal:
- RSI > 70 (overbought)
- Price near resistance or breaking down
- Negative MACD crossover
- Deteriorating fundamentals
- Downtrend confirmed
- Negative news sentiment

### HOLD Signal:
- Mixed indicators
- Consolidating price action
- Waiting for clearer signals
- Neutral news

## For Users with Existing Positions:
If user mentions they already own the stock:
- Focus on whether to HOLD or SELL
- Calculate current profit/loss if purchase price is provided
- Provide trailing stop loss recommendations
- Assess if the original buy thesis is still valid

## Important Guidelines:
1. Always use the tools to fetch real data - NEVER make up numbers
2. Be objective and data-driven in your analysis
3. Clearly state confidence levels and uncertainties
4. Consider both upside potential and downside risks
5. Provide specific price targets when recommending BUY
6. Always recommend stop-loss levels for risk management
7. After completing analysis, ALWAYS generate a PDF report using create_stock_report tool

Remember: Indian stock symbols need .NS suffix for NSE or .BO for BSE. The tools will auto-add .NS if not provided.
"""


# Legacy single-agent (kept for backward compatibility)
stock_analyst_agent = Agent(
    name="Indian Stock Analyst",
    instructions=LEGACY_STOCK_ANALYST_INSTRUCTIONS,
    model=MODEL_NAME,
    model_settings=ModelSettings(
        temperature=AGENT_TEMPERATURE,
    ),
    tools=[
        # Stock Data Tools
        get_stock_price,
        get_stock_info,
        get_historical_data,
        get_fundamentals,
        # Technical Analysis Tools
        get_technical_indicators,
        get_support_resistance,
        analyze_trend,
        # News Tools
        get_stock_news,
        get_market_news,
        # Sentiment Analysis Tools
        analyze_news_sentiment,
        get_sentiment_score,
        # PDF Generator
        create_stock_report,
    ],
)


# ============================================================================
# MULTI-AGENT SYSTEM (NEW - RECOMMENDED)
# ============================================================================

# Export the multi-agent orchestrator as the primary agent
multi_agent_analyst = stock_orchestrator_agent


# ============================================================================
# RUNNER FUNCTIONS
# ============================================================================

async def analyze_stock(query: str, use_multi_agent: bool = True) -> str:
    """
    Analyze a stock based on user query.

    Args:
        query: User's question about a stock (e.g., "Should I buy RELIANCE?")
        use_multi_agent: If True, uses the multi-agent system (recommended).
                        If False, uses the legacy single agent.

    Returns:
        Agent's analysis and recommendation.
    """
    agent = multi_agent_analyst if use_multi_agent else stock_analyst_agent
    max_turns = MAX_TURNS * 2 if use_multi_agent else MAX_TURNS  # More turns for multi-agent

    result = await Runner.run(
        agent,
        query,
        max_turns=max_turns,
    )
    return result.final_output


def analyze_stock_sync(query: str, use_multi_agent: bool = True) -> str:
    """
    Synchronous version of analyze_stock.

    Args:
        query: User's question about a stock.
        use_multi_agent: If True, uses the multi-agent system.

    Returns:
        Agent's analysis and recommendation.
    """
    agent = multi_agent_analyst if use_multi_agent else stock_analyst_agent
    max_turns = MAX_TURNS * 2 if use_multi_agent else MAX_TURNS

    result = Runner.run_sync(
        agent,
        query,
        max_turns=max_turns,
    )
    return result.final_output


async def analyze_stock_streaming(query: str, use_multi_agent: bool = True):
    """
    Analyze stock with streaming output.

    Args:
        query: User's question about a stock.
        use_multi_agent: If True, uses the multi-agent system.

    Yields:
        Streaming events from the agent.
    """
    agent = multi_agent_analyst if use_multi_agent else stock_analyst_agent
    max_turns = MAX_TURNS * 2 if use_multi_agent else MAX_TURNS

    result = await Runner.run_streamed(
        agent,
        query,
        max_turns=max_turns,
    )

    async for event in result.stream_events():
        yield event

    # Note: final_output available via result.final_output after iteration


# Interactive chat session
async def interactive_session(use_multi_agent: bool = True):
    """
    Run an interactive chat session with the stock analyst.

    Args:
        use_multi_agent: If True, uses the multi-agent system (recommended).
    """
    agent_type = "Multi-Agent" if use_multi_agent else "Single-Agent"
    agent = multi_agent_analyst if use_multi_agent else stock_analyst_agent
    max_turns = MAX_TURNS * 2 if use_multi_agent else MAX_TURNS

    print("\n" + "="*60)
    print(f"  INDIAN STOCK ANALYST AI ({agent_type} System)")
    print("  Powered by OpenAI Agents SDK")
    print("="*60)
    print("\nWelcome! I can help you analyze Indian stocks (NSE/BSE).")
    print("Ask me about any stock, e.g., 'Should I buy RELIANCE?'")

    if use_multi_agent:
        print("\n[Multi-Agent Mode Active]")
        print("- Fundamental Analyst: Analyzing financials")
        print("- Technical Analyst: Analyzing charts")
        print("- Sentiment Analyst: Analyzing news")

    print("\nType 'quit' or 'exit' to end the session.\n")

    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using Indian Stock Analyst AI. Goodbye!")
                break

            # Build input with history for context
            if conversation_history:
                full_input = conversation_history + [{"role": "user", "content": user_input}]
            else:
                full_input = user_input

            print("\nAnalyzing... (this may take a moment)\n")

            # Run the agent
            result = await Runner.run(
                agent,
                full_input,
                max_turns=max_turns,
            )

            # Print the response
            print(f"Analyst: {result.final_output}")

            # Update conversation history
            conversation_history = result.to_input_list()

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with a different query.")


if __name__ == "__main__":
    import asyncio
    # Default to multi-agent mode
    asyncio.run(interactive_session(use_multi_agent=True))
