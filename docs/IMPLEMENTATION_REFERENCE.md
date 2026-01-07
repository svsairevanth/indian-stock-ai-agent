# Implementation Reference: Multi-Agent Architecture, Structured Output & Sentiment Analysis

This document contains all the code patterns, best practices, and implementation details needed to upgrade the Stock Analyst Agent with the three priority improvements.

---

## Table of Contents

1. [Multi-Agent Architecture with Handoffs](#1-multi-agent-architecture-with-handoffs)
2. [Structured Output with Pydantic](#2-structured-output-with-pydantic)
3. [Enhanced Sentiment Analysis](#3-enhanced-sentiment-analysis)
4. [Integration Patterns](#4-integration-patterns)

---

## 1. Multi-Agent Architecture with Handoffs

### 1.1 OpenAI Agents SDK Patterns

The OpenAI Agents SDK supports two main multi-agent patterns:

#### Pattern A: Agents as Tools (Orchestrator Pattern)
```python
from agents import Agent, Runner

# Specialized agents
data_agent = Agent(
    name="Data Agent",
    instructions="You fetch and process stock data"
)

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="You perform technical analysis"
)

# Orchestrator that uses other agents as tools
orchestrator = Agent(
    name="Stock Orchestrator",
    instructions="You coordinate stock analysis tasks",
    tools=[
        data_agent.as_tool(
            tool_name="fetch_stock_data",
            tool_description="Fetch stock data for analysis"
        ),
        analysis_agent.as_tool(
            tool_name="analyze_stock",
            tool_description="Perform technical analysis on stock data"
        )
    ]
)
```

#### Pattern B: Handoffs (Delegation Pattern) - RECOMMENDED
```python
from agents import Agent, handoff

# Specialized agents
fundamental_agent = Agent(
    name="Fundamental Analyst",
    instructions="You analyze company fundamentals: P/E, P/B, ROE, debt levels, growth metrics"
)

technical_agent = Agent(
    name="Technical Analyst",
    instructions="You analyze price action, RSI, MACD, moving averages, support/resistance"
)

sentiment_agent = Agent(
    name="Sentiment Analyst",
    instructions="You analyze news sentiment and market mood"
)

# Main triage agent that hands off to specialists
triage_agent = Agent(
    name="Stock Analyst Triage",
    instructions="""You coordinate stock analysis by delegating to specialists:
    - Hand off fundamental analysis to Fundamental Analyst
    - Hand off technical analysis to Technical Analyst
    - Hand off news/sentiment to Sentiment Analyst
    After all analyses, synthesize into final recommendation.""",
    handoffs=[fundamental_agent, technical_agent, sentiment_agent]
)
```

### 1.2 Handoff with Data Passing
```python
from pydantic import BaseModel
from agents import Agent, handoff, RunContextWrapper

class AnalysisData(BaseModel):
    symbol: str
    analysis_type: str
    priority: str = "normal"

async def on_handoff(ctx: RunContextWrapper, input_data: AnalysisData):
    print(f"Handoff to {input_data.analysis_type} for {input_data.symbol}")

agent = Agent(name="Specialist Agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=AnalysisData,
)
```

### 1.3 Recommended Architecture for Stock Analyst

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                            │
│  "Coordinates analysis and synthesizes final recommendation"    │
│                                                                  │
│  handoffs=[fundamental_agent, technical_agent, sentiment_agent] │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ FUNDAMENTAL   │ │  TECHNICAL    │ │  SENTIMENT    │
│   ANALYST     │ │   ANALYST     │ │   ANALYST     │
│               │ │               │ │               │
│ Tools:        │ │ Tools:        │ │ Tools:        │
│ -get_fundamen │ │ -get_tech_ind │ │ -get_news     │
│ -get_stock_in │ │ -get_support  │ │ -analyze_sent │
│               │ │ -analyze_tren │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
```

### 1.4 Running Multi-Agent System
```python
from agents import Runner

async def analyze_stock(query: str):
    result = await Runner.run(
        starting_agent=orchestrator_agent,
        input=query,
        max_turns=25  # Allow enough turns for handoffs
    )
    return result.final_output
```

---

## 2. Structured Output with Pydantic

### 2.1 Basic Structured Output
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from agents import Agent

class StockRecommendation(BaseModel):
    """Structured output for stock analysis."""
    symbol: str = Field(description="Stock symbol analyzed")
    company_name: str = Field(description="Company name")
    recommendation: Literal["BUY", "SELL", "HOLD"] = Field(
        description="Investment recommendation"
    )
    confidence: float = Field(
        ge=0, le=100,
        description="Confidence score 0-100"
    )
    current_price: float = Field(description="Current stock price in INR")
    target_price: Optional[float] = Field(
        default=None,
        description="Target price if BUY recommendation"
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Recommended stop loss price"
    )
    time_horizon: Literal["Short-term", "Medium-term", "Long-term"] = Field(
        description="Investment time horizon"
    )

    # Scores from different analysis types
    fundamental_score: float = Field(
        ge=0, le=10,
        description="Fundamental analysis score 0-10"
    )
    technical_score: float = Field(
        ge=0, le=10,
        description="Technical analysis score 0-10"
    )
    sentiment_score: float = Field(
        ge=-1, le=1,
        description="News sentiment score -1 to +1"
    )

    # Key factors
    key_positives: List[str] = Field(
        description="Key positive factors supporting recommendation"
    )
    key_risks: List[str] = Field(
        description="Key risk factors to consider"
    )

    summary: str = Field(
        description="Brief summary of the analysis"
    )

# Create agent with structured output
agent = Agent(
    name="Stock Analyst",
    instructions="Analyze stocks and provide recommendations",
    output_type=StockRecommendation,  # Enforces structured output
    tools=[...]
)
```

### 2.2 Nested Structured Output
```python
class FundamentalMetrics(BaseModel):
    pe_ratio: Optional[float] = Field(description="P/E ratio")
    pb_ratio: Optional[float] = Field(description="P/B ratio")
    roe: Optional[float] = Field(description="Return on Equity %")
    debt_to_equity: Optional[float] = Field(description="Debt to Equity ratio")
    revenue_growth: Optional[float] = Field(description="Revenue growth %")
    profit_margin: Optional[float] = Field(description="Profit margin %")

class TechnicalIndicators(BaseModel):
    rsi: float = Field(description="RSI value 0-100")
    rsi_signal: Literal["Oversold", "Neutral", "Overbought"]
    macd_signal: Literal["Bullish", "Bearish", "Neutral"]
    trend: Literal["Uptrend", "Downtrend", "Sideways"]
    support_level: float
    resistance_level: float

class NewsSentiment(BaseModel):
    overall_sentiment: Literal["Positive", "Neutral", "Negative"]
    sentiment_score: float = Field(ge=-1, le=1)
    news_count: int
    key_headlines: List[str]

class ComprehensiveAnalysis(BaseModel):
    """Complete stock analysis with all components."""
    symbol: str
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float

    fundamentals: FundamentalMetrics
    technicals: TechnicalIndicators
    sentiment: NewsSentiment

    bull_case: str = Field(description="Bullish argument for the stock")
    bear_case: str = Field(description="Bearish argument against the stock")

    final_verdict: str
```

### 2.3 Agent with Multiple Output Types
```python
from pydantic_ai import ToolOutput

class QuickAnalysis(BaseModel):
    symbol: str
    recommendation: str
    reason: str

class DetailedAnalysis(BaseModel):
    # ... full analysis fields

agent = Agent(
    'openai:gpt-4o',
    output_type=[
        ToolOutput(QuickAnalysis, name='quick_analysis'),
        ToolOutput(DetailedAnalysis, name='detailed_analysis'),
    ],
)
```

---

## 3. Enhanced Sentiment Analysis

### 3.1 VADER Sentiment (Rule-based, Fast)
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment_vader(text: str) -> dict:
    """
    Analyze sentiment using VADER.
    Returns compound score from -1 (negative) to +1 (positive).
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)

    # scores contains: neg, neu, pos, compound
    return {
        "compound": scores["compound"],  # Overall score -1 to +1
        "positive": scores["pos"],
        "negative": scores["neg"],
        "neutral": scores["neu"],
        "label": get_sentiment_label(scores["compound"])
    }

def get_sentiment_label(compound: float) -> str:
    """Convert compound score to label."""
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"
```

### 3.2 TextBlob Sentiment (Simple, Built-in)
```python
from textblob import TextBlob

def analyze_sentiment_textblob(text: str) -> dict:
    """
    Analyze sentiment using TextBlob.
    Polarity: -1 (negative) to +1 (positive)
    Subjectivity: 0 (objective) to 1 (subjective)
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "label": get_polarity_label(polarity)
    }

def get_polarity_label(polarity: float) -> str:
    if polarity >= 0.1:
        return "Positive"
    elif polarity <= -0.1:
        return "Negative"
    return "Neutral"
```

### 3.3 FinBERT (Best for Financial Text)
```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import numpy as np

class FinBERTSentiment:
    """Financial domain-specific sentiment analysis."""

    def __init__(self):
        self.model = BertForSequenceClassification.from_pretrained(
            'yiyanghkust/finbert-tone',
            num_labels=3
        )
        self.tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
        self.labels = {0: 'neutral', 1: 'positive', 2: 'negative'}

    def analyze(self, texts: list) -> list:
        """Analyze sentiment for a list of texts."""
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        results = []
        for idx, text in enumerate(texts):
            probs = predictions[idx].numpy()
            label_idx = np.argmax(probs)
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "label": self.labels[label_idx],
                "confidence": float(probs[label_idx]),
                "scores": {
                    "neutral": float(probs[0]),
                    "positive": float(probs[1]),
                    "negative": float(probs[2])
                }
            })

        return results

# Usage
finbert = FinBERTSentiment()
results = finbert.analyze([
    "Company reports strong quarterly earnings growth",
    "Stock price plummets amid fraud allegations",
    "Markets remain stable despite global concerns"
])
```

### 3.4 Combined Sentiment Analyzer (Recommended)
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from typing import List, Dict
import statistics

class CombinedSentimentAnalyzer:
    """
    Combines multiple sentiment analysis approaches for more robust results.
    Uses VADER and TextBlob for speed, with optional FinBERT for accuracy.
    """

    def __init__(self, use_finbert: bool = False):
        self.vader = SentimentIntensityAnalyzer()
        self.use_finbert = use_finbert
        if use_finbert:
            from transformers import pipeline
            self.finbert = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert"
            )

    def analyze_text(self, text: str) -> Dict:
        """Analyze a single text."""
        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores["compound"]

        # TextBlob analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity

        # Combine scores (weighted average)
        # VADER is better for social media style, TextBlob for formal text
        combined_score = (vader_compound * 0.6 + textblob_polarity * 0.4)

        # Optional FinBERT for financial texts
        if self.use_finbert:
            try:
                finbert_result = self.finbert(text[:512])[0]
                finbert_score = finbert_result["score"]
                if finbert_result["label"] == "negative":
                    finbert_score = -finbert_score
                elif finbert_result["label"] == "neutral":
                    finbert_score = 0
                # Weight FinBERT higher for financial text
                combined_score = (combined_score * 0.4 + finbert_score * 0.6)
            except:
                pass

        return {
            "score": round(combined_score, 4),
            "label": self._get_label(combined_score),
            "vader_compound": vader_compound,
            "textblob_polarity": textblob_polarity,
        }

    def analyze_news_list(self, news_items: List[Dict]) -> Dict:
        """
        Analyze a list of news items and return aggregate sentiment.

        Args:
            news_items: List of dicts with 'title' and optionally 'summary'

        Returns:
            Aggregate sentiment analysis
        """
        if not news_items:
            return {
                "overall_score": 0,
                "overall_label": "Neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "analyzed_items": []
            }

        scores = []
        analyzed = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for item in news_items:
            text = item.get("title", "")
            if item.get("summary"):
                text += " " + item["summary"]

            result = self.analyze_text(text)
            scores.append(result["score"])

            if result["label"] == "Positive":
                positive_count += 1
            elif result["label"] == "Negative":
                negative_count += 1
            else:
                neutral_count += 1

            analyzed.append({
                "title": item.get("title", "")[:100],
                "score": result["score"],
                "label": result["label"]
            })

        overall_score = statistics.mean(scores) if scores else 0

        return {
            "overall_score": round(overall_score, 4),
            "overall_label": self._get_label(overall_score),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "news_count": len(news_items),
            "analyzed_items": analyzed[:5]  # Top 5 for brevity
        }

    def _get_label(self, score: float) -> str:
        if score >= 0.1:
            return "Positive"
        elif score <= -0.1:
            return "Negative"
        return "Neutral"
```

### 3.5 Integration as Tool
```python
from agents import function_tool
import json

@function_tool
def analyze_news_sentiment(symbol: str, news_data: str) -> str:
    """
    Analyze sentiment of news articles for a stock.

    Args:
        symbol: Stock symbol
        news_data: JSON string of news items with 'title' fields

    Returns:
        Sentiment analysis results with scores and labels.
    """
    try:
        news_items = json.loads(news_data)
        analyzer = CombinedSentimentAnalyzer()
        result = analyzer.analyze_news_list(news_items)

        return json.dumps({
            "symbol": symbol,
            "sentiment_analysis": {
                "overall_score": result["overall_score"],
                "overall_label": result["overall_label"],
                "interpretation": _interpret_sentiment(result["overall_score"]),
                "breakdown": {
                    "positive_news": result["positive_count"],
                    "negative_news": result["negative_count"],
                    "neutral_news": result["neutral_count"],
                },
                "top_headlines_analyzed": result["analyzed_items"]
            }
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})

def _interpret_sentiment(score: float) -> str:
    if score >= 0.3:
        return "Strongly positive sentiment - bullish news flow"
    elif score >= 0.1:
        return "Mildly positive sentiment - favorable news"
    elif score <= -0.3:
        return "Strongly negative sentiment - bearish news flow"
    elif score <= -0.1:
        return "Mildly negative sentiment - concerning news"
    return "Neutral sentiment - mixed or no significant news"
```

---

## 4. Integration Patterns

### 4.1 Complete Multi-Agent Implementation
```python
from agents import Agent, Runner, handoff, function_tool
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ============== STRUCTURED OUTPUT MODELS ==============

class FundamentalAnalysis(BaseModel):
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    fundamental_score: float = Field(ge=0, le=10)
    assessment: str

class TechnicalAnalysis(BaseModel):
    rsi: float
    macd_signal: str
    trend: str
    support: float
    resistance: float
    technical_score: float = Field(ge=0, le=10)
    assessment: str

class SentimentAnalysis(BaseModel):
    overall_score: float = Field(ge=-1, le=1)
    positive_count: int
    negative_count: int
    sentiment_label: str
    assessment: str

class StockRecommendation(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=100)
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    time_horizon: str

    fundamental_analysis: FundamentalAnalysis
    technical_analysis: TechnicalAnalysis
    sentiment_analysis: SentimentAnalysis

    bull_case: str
    bear_case: str
    key_risks: List[str]
    summary: str

# ============== SPECIALIZED AGENTS ==============

fundamental_analyst = Agent(
    name="Fundamental Analyst",
    instructions="""You are an expert fundamental analyst for Indian stocks.

    Your job is to analyze:
    - P/E and P/B ratios (compare to sector averages)
    - ROE and profitability metrics
    - Debt levels and financial health
    - Revenue and earnings growth
    - Dividend yield and payout

    Use the get_fundamentals and get_stock_info tools to gather data.
    Provide a fundamental_score from 0-10 and clear assessment.

    Score Guide:
    - 8-10: Excellent fundamentals, strong buy on this basis
    - 6-8: Good fundamentals, supportive of buy
    - 4-6: Average fundamentals, neutral
    - 2-4: Weak fundamentals, caution advised
    - 0-2: Poor fundamentals, avoid
    """,
    tools=[get_fundamentals, get_stock_info],
)

technical_analyst = Agent(
    name="Technical Analyst",
    instructions="""You are an expert technical analyst for Indian stocks.

    Your job is to analyze:
    - RSI (overbought >70, oversold <30)
    - MACD crossovers and momentum
    - Moving averages (20, 50, 200 SMA)
    - Support and resistance levels
    - Trend direction and strength
    - Bollinger Bands and volatility

    Use the technical analysis tools to gather data.
    Provide a technical_score from 0-10 and clear assessment.

    Score Guide:
    - 8-10: Strong bullish technicals, excellent entry
    - 6-8: Positive technicals, good entry
    - 4-6: Mixed signals, wait for confirmation
    - 2-4: Bearish technicals, avoid entry
    - 0-2: Strong sell signals
    """,
    tools=[get_technical_indicators, get_support_resistance, analyze_trend],
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    instructions="""You are a news and sentiment analyst for Indian stocks.

    Your job is to:
    - Gather recent news about the stock
    - Analyze sentiment of news headlines
    - Identify key positive and negative news
    - Assess overall market mood toward the stock

    Use the news tools and sentiment analyzer.
    Provide sentiment_score from -1 to +1 and assessment.

    Score Guide:
    - 0.3 to 1.0: Strongly positive sentiment
    - 0.1 to 0.3: Mildly positive
    - -0.1 to 0.1: Neutral
    - -0.3 to -0.1: Mildly negative
    - -1.0 to -0.3: Strongly negative
    """,
    tools=[get_stock_news, analyze_news_sentiment],
)

# ============== ORCHESTRATOR AGENT ==============

orchestrator_agent = Agent(
    name="Stock Analysis Orchestrator",
    instructions="""You are the lead stock analyst coordinating a team of specialists.

    When asked to analyze a stock, you MUST:

    1. FIRST, hand off to Fundamental Analyst for fundamental analysis
    2. THEN, hand off to Technical Analyst for technical analysis
    3. THEN, hand off to Sentiment Analyst for news sentiment
    4. FINALLY, synthesize all analyses into a recommendation

    Your synthesis should:
    - Weigh fundamental (40%), technical (35%), and sentiment (25%)
    - Present both bull case and bear case
    - Provide clear BUY/SELL/HOLD recommendation
    - Set realistic target price and stop loss
    - List key risks

    Be objective and data-driven. Never make up numbers.
    Always use the specialists' tools through handoffs.
    """,
    handoffs=[fundamental_analyst, technical_analyst, sentiment_analyst],
    output_type=StockRecommendation,  # Structured output
)

# ============== RUNNER ==============

async def analyze_stock_multiagent(query: str) -> StockRecommendation:
    """Run multi-agent stock analysis."""
    result = await Runner.run(
        starting_agent=orchestrator_agent,
        input=query,
        max_turns=30,  # Allow enough turns for all handoffs
    )
    return result.final_output
```

### 4.2 Requirements Update
```
# requirements.txt additions
vaderSentiment>=3.3.2
textblob>=0.17.1
# Optional for FinBERT (requires more resources):
# transformers>=4.35.0
# torch>=2.0.0
```

### 4.3 Installation Commands
```bash
pip install vaderSentiment textblob
python -m textblob.download_corpora  # Download NLTK data for TextBlob
```

---

## 5. Best Practices Summary

### Do's:
1. **Use handoffs for specialized analysis** - Each agent focuses on one domain
2. **Define Pydantic models** - Ensures consistent, validated output
3. **Combine sentiment methods** - VADER + TextBlob for robustness
4. **Set appropriate max_turns** - Multi-agent needs more turns (25-30)
5. **Use descriptive agent instructions** - Clear role and scoring guidelines
6. **Implement error handling** - Graceful fallbacks in tools

### Don'ts:
1. **Don't overload one agent** - Split responsibilities
2. **Don't skip validation** - Use Pydantic Field constraints
3. **Don't rely on single sentiment method** - Combine for accuracy
4. **Don't hardcode recommendations** - Let agents analyze data
5. **Don't ignore confidence levels** - Include in output

---

## 6. File Structure After Implementation

```
Stock Agent/
├── agent.py                 # Multi-agent orchestrator (UPDATED)
├── agents/                  # NEW: Specialized agents
│   ├── __init__.py
│   ├── fundamental_analyst.py
│   ├── technical_analyst.py
│   └── sentiment_analyst.py
├── models/                  # NEW: Pydantic models
│   ├── __init__.py
│   └── schemas.py           # StockRecommendation, etc.
├── tools/
│   ├── stock_data.py
│   ├── technical_analysis.py
│   ├── news_fetcher.py
│   └── sentiment_analyzer.py  # NEW: Enhanced sentiment
├── config.py
├── pdf_generator.py
├── main.py
└── requirements.txt         # UPDATED with new deps
```

---

This reference document contains all the patterns and code needed to implement the three priority improvements. Ready for implementation!
