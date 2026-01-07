"""
Pipeline Orchestrator - Sequential Multi-Agent Execution

This module implements the Sequential Runner Pattern for guaranteed agent execution.
Each agent runs in order and passes context to the next agent.

This is more reliable than handoff-based orchestration because:
1. Every agent is guaranteed to run
2. No reliance on LLM to correctly hand off
3. Deterministic execution order
"""

import asyncio
import yfinance as yf
import json
from openai_sdk import Agent, Runner, ModelSettings

# Import all specialist agents
from .fundamental_analyst import fundamental_analyst_agent
from .technical_analyst import technical_analyst_agent
from .sentiment_analyst import sentiment_analyst_agent
from .news_intelligence_agent import news_intelligence_agent  # Enhanced news analysis
from .macro_analyst import macro_analyst_agent
from .document_analyst import document_analyst_agent
from .bull_agent import bull_agent
from .bear_agent import bear_agent
from .debate_judge import debate_judge_agent
from .risk_manager import risk_manager_agent

# Import PDF generator
from pdf_generator import generate_stock_report, StockReportData, create_stock_report

from config import MODEL_NAME, AGENT_TEMPERATURE, MAX_TURNS


def fetch_raw_stock_data(symbol: str) -> dict:
    """
    Fetch raw stock data directly from yfinance.
    This data is AUTHORITATIVE and should not be modified by LLM.

    Args:
        symbol: Stock symbol (e.g., "TCS", "RELIANCE")

    Returns:
        Dictionary with raw stock data
    """
    # Normalize symbol
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = f"{symbol}.NS"

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Helper to safely get values
        def safe_get(key, default=None):
            import math
            value = info.get(key, default)
            if value is None:
                return default
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return default
            return value

        # Extract all needed data
        current_price = safe_get("currentPrice") or safe_get("regularMarketPrice")
        prev_close = safe_get("previousClose", 0)

        data = {
            "symbol": symbol,
            "company_name": safe_get("longName", symbol),

            # Price data (AUTHORITATIVE - do not let LLM modify)
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(prev_close, 2) if prev_close else None,
            "day_change": round(current_price - prev_close, 2) if current_price and prev_close else None,
            "day_change_percent": round(((current_price - prev_close) / prev_close) * 100, 2) if current_price and prev_close else None,
            "week_52_high": round(safe_get("fiftyTwoWeekHigh", 0), 2) if safe_get("fiftyTwoWeekHigh") else None,
            "week_52_low": round(safe_get("fiftyTwoWeekLow", 0), 2) if safe_get("fiftyTwoWeekLow") else None,

            # Fundamental data (AUTHORITATIVE)
            "pe_ratio": round(safe_get("trailingPE", 0), 2) if safe_get("trailingPE") else None,
            "pb_ratio": round(safe_get("priceToBook", 0), 2) if safe_get("priceToBook") else None,
            "market_cap": safe_get("marketCap"),
            "roe": safe_get("returnOnEquity"),  # Decimal format (0.47 = 47%)
            "debt_to_equity": round(safe_get("debtToEquity", 0), 2) if safe_get("debtToEquity") else None,
            "dividend_yield": safe_get("dividendYield"),  # Can be decimal or percentage

            # Company info
            "sector": safe_get("sector", "N/A"),
            "industry": safe_get("industry", "N/A"),
        }

        print(f"     [DATA] Fetched raw data: Price={data['current_price']}, 52W High={data['week_52_high']}, 52W Low={data['week_52_low']}, ROE={data['roe']}")
        return data

    except Exception as e:
        print(f"     [ERROR] Failed to fetch raw data: {e}")
        return {
            "symbol": symbol,
            "company_name": symbol,
            "current_price": None,
            "error": str(e)
        }


async def run_stock_analysis_pipeline(stock_symbol: str, user_query: str) -> dict:
    """
    Run the complete stock analysis pipeline with all agents.

    This function runs each agent sequentially, guaranteeing that
    all agents participate in the analysis.

    Args:
        stock_symbol: The stock symbol to analyze (e.g., "RELIANCE", "TCS")
        user_query: The original user query

    Returns:
        Dictionary containing all analysis results and final recommendation
    """
    results = {
        "stock_symbol": stock_symbol,
        "user_query": user_query,
        "agents_run": [],
        "raw_data": None,  # AUTHORITATIVE stock data from yfinance
        "fundamental": None,
        "technical": None,
        "news_intelligence": None,  # NEW: Advanced news analysis
        "sentiment": None,
        "macro": None,
        "document": None,
        "bull_case": None,
        "bear_case": None,
        "debate_verdict": None,
        "risk_assessment": None,
        "final_recommendation": None,
    }

    print(f"\n[Pipeline] Starting analysis for {stock_symbol}")
    print("=" * 60)

    # ========== PHASE 0: FETCH RAW DATA ==========
    print("\n[Phase 0] Fetching Authoritative Stock Data")
    print("-" * 40)
    print("[0/10] Fetching raw data from yfinance...")
    results["raw_data"] = fetch_raw_stock_data(stock_symbol)
    print("     [OK] Raw data fetched (this data will be used directly in PDF)")

    # ========== PHASE 1: DATA GATHERING ==========
    print("\n[Phase 1] Data Gathering")
    print("-" * 40)

    # Step 1: Fundamental Analysis
    print("[1/9] Running Fundamental Analyst...")
    try:
        result = await Runner.run(
            fundamental_analyst_agent,
            f"Analyze the fundamentals of {stock_symbol} stock. Provide valuation, profitability, financial health, and growth analysis.",
            max_turns=MAX_TURNS,
        )
        results["fundamental"] = result.final_output
        results["agents_run"].append("Fundamental Analyst")
        print("     [OK] Fundamental analysis complete")
    except Exception as e:
        print(f"     [ERROR] Fundamental analysis failed: {e}")
        results["fundamental"] = f"Error: {e}"

    # Step 2: Technical Analysis
    print("[2/9] Running Technical Analyst...")
    try:
        result = await Runner.run(
            technical_analyst_agent,
            f"Analyze the technical indicators for {stock_symbol} stock. Include RSI, MACD, moving averages, support/resistance levels, and trend analysis.",
            max_turns=MAX_TURNS,
        )
        results["technical"] = result.final_output
        results["agents_run"].append("Technical Analyst")
        print("     [OK] Technical analysis complete")
    except Exception as e:
        print(f"     [ERROR] Technical analysis failed: {e}")
        results["technical"] = f"Error: {e}"

    # Step 3: News Intelligence Analysis (Enhanced)
    print("[3/10] Running News Intelligence Analyst...")
    try:
        result = await Runner.run(
            news_intelligence_agent,
            f"""Analyze news for {stock_symbol} stock:
1. Fetch comprehensive news from multiple sources using fetch_comprehensive_news
2. Analyze with event detection using analyze_news_with_events
3. Get sector news for context
4. Check market mood

Provide a complete news intelligence report with events detected, impact scores, and news-based recommendation.""",
            max_turns=MAX_TURNS,
        )
        results["news_intelligence"] = result.final_output
        results["agents_run"].append("News Intelligence Analyst")
        print("     [OK] News intelligence analysis complete")
    except Exception as e:
        print(f"     [ERROR] News intelligence failed: {e}")
        results["news_intelligence"] = f"Error: {e}"

    # Step 3b: Basic Sentiment Analysis (backup/additional)
    print("[3b/10] Running Sentiment Analyst (backup)...")
    try:
        result = await Runner.run(
            sentiment_analyst_agent,
            f"Analyze the news sentiment for {stock_symbol} stock. Fetch recent news and provide sentiment scores.",
            max_turns=MAX_TURNS,
        )
        results["sentiment"] = result.final_output
        results["agents_run"].append("Sentiment Analyst")
        print("     [OK] Sentiment analysis complete")
    except Exception as e:
        print(f"     [ERROR] Sentiment analysis failed: {e}")
        results["sentiment"] = f"Error: {e}"

    # Step 4: Macro Analysis
    print("[4/9] Running Macro Analyst...")
    try:
        result = await Runner.run(
            macro_analyst_agent,
            f"Analyze the macroeconomic context for {stock_symbol} stock. Include RBI policy impact, sector performance, and benchmark comparison.",
            max_turns=MAX_TURNS,
        )
        results["macro"] = result.final_output
        results["agents_run"].append("Macro Analyst")
        print("     [OK] Macro analysis complete")
    except Exception as e:
        print(f"     [ERROR] Macro analysis failed: {e}")
        results["macro"] = f"Error: {e}"

    # Step 5: Document Analysis
    print("[5/9] Running Document Analyst...")
    try:
        result = await Runner.run(
            document_analyst_agent,
            f"Analyze quarterly results and company announcements for {stock_symbol} stock. Include peer comparison if available.",
            max_turns=MAX_TURNS,
        )
        results["document"] = result.final_output
        results["agents_run"].append("Document Analyst")
        print("     [OK] Document analysis complete")
    except Exception as e:
        print(f"     [ERROR] Document analysis failed: {e}")
        results["document"] = f"Error: {e}"

    # ========== PHASE 2: DEBATE ==========
    print("\n[Phase 2] Bull vs Bear Debate")
    print("-" * 40)

    # Compile all analysis for debate
    all_analysis = f"""
## Analysis Data for {stock_symbol}

### Fundamental Analysis:
{results['fundamental']}

### Technical Analysis:
{results['technical']}

### Sentiment Analysis:
{results['sentiment']}

### Macro Analysis:
{results['macro']}

### Document Analysis:
{results['document']}
"""

    # Step 6: Bull Case
    print("[6/9] Running Bull Advocate...")
    try:
        result = await Runner.run(
            bull_agent,
            f"Based on the following analysis data, build the strongest BULLISH case for {stock_symbol}:\n\n{all_analysis}",
            max_turns=MAX_TURNS,
        )
        results["bull_case"] = result.final_output
        results["agents_run"].append("Bull Advocate")
        print("     [OK] Bull case complete")
    except Exception as e:
        print(f"     [ERROR] Bull case failed: {e}")
        results["bull_case"] = f"Error: {e}"

    # Step 7: Bear Case
    print("[7/9] Running Bear Advocate...")
    try:
        result = await Runner.run(
            bear_agent,
            f"Based on the following analysis data, build the strongest BEARISH case for {stock_symbol}:\n\n{all_analysis}",
            max_turns=MAX_TURNS,
        )
        results["bear_case"] = result.final_output
        results["agents_run"].append("Bear Advocate")
        print("     [OK] Bear case complete")
    except Exception as e:
        print(f"     [ERROR] Bear case failed: {e}")
        results["bear_case"] = f"Error: {e}"

    # Step 8: Debate Judge
    print("[8/9] Running Debate Judge...")
    try:
        debate_input = f"""
## Bull Case for {stock_symbol}:
{results['bull_case']}

## Bear Case for {stock_symbol}:
{results['bear_case']}

Please judge this debate and provide your verdict with a recommendation.
"""
        result = await Runner.run(
            debate_judge_agent,
            debate_input,
            max_turns=MAX_TURNS,
        )
        results["debate_verdict"] = result.final_output
        results["agents_run"].append("Debate Judge")
        print("     [OK] Debate verdict complete")
    except Exception as e:
        print(f"     [ERROR] Debate verdict failed: {e}")
        results["debate_verdict"] = f"Error: {e}"

    # ========== PHASE 3: RISK ASSESSMENT ==========
    print("\n[Phase 3] Risk Assessment")
    print("-" * 40)

    # Step 9: Risk Manager
    print("[9/9] Running Risk Manager...")
    try:
        result = await Runner.run(
            risk_manager_agent,
            f"Provide risk management recommendations for {stock_symbol} including position sizing, stop loss levels, and risk-reward assessment.",
            max_turns=MAX_TURNS,
        )
        results["risk_assessment"] = result.final_output
        results["agents_run"].append("Risk Manager")
        print("     [OK] Risk assessment complete")
    except Exception as e:
        print(f"     [ERROR] Risk assessment failed: {e}")
        results["risk_assessment"] = f"Error: {e}"

    print("\n" + "=" * 60)
    print(f"[Pipeline] Analysis complete! Agents run: {len(results['agents_run'])}/9")
    print("=" * 60)

    return results


def format_final_report(results: dict) -> str:
    """
    Format all analysis results into a final report.

    Args:
        results: Dictionary containing all analysis results

    Returns:
        Formatted string report
    """
    report = f"""
================================================================================
                    COMPREHENSIVE STOCK ANALYSIS REPORT
                           {results['stock_symbol']}
================================================================================

AGENTS THAT PARTICIPATED: {len(results['agents_run'])}/10
{', '.join(results['agents_run'])}

================================================================================
                           FUNDAMENTAL ANALYSIS
================================================================================
{results['fundamental']}

================================================================================
                            TECHNICAL ANALYSIS
================================================================================
{results['technical']}

================================================================================
                       NEWS INTELLIGENCE ANALYSIS
================================================================================
{results.get('news_intelligence', 'Not available')}

================================================================================
                           SENTIMENT ANALYSIS
================================================================================
{results['sentiment']}

================================================================================
                         MACROECONOMIC ANALYSIS
================================================================================
{results['macro']}

================================================================================
                           DOCUMENT ANALYSIS
================================================================================
{results['document']}

================================================================================
                              BULL CASE
================================================================================
{results['bull_case']}

================================================================================
                              BEAR CASE
================================================================================
{results['bear_case']}

================================================================================
                            DEBATE VERDICT
================================================================================
{results['debate_verdict']}

================================================================================
                           RISK ASSESSMENT
================================================================================
{results['risk_assessment']}

================================================================================
"""
    return report


# Create a simple orchestrator agent for generating final PDF
FINAL_ORCHESTRATOR_INSTRUCTIONS = """
You are the Final Report Generator. You receive comprehensive analysis from 9 specialist agents.

Your ONLY job is to:
1. Review all the analysis provided
2. Extract ALL key metrics carefully
3. Determine final recommendation (BUY/SELL/HOLD)
4. Generate a PDF report using the create_stock_report tool with ALL parameters

You MUST call the create_stock_report tool with ALL available data. Do NOT leave fields empty if the data exists in the analysis.

## CRITICAL VALIDATION RULES:
1. **Stop Loss MUST be BELOW current price** - A stop loss is a protective level to sell if price drops. If you extract a stop loss that is ABOVE the current price, you have made an error. Re-read the analysis.
2. **Target Price should typically be ABOVE current price** for BUY recommendations
3. **52-Week High must be >= Current Price** - It's the highest price in the last year
4. **52-Week Low must be <= Current Price** - It's the lowest price in the last year
5. **ROE and Dividend Yield are decimals** - 9.72% ROE should be passed as 0.0972

CAREFULLY EXTRACT these from the analysis:

## Required Fields:
- symbol: Stock symbol (e.g., "RELIANCE.NS")
- company_name: Full company name
- current_price: Current stock price (number)
- recommendation: BUY, SELL, or HOLD
- confidence_score: 0-100 (number)
- detailed_analysis: Summary combining all analysis (text)

## Fundamental Metrics (from Fundamental Analysis section):
Look for these EXACT patterns in the Fundamental Analysis:
- pe_ratio: Find "P/E Ratio: X" or "Trailing PE: X" -> use X
- pb_ratio: Find "P/B Ratio: X" or "Price to Book: X" -> use X
- market_cap: Find "Market Cap: X" -> use X (as number, e.g., 5000000000000)
- roe: Find "ROE: X%" or "Return on Equity: X%" -> DIVIDE by 100 (9.72% -> 0.0972)
- debt_to_equity: Find "Debt to Equity: X" -> use X
- dividend_yield: Find "Dividend Yield: X%" -> DIVIDE by 100 (0.36% -> 0.0036)

## Price Data (look in Fundamental Analysis or Stock Price section):
- week_52_high: Find "52-Week High: X" or "52 Week High: X" -> use X
- week_52_low: Find "52-Week Low: X" or "52 Week Low: X" -> use X
- day_change: Day price change (number, can be negative)
- day_change_percent: Day change percentage (number)

## Technical Metrics (from Technical Analysis section):
- rsi: Find "RSI: X" or "RSI (14): X" -> use X
- macd_signal: Find MACD description -> "bullish", "bearish", or "neutral"
- trend_direction: Find trend description -> "uptrend", "downtrend", or "sideways"
- support_level: Find "Support: X" or "Support Level: X" -> use X
- resistance_level: Find "Resistance: X" or "Resistance Level: X" -> use X

## Risk Data (from Risk Assessment section):
- target_price: Find "Target Price: X" or "Target: X" -> use X (should be > current_price for BUY)
- stop_loss: Find "Stop Loss: X" -> use X (MUST be < current_price - this is critical!)
- investment_horizon: "Short-term", "Medium-term", or "Long-term"

## Analysis Summary:
- positive_factors: Comma-separated list of 5 key positives from Bull case
- risk_factors: Comma-separated list of 5 key risks from Bear case

## Example Extraction:
If you see in the analysis:
```
Current Price: 1500.25
52-Week High: 1611.80
52-Week Low: 1114.85
ROE: 9.72%
Dividend Yield: 0.36%
Stop Loss: 1395.00 (below current price)
Target: 1750.00
```

You should pass:
- current_price: 1500.25
- week_52_high: 1611.80
- week_52_low: 1114.85
- roe: 0.0972 (divided by 100)
- dividend_yield: 0.0036 (divided by 100)
- stop_loss: 1395.00 (must be less than 1500.25)
- target_price: 1750.00

REMEMBER: If stop_loss > current_price, you have extracted the WRONG value!
"""

final_orchestrator_agent = Agent(
    name="Final Report Generator",
    instructions=FINAL_ORCHESTRATOR_INSTRUCTIONS,
    model=MODEL_NAME,
    model_settings=ModelSettings(
        temperature=0.2,
    ),
    tools=[
        create_stock_report,
    ],
)


def extract_technical_metrics(technical_analysis: str) -> dict:
    """
    Extract technical metrics from the technical analysis text.
    Uses simple pattern matching for reliability.
    """
    import re

    metrics = {
        "rsi": None,
        "macd_signal": None,
        "trend_direction": None,
        "support_level": None,
        "resistance_level": None,
    }

    if not technical_analysis:
        return metrics

    text = technical_analysis.lower()

    # Extract RSI
    rsi_match = re.search(r'rsi[:\s]*(\d+\.?\d*)', text)
    if rsi_match:
        metrics["rsi"] = float(rsi_match.group(1))

    # Extract MACD signal
    if 'macd' in text:
        if 'bullish' in text.split('macd')[1][:100]:
            metrics["macd_signal"] = "bullish"
        elif 'bearish' in text.split('macd')[1][:100]:
            metrics["macd_signal"] = "bearish"
        else:
            metrics["macd_signal"] = "neutral"

    # Extract trend direction
    if 'uptrend' in text or 'strong uptrend' in text:
        metrics["trend_direction"] = "uptrend"
    elif 'downtrend' in text:
        metrics["trend_direction"] = "downtrend"
    else:
        metrics["trend_direction"] = "sideways"

    # Extract support level
    support_match = re.search(r'support[:\s]*₹?(\d+\.?\d*)', text)
    if support_match:
        metrics["support_level"] = float(support_match.group(1))
    else:
        # Try alternative pattern
        support_match = re.search(r'immediate support[:\s]*₹?(\d+\.?\d*)', text)
        if support_match:
            metrics["support_level"] = float(support_match.group(1))

    # Extract resistance level
    resistance_match = re.search(r'resistance[:\s]*₹?(\d+\.?\d*)', text)
    if resistance_match:
        metrics["resistance_level"] = float(resistance_match.group(1))

    return metrics


def extract_risk_metrics(risk_assessment: str, current_price: float) -> dict:
    """
    Extract risk metrics from the risk assessment text.
    Validates stop loss is below current price.
    """
    import re

    metrics = {
        "target_price": None,
        "stop_loss": None,
        "investment_horizon": "Medium-term",
    }

    if not risk_assessment:
        return metrics

    text = risk_assessment

    # Extract target price
    target_match = re.search(r'target[:\s]*₹?(\d+\.?\d*)', text, re.IGNORECASE)
    if target_match:
        metrics["target_price"] = float(target_match.group(1))

    # Extract stop loss - VALIDATE it's below current price
    stop_matches = re.findall(r'stop[:\s]*₹?(\d+\.?\d*)', text, re.IGNORECASE)
    for match in stop_matches:
        stop_value = float(match)
        if current_price and stop_value < current_price:
            metrics["stop_loss"] = stop_value
            break

    # If no valid stop loss found, try to find primary stop
    if not metrics["stop_loss"]:
        primary_match = re.search(r'primary stop[:\s]*₹?(\d+\.?\d*)', text, re.IGNORECASE)
        if primary_match:
            stop_value = float(primary_match.group(1))
            if current_price and stop_value < current_price:
                metrics["stop_loss"] = stop_value

    # Extract investment horizon
    if 'short-term' in text.lower() or 'short term' in text.lower():
        metrics["investment_horizon"] = "Short-term"
    elif 'long-term' in text.lower() or 'long term' in text.lower():
        metrics["investment_horizon"] = "Long-term"
    else:
        metrics["investment_horizon"] = "Medium-term"

    return metrics


def determine_recommendation(debate_verdict: str) -> tuple:
    """
    Extract recommendation and confidence from debate verdict.
    """
    if not debate_verdict:
        return "HOLD", 50

    text = debate_verdict.upper()

    # Determine recommendation
    if 'STRONG BUY' in text:
        recommendation = "BUY"
        base_confidence = 85
    elif 'BUY' in text and 'SELL' not in text:
        recommendation = "BUY"
        base_confidence = 70
    elif 'STRONG SELL' in text:
        recommendation = "SELL"
        base_confidence = 85
    elif 'SELL' in text:
        recommendation = "SELL"
        base_confidence = 70
    else:
        recommendation = "HOLD"
        base_confidence = 60

    # Try to extract confidence from text
    import re
    confidence_match = re.search(r'confidence[:\s]*(\d+)', debate_verdict, re.IGNORECASE)
    if confidence_match:
        base_confidence = int(confidence_match.group(1))

    return recommendation, min(max(base_confidence, 0), 100)


def extract_factors(bull_case: str, bear_case: str) -> tuple:
    """
    Extract positive and risk factors from bull and bear cases.
    """
    import re

    positive_factors = []
    risk_factors = []

    # Extract from bull case
    if bull_case:
        # Look for numbered or bulleted points
        lines = bull_case.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                clean_line = re.sub(r'^[-•*\d.]+\s*', '', line).strip()
                if len(clean_line) > 10 and len(positive_factors) < 5:
                    positive_factors.append(clean_line[:100])

    # Extract from bear case
    if bear_case:
        lines = bear_case.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                clean_line = re.sub(r'^[-•*\d.]+\s*', '', line).strip()
                if len(clean_line) > 10 and len(risk_factors) < 5:
                    risk_factors.append(clean_line[:100])

    # Default factors if none found
    if not positive_factors:
        positive_factors = ["Strong fundamentals", "Market leadership", "Growth potential"]
    if not risk_factors:
        risk_factors = ["Market volatility", "Sector headwinds", "Valuation concerns"]

    return positive_factors, risk_factors


async def run_full_analysis_with_pdf(stock_symbol: str, user_query: str) -> str:
    """
    Run the complete analysis pipeline and generate PDF report.
    Uses DIRECT data from yfinance for numerical values (no LLM extraction).

    Args:
        stock_symbol: Stock symbol to analyze
        user_query: Original user query

    Returns:
        Final output including PDF path
    """
    # Step 1: Run the analysis pipeline
    results = await run_stock_analysis_pipeline(stock_symbol, user_query)

    # Step 2: Format the report
    formatted_report = format_final_report(results)

    # Step 3: Generate PDF DIRECTLY using raw data (no LLM extraction!)
    print("\n[Final Step] Generating PDF Report (using authoritative data)...")

    try:
        raw_data = results.get("raw_data", {})
        current_price = raw_data.get("current_price")

        # Extract technical metrics from analysis text
        tech_metrics = extract_technical_metrics(results.get("technical", ""))

        # Extract risk metrics (with validation)
        risk_metrics = extract_risk_metrics(results.get("risk_assessment", ""), current_price)

        # Determine recommendation from debate
        recommendation, confidence = determine_recommendation(results.get("debate_verdict", ""))

        # Extract positive and risk factors
        positive_factors, risk_factors = extract_factors(
            results.get("bull_case", ""),
            results.get("bear_case", "")
        )

        # Create detailed analysis summary
        detailed_analysis = f"""
{results.get('stock_symbol', stock_symbol)} Analysis Summary:

Fundamental Assessment: {results.get('fundamental', 'N/A')[:500] if results.get('fundamental') else 'N/A'}

Technical Assessment: The stock shows {tech_metrics.get('trend_direction', 'mixed')} trend with RSI at {tech_metrics.get('rsi', 'N/A')}.

Debate Verdict: {results.get('debate_verdict', 'N/A')[:500] if results.get('debate_verdict') else 'N/A'}
"""

        # Create StockReportData with AUTHORITATIVE values from raw_data
        report_data = StockReportData(
            # Use RAW DATA for all numerical values (AUTHORITATIVE)
            symbol=raw_data.get("symbol", f"{stock_symbol}.NS"),
            company_name=raw_data.get("company_name", stock_symbol),
            current_price=raw_data.get("current_price") or 0,
            week_52_high=raw_data.get("week_52_high"),
            week_52_low=raw_data.get("week_52_low"),
            day_change=raw_data.get("day_change"),
            day_change_percent=raw_data.get("day_change_percent"),

            # Fundamental metrics from RAW DATA
            pe_ratio=raw_data.get("pe_ratio"),
            pb_ratio=raw_data.get("pb_ratio"),
            market_cap=raw_data.get("market_cap"),
            roe=raw_data.get("roe"),
            debt_to_equity=raw_data.get("debt_to_equity"),
            dividend_yield=raw_data.get("dividend_yield"),

            # Technical metrics (extracted from analysis text)
            rsi=tech_metrics.get("rsi"),
            macd_signal=tech_metrics.get("macd_signal"),
            trend_direction=tech_metrics.get("trend_direction"),
            support_level=tech_metrics.get("support_level"),
            resistance_level=tech_metrics.get("resistance_level"),

            # Risk metrics (extracted and validated)
            target_price=risk_metrics.get("target_price"),
            stop_loss=risk_metrics.get("stop_loss"),
            investment_horizon=risk_metrics.get("investment_horizon"),

            # Recommendation (from debate)
            recommendation=recommendation,
            confidence_score=confidence,

            # Analysis content
            positive_factors=positive_factors,
            risk_factors=risk_factors,
            detailed_analysis=detailed_analysis,
        )

        # Generate PDF directly
        pdf_path = generate_stock_report(report_data)
        print(f"[OK] PDF Report generated: {pdf_path}")

        # Log what data was used
        print(f"     [DATA USED] Price: {raw_data.get('current_price')}, 52W High: {raw_data.get('week_52_high')}, 52W Low: {raw_data.get('week_52_low')}")
        print(f"     [DATA USED] ROE: {raw_data.get('roe')}, Dividend: {raw_data.get('dividend_yield')}")
        print(f"     [EXTRACTED] Stop Loss: {risk_metrics.get('stop_loss')}, Target: {risk_metrics.get('target_price')}")

        return formatted_report + f"\n\nPDF Report generated: {pdf_path}\nRecommendation: {recommendation} (Confidence: {confidence}%)"

    except Exception as e:
        import traceback
        print(f"[ERROR] PDF generation failed: {e}")
        traceback.print_exc()
        return formatted_report + f"\n\n[PDF Generation Error: {e}]"
