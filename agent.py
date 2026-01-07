"""
Indian Stock Analyst Agent - Main agent implementation using OpenAI Agents SDK.
This agent analyzes Indian stocks and provides buy/sell/hold recommendations.
"""

from agents import Agent, Runner, ModelSettings
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import all tools
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
from pdf_generator import create_stock_report

from config import MODEL_NAME, AGENT_TEMPERATURE, MAX_TURNS


# Structured output for stock analysis
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


# Agent System Prompt
STOCK_ANALYST_INSTRUCTIONS = """
You are an expert Indian Stock Market Analyst AI specializing in NSE and BSE stocks.
Your role is to provide comprehensive stock analysis and actionable recommendations.

## Your Capabilities:
1. **Real-time Data**: Fetch current stock prices, trading volumes, and market data
2. **Fundamental Analysis**: Analyze P/E ratios, P/B ratios, ROE, debt levels, growth metrics
3. **Technical Analysis**: Calculate RSI, MACD, Moving Averages, Bollinger Bands, support/resistance
4. **News Analysis**: Gather and analyze recent news affecting the stock
5. **Report Generation**: Create professional PDF reports with recommendations

## Analysis Framework:
When analyzing a stock, you MUST:
1. First get the current stock price and basic info
2. Fetch fundamental data (P/E, P/B, market cap, etc.)
3. Calculate technical indicators (RSI, MACD, trend)
4. Get support and resistance levels
5. Fetch recent news about the stock
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

## Response Format:
After analysis, provide:
1. Clear BUY/SELL/HOLD recommendation
2. Target price (for BUY)
3. Stop loss level
4. Key supporting factors
5. Risk factors to consider
6. Investment time horizon

Remember: Indian stock symbols need .NS suffix for NSE or .BO for BSE. The tools will auto-add .NS if not provided.
"""


# Create the main stock analyst agent
stock_analyst_agent = Agent(
    name="Indian Stock Analyst",
    instructions=STOCK_ANALYST_INSTRUCTIONS,
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
        # PDF Generator
        create_stock_report,
    ],
)


# Convenience functions for running the agent
async def analyze_stock(query: str) -> str:
    """
    Analyze a stock based on user query.

    Args:
        query: User's question about a stock (e.g., "Should I buy RELIANCE?")

    Returns:
        Agent's analysis and recommendation.
    """
    result = await Runner.run(
        stock_analyst_agent,
        query,
        max_turns=MAX_TURNS,
    )
    return result.final_output


def analyze_stock_sync(query: str) -> str:
    """
    Synchronous version of analyze_stock.

    Args:
        query: User's question about a stock.

    Returns:
        Agent's analysis and recommendation.
    """
    result = Runner.run_sync(
        stock_analyst_agent,
        query,
        max_turns=MAX_TURNS,
    )
    return result.final_output


async def analyze_stock_streaming(query: str):
    """
    Analyze stock with streaming output.

    Args:
        query: User's question about a stock.

    Yields:
        Streaming events from the agent.
    """
    result = await Runner.run_streamed(
        stock_analyst_agent,
        query,
        max_turns=MAX_TURNS,
    )

    async for event in result.stream_events():
        yield event

    return result.final_output


# Interactive chat session
async def interactive_session():
    """Run an interactive chat session with the stock analyst."""
    print("\n" + "="*60)
    print("  INDIAN STOCK ANALYST AI  ")
    print("  Powered by OpenAI Agents SDK")
    print("="*60)
    print("\nWelcome! I can help you analyze Indian stocks (NSE/BSE).")
    print("Ask me about any stock, e.g., 'Should I buy RELIANCE?'")
    print("Type 'quit' or 'exit' to end the session.\n")

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
                stock_analyst_agent,
                full_input,
                max_turns=MAX_TURNS,
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
    asyncio.run(interactive_session())
