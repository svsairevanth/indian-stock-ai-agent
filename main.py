"""
Indian Stock Analyst Agent - Main Entry Point

This is the main entry point for the Indian Stock Analyst Agent.
Run this file to start analyzing stocks.

Usage:
    python main.py                    # Interactive mode
    python main.py "Analyze RELIANCE" # Single query mode
    python main.py --help             # Show help
"""

import asyncio
import sys
import os

# Ensure the project directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import (
    stock_analyst_agent,
    analyze_stock,
    analyze_stock_sync,
    interactive_session,
)
from agents import Runner
from config import MAX_TURNS, MODEL_NAME


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🇮🇳  INDIAN STOCK ANALYST AI  📈                            ║
    ║                                                               ║
    ║   Powered by OpenAI Agents SDK                                ║
    ║   Analyze NSE & BSE Stocks with AI                            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help information."""
    help_text = """
    USAGE:
        python main.py                      Start interactive session
        python main.py "<query>"            Analyze with single query
        python main.py --help               Show this help message

    EXAMPLES:
        python main.py "Should I buy RELIANCE?"
        python main.py "Analyze TCS stock for investment"
        python main.py "I own INFY at 1500, should I hold or sell?"
        python main.py "Compare HDFCBANK and ICICIBANK"

    SUPPORTED STOCKS:
        - All NSE stocks (use symbol like RELIANCE, TCS, INFY)
        - All BSE stocks (add .BO suffix like RELIANCE.BO)
        - Indian indices (NIFTY50, SENSEX)

    FEATURES:
        - Real-time price data
        - Fundamental analysis (P/E, P/B, ROE, etc.)
        - Technical analysis (RSI, MACD, Moving Averages)
        - Support & Resistance levels
        - News sentiment analysis
        - PDF report generation

    ENVIRONMENT SETUP:
        Set your OpenAI API key:
        export OPENAI_API_KEY=your-api-key-here

        Or create a .env file:
        OPENAI_API_KEY=your-api-key-here
    """
    print(help_text)


async def single_query_mode(query: str):
    """Run a single query and print the result."""
    print(f"\n📊 Analyzing: {query}\n")
    print("-" * 50)

    try:
        result = await Runner.run(
            stock_analyst_agent,
            query,
            max_turns=MAX_TURNS,
        )
        print(f"\n{result.final_output}")

        # Check if PDF was generated
        for item in result.new_items:
            if hasattr(item, 'output') and 'pdf_path' in str(item.output):
                print("\n📄 PDF Report has been generated!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your OPENAI_API_KEY is set correctly")
        print("2. You have internet connectivity")
        print("3. The stock symbol is valid")


async def main():
    """Main entry point."""
    print_banner()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("Please set your API key:")
        print("  export OPENAI_API_KEY=your-api-key-here")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=your-api-key-here\n")

    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg in ['--help', '-h', 'help']:
            print_help()
            return

        # Single query mode
        query = ' '.join(sys.argv[1:])
        await single_query_mode(query)
    else:
        # Interactive mode
        print(f"\n🤖 Model: {MODEL_NAME}")
        print(f"📁 Reports will be saved to: reports/")
        await interactive_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)
