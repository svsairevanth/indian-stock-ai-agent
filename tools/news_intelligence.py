"""
News Intelligence System - Advanced news analysis for stock decisions.

This module provides:
1. Multi-source news aggregation (Economic Times, Moneycontrol, Livemint, BSE/NSE)
2. Event detection (earnings, M&A, management changes, regulatory)
3. Impact scoring (how much will this news affect the stock?)
4. Freshness weighting (recent news matters more)
5. Comprehensive sentiment analysis

Author: Indian Stock Analyst AI
"""

import json
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
import yfinance as yf
from bs4 import BeautifulSoup
from openai_sdk import function_tool


# ============== CONFIGURATION ==============

# News source RSS feeds
NEWS_SOURCES = {
    "economic_times": {
        "name": "Economic Times",
        "base_url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "markets_url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "credibility": 0.9,
    },
    "moneycontrol": {
        "name": "Moneycontrol",
        "search_url": "https://www.moneycontrol.com/rss/MCtopnews.xml",
        "markets_url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "credibility": 0.85,
    },
    "livemint": {
        "name": "Livemint",
        "markets_url": "https://www.livemint.com/rss/markets",
        "companies_url": "https://www.livemint.com/rss/companies",
        "credibility": 0.85,
    },
    "business_standard": {
        "name": "Business Standard",
        "markets_url": "https://www.business-standard.com/rss/markets-106.rss",
        "companies_url": "https://www.business-standard.com/rss/companies-101.rss",
        "credibility": 0.85,
    },
}

# Event detection patterns
EVENT_PATTERNS = {
    "EARNINGS": {
        "keywords": ["quarterly results", "Q1", "Q2", "Q3", "Q4", "profit", "revenue",
                     "EPS", "net income", "operating income", "EBITDA", "earnings"],
        "impact_score": 9,
        "description": "Earnings announcement or results"
    },
    "M&A": {
        "keywords": ["acquisition", "merger", "buyout", "takeover", "acquires", "buys",
                     "deal", "transaction", "stake", "demerger", "spin-off"],
        "impact_score": 10,
        "description": "Mergers, acquisitions, or corporate restructuring"
    },
    "MANAGEMENT": {
        "keywords": ["CEO", "CFO", "MD", "chairman", "director", "resignation",
                     "appointment", "steps down", "joins", "leadership"],
        "impact_score": 8,
        "description": "Management or leadership changes"
    },
    "REGULATORY": {
        "keywords": ["SEBI", "RBI", "penalty", "fine", "investigation", "probe",
                     "compliance", "violation", "ban", "restriction", "notice"],
        "impact_score": 9,
        "description": "Regulatory action or investigation"
    },
    "CONTRACTS": {
        "keywords": ["contract", "order", "deal", "partnership", "agreement",
                     "MoU", "collaboration", "tie-up", "wins", "bags", "secures"],
        "impact_score": 7,
        "description": "New contracts or partnerships"
    },
    "RATING_CHANGE": {
        "keywords": ["upgrade", "downgrade", "target price", "rating", "buy rating",
                     "sell rating", "hold rating", "outperform", "underperform"],
        "impact_score": 6,
        "description": "Analyst rating or target price change"
    },
    "DIVIDEND": {
        "keywords": ["dividend", "bonus", "stock split", "buyback", "record date",
                     "ex-date", "payout"],
        "impact_score": 5,
        "description": "Dividend or corporate action"
    },
    "EXPANSION": {
        "keywords": ["expansion", "new plant", "capacity", "investment", "capex",
                     "greenfield", "brownfield", "new facility"],
        "impact_score": 6,
        "description": "Business expansion or investment"
    },
    "LEGAL": {
        "keywords": ["lawsuit", "court", "litigation", "arbitration", "dispute",
                     "settlement", "verdict", "judgment"],
        "impact_score": 7,
        "description": "Legal proceedings or disputes"
    },
    "FRAUD_SCANDAL": {
        "keywords": ["fraud", "scam", "scandal", "embezzlement", "misappropriation",
                     "accounting irregularities", "whistleblower"],
        "impact_score": 10,
        "description": "Fraud or scandal - highest impact"
    },
}

# Freshness weights (how much recent news matters)
FRESHNESS_WEIGHTS = {
    "last_6_hours": 1.0,
    "last_24_hours": 0.9,
    "last_3_days": 0.7,
    "last_7_days": 0.4,
    "older": 0.1,
}


# ============== HELPER FUNCTIONS ==============

def _normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to NSE format."""
    symbol = symbol.upper().strip()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = f"{symbol}.NS"
    return symbol


def _get_company_name(symbol: str) -> str:
    """Get company name from symbol."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info.get("longName", symbol.replace(".NS", "").replace(".BO", ""))
    except:
        return symbol.replace(".NS", "").replace(".BO", "")


def _calculate_freshness_weight(pub_date: str) -> float:
    """Calculate freshness weight based on publication date."""
    try:
        # Try parsing various date formats
        for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                dt = datetime.strptime(pub_date[:25], fmt.replace(" %z", ""))
                break
            except:
                continue
        else:
            return 0.5  # Default if parsing fails

        now = datetime.now()
        age = now - dt

        if age < timedelta(hours=6):
            return FRESHNESS_WEIGHTS["last_6_hours"]
        elif age < timedelta(hours=24):
            return FRESHNESS_WEIGHTS["last_24_hours"]
        elif age < timedelta(days=3):
            return FRESHNESS_WEIGHTS["last_3_days"]
        elif age < timedelta(days=7):
            return FRESHNESS_WEIGHTS["last_7_days"]
        else:
            return FRESHNESS_WEIGHTS["older"]
    except:
        return 0.5


def _detect_events(title: str, content: str = "") -> List[Dict]:
    """Detect events in news title and content."""
    text = (title + " " + content).lower()
    detected_events = []

    for event_type, event_info in EVENT_PATTERNS.items():
        for keyword in event_info["keywords"]:
            if keyword.lower() in text:
                detected_events.append({
                    "type": event_type,
                    "keyword_matched": keyword,
                    "impact_score": event_info["impact_score"],
                    "description": event_info["description"]
                })
                break  # Only count each event type once

    return detected_events


def _calculate_impact_score(events: List[Dict], freshness: float, sentiment_score: float) -> float:
    """Calculate overall impact score for a news item."""
    if not events:
        base_impact = 3  # Default low impact for routine news
    else:
        # Take the highest impact event
        base_impact = max(e["impact_score"] for e in events)

    # Adjust by freshness and sentiment intensity
    sentiment_intensity = abs(sentiment_score)

    # Final score: base * freshness * (1 + sentiment_intensity)
    final_score = base_impact * freshness * (1 + sentiment_intensity * 0.5)

    return min(10.0, round(final_score, 2))


def _fetch_rss_news(url: str, source_name: str, max_items: int = 10) -> List[Dict]:
    """Fetch news from RSS feed."""
    news_items = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")

            for item in items[:max_items]:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                pub_date = item.pubDate.text if item.pubDate else ""
                description = item.description.text if item.description else ""

                # Clean description
                if description:
                    description = BeautifulSoup(description, "html.parser").get_text()[:500]

                news_items.append({
                    "title": title,
                    "link": link,
                    "published": pub_date,
                    "description": description,
                    "source": source_name,
                })
    except Exception as e:
        print(f"Error fetching from {source_name}: {e}")

    return news_items


# ============== MAIN TOOLS ==============

@function_tool
def fetch_comprehensive_news(symbol: str, max_per_source: int = 5) -> str:
    """
    Fetch news from multiple Indian financial news sources.

    Aggregates news from:
    - Economic Times (highest credibility for Indian markets)
    - Moneycontrol (popular retail investor source)
    - Livemint (business news)
    - Business Standard (corporate news)
    - Yahoo Finance (global perspective)
    - Google News (broad coverage)

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        max_per_source: Maximum articles per source (default: 5)

    Returns:
        JSON with aggregated news from all sources with metadata.
    """
    symbol = _normalize_symbol(symbol)
    company_name = _get_company_name(symbol)
    all_news = []
    source_stats = {}

    # 1. Fetch from Yahoo Finance
    try:
        stock = yf.Ticker(symbol)
        yf_news = stock.news or []
        yf_items = []

        for item in yf_news[:max_per_source]:
            pub_time = item.get("providerPublishTime")
            pub_date = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M") if pub_time else "N/A"

            yf_items.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "published": pub_date,
                "description": "",
                "source": "Yahoo Finance",
                "credibility": 0.8,
            })

        all_news.extend(yf_items)
        source_stats["Yahoo Finance"] = len(yf_items)
    except Exception as e:
        source_stats["Yahoo Finance"] = f"Error: {e}"

    # 2. Fetch from Google News
    try:
        search_query = f"{company_name} stock NSE"
        encoded_query = quote(search_query)
        google_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

        google_items = _fetch_rss_news(google_url, "Google News", max_per_source)
        for item in google_items:
            item["credibility"] = 0.7

        # Filter to avoid duplicates
        existing_titles = {n["title"].lower() for n in all_news}
        google_items = [n for n in google_items if n["title"].lower() not in existing_titles]

        all_news.extend(google_items)
        source_stats["Google News"] = len(google_items)
    except Exception as e:
        source_stats["Google News"] = f"Error: {e}"

    # 3. Fetch from Economic Times Markets
    try:
        et_items = _fetch_rss_news(
            NEWS_SOURCES["economic_times"]["markets_url"],
            "Economic Times",
            max_per_source
        )
        # Filter for company-related news
        et_filtered = [n for n in et_items if company_name.lower().split()[0] in n["title"].lower()]
        for item in et_filtered:
            item["credibility"] = NEWS_SOURCES["economic_times"]["credibility"]

        all_news.extend(et_filtered)
        source_stats["Economic Times"] = len(et_filtered)
    except Exception as e:
        source_stats["Economic Times"] = f"Error: {e}"

    # 4. Fetch from Moneycontrol
    try:
        mc_items = _fetch_rss_news(
            NEWS_SOURCES["moneycontrol"]["markets_url"],
            "Moneycontrol",
            max_per_source
        )
        mc_filtered = [n for n in mc_items if company_name.lower().split()[0] in n["title"].lower()]
        for item in mc_filtered:
            item["credibility"] = NEWS_SOURCES["moneycontrol"]["credibility"]

        all_news.extend(mc_filtered)
        source_stats["Moneycontrol"] = len(mc_filtered)
    except Exception as e:
        source_stats["Moneycontrol"] = f"Error: {e}"

    # 5. Fetch from Livemint
    try:
        lm_items = _fetch_rss_news(
            NEWS_SOURCES["livemint"]["companies_url"],
            "Livemint",
            max_per_source
        )
        lm_filtered = [n for n in lm_items if company_name.lower().split()[0] in n["title"].lower()]
        for item in lm_filtered:
            item["credibility"] = NEWS_SOURCES["livemint"]["credibility"]

        all_news.extend(lm_filtered)
        source_stats["Livemint"] = len(lm_filtered)
    except Exception as e:
        source_stats["Livemint"] = f"Error: {e}"

    # Sort by publication date (most recent first)
    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)

    result = {
        "symbol": symbol,
        "company_name": company_name,
        "fetch_time": datetime.now().isoformat(),
        "total_articles": len(all_news),
        "source_breakdown": source_stats,
        "news": all_news,
    }

    return json.dumps(result, indent=2)


@function_tool
def analyze_news_with_events(symbol: str, news_json: str) -> str:
    """
    Analyze news with event detection and impact scoring.

    This tool:
    1. Detects events (earnings, M&A, management changes, etc.)
    2. Calculates freshness weight (recent news matters more)
    3. Calculates impact score (how much will this affect the stock?)
    4. Provides actionable insights

    Args:
        symbol: Stock symbol
        news_json: JSON string from fetch_comprehensive_news

    Returns:
        Detailed analysis with events, impact scores, and insights.
    """
    try:
        news_data = json.loads(news_json)
        news_items = news_data.get("news", [])

        if not news_items:
            return json.dumps({
                "symbol": symbol,
                "error": "No news items to analyze",
                "recommendation": "Unable to assess news sentiment"
            })

        analyzed_items = []
        high_impact_news = []
        detected_event_types = set()
        total_sentiment = 0

        for item in news_items:
            title = item.get("title", "")
            description = item.get("description", "")
            pub_date = item.get("published", "")
            credibility = item.get("credibility", 0.7)

            # Detect events
            events = _detect_events(title, description)
            for e in events:
                detected_event_types.add(e["type"])

            # Calculate freshness
            freshness = _calculate_freshness_weight(pub_date)

            # Simple sentiment from title
            positive_words = ["surge", "jump", "rise", "gain", "profit", "growth", "beat",
                           "upgrade", "buy", "bullish", "strong", "record", "high"]
            negative_words = ["fall", "drop", "decline", "loss", "miss", "downgrade",
                           "sell", "bearish", "weak", "low", "crash", "plunge", "fraud"]

            title_lower = title.lower()
            pos_count = sum(1 for w in positive_words if w in title_lower)
            neg_count = sum(1 for w in negative_words if w in title_lower)

            if pos_count > neg_count:
                sentiment = 0.3 + (pos_count * 0.1)
            elif neg_count > pos_count:
                sentiment = -0.3 - (neg_count * 0.1)
            else:
                sentiment = 0

            sentiment = max(-1, min(1, sentiment))
            total_sentiment += sentiment

            # Calculate impact
            impact = _calculate_impact_score(events, freshness, sentiment)

            analyzed_item = {
                "title": title[:150],
                "source": item.get("source", "Unknown"),
                "published": pub_date,
                "events_detected": events,
                "freshness_weight": freshness,
                "sentiment": round(sentiment, 2),
                "impact_score": impact,
                "credibility": credibility,
            }

            analyzed_items.append(analyzed_item)

            # Track high impact news
            if impact >= 7:
                high_impact_news.append({
                    "title": title[:100],
                    "impact_score": impact,
                    "events": [e["type"] for e in events],
                    "sentiment": "Positive" if sentiment > 0.1 else "Negative" if sentiment < -0.1 else "Neutral"
                })

        # Calculate overall metrics
        avg_sentiment = total_sentiment / len(news_items) if news_items else 0
        avg_impact = sum(item["impact_score"] for item in analyzed_items) / len(analyzed_items)

        # Generate insights
        insights = []

        if "EARNINGS" in detected_event_types:
            insights.append("EARNINGS news detected - expect high volatility around results")
        if "M&A" in detected_event_types:
            insights.append("M&A activity detected - potential significant price movement")
        if "FRAUD_SCANDAL" in detected_event_types:
            insights.append("WARNING: Fraud/scandal news detected - high risk")
        if "REGULATORY" in detected_event_types:
            insights.append("Regulatory news detected - monitor for compliance issues")
        if "RATING_CHANGE" in detected_event_types:
            insights.append("Analyst rating change detected - may influence sentiment")

        if avg_sentiment > 0.2:
            insights.append(f"Overall positive news flow (sentiment: {avg_sentiment:.2f})")
        elif avg_sentiment < -0.2:
            insights.append(f"Overall negative news flow (sentiment: {avg_sentiment:.2f})")
        else:
            insights.append(f"Mixed/neutral news flow (sentiment: {avg_sentiment:.2f})")

        if avg_impact > 6:
            insights.append("High impact news cycle - expect price movement")

        result = {
            "symbol": symbol,
            "analysis_time": datetime.now().isoformat(),
            "total_articles_analyzed": len(analyzed_items),
            "overall_metrics": {
                "average_sentiment": round(avg_sentiment, 3),
                "sentiment_label": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral",
                "average_impact_score": round(avg_impact, 2),
                "detected_event_types": list(detected_event_types),
            },
            "high_impact_news": high_impact_news[:5],  # Top 5 high impact
            "insights": insights,
            "detailed_analysis": analyzed_items[:15],  # Top 15 items
            "recommendation": _generate_news_recommendation(avg_sentiment, avg_impact, detected_event_types)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Analysis failed: {str(e)}",
            "symbol": symbol
        })


def _generate_news_recommendation(sentiment: float, impact: float, events: set) -> str:
    """Generate actionable recommendation based on news analysis."""

    # Check for critical events
    if "FRAUD_SCANDAL" in events:
        return "AVOID - Fraud/scandal news detected. Wait for clarity before investing."

    if "REGULATORY" in events and sentiment < 0:
        return "CAUTION - Negative regulatory news. Monitor situation closely."

    # Based on sentiment and impact
    if sentiment > 0.3 and impact > 5:
        return "POSITIVE - Strong positive news flow with high impact. Consider as entry opportunity."
    elif sentiment > 0.1 and impact > 4:
        return "MILDLY POSITIVE - Favorable news coverage. Good for existing positions."
    elif sentiment < -0.3 and impact > 5:
        return "NEGATIVE - Strong negative news flow. Consider reducing exposure or avoiding."
    elif sentiment < -0.1 and impact > 4:
        return "MILDLY NEGATIVE - Concerning news coverage. Exercise caution."
    elif "EARNINGS" in events:
        return "WAIT - Earnings news detected. Wait for market reaction before acting."
    elif "M&A" in events:
        return "MONITOR - M&A news detected. Significant uncertainty - wait for details."
    else:
        return "NEUTRAL - No significant news impact. Focus on fundamentals and technicals."


@function_tool
def get_sector_news(sector: str, max_articles: int = 10) -> str:
    """
    Get news for a specific sector to understand industry trends.

    Args:
        sector: Sector name (IT, Banking, Pharma, Auto, FMCG, Energy, Metals, Realty)
        max_articles: Number of articles to fetch

    Returns:
        Sector-specific news with analysis.
    """
    sector_queries = {
        "IT": "Indian IT sector TCS Infosys Wipro",
        "Banking": "Indian banking sector HDFC ICICI SBI",
        "Pharma": "Indian pharma sector Sun Pharma Cipla",
        "Auto": "Indian auto sector Maruti Tata Motors Mahindra",
        "FMCG": "Indian FMCG sector HUL ITC Nestle",
        "Energy": "Indian energy sector Reliance ONGC",
        "Metals": "Indian metals sector Tata Steel JSW",
        "Realty": "Indian real estate sector DLF Godrej Properties",
    }

    query = sector_queries.get(sector, f"Indian {sector} sector stocks")
    encoded_query = quote(query)

    try:
        # Fetch from Google News
        google_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        news_items = _fetch_rss_news(google_url, "Google News", max_articles)

        # Analyze sentiment
        total_sentiment = 0
        analyzed = []

        for item in news_items:
            events = _detect_events(item["title"], item.get("description", ""))
            freshness = _calculate_freshness_weight(item.get("published", ""))

            # Simple sentiment
            title_lower = item["title"].lower()
            sentiment = 0
            if any(w in title_lower for w in ["growth", "rise", "gain", "strong", "rally"]):
                sentiment = 0.3
            elif any(w in title_lower for w in ["fall", "decline", "weak", "crash", "loss"]):
                sentiment = -0.3

            total_sentiment += sentiment
            analyzed.append({
                "title": item["title"][:120],
                "source": item["source"],
                "sentiment": sentiment,
                "events": [e["type"] for e in events]
            })

        avg_sentiment = total_sentiment / len(news_items) if news_items else 0

        result = {
            "sector": sector,
            "fetch_time": datetime.now().isoformat(),
            "total_articles": len(news_items),
            "sector_sentiment": round(avg_sentiment, 3),
            "sector_outlook": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral",
            "news": analyzed
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch sector news: {str(e)}",
            "sector": sector
        })


@function_tool
def get_market_mood_index(categories: str = "all") -> str:
    """
    Get overall market mood by analyzing news across categories.

    Analyzes news from:
    - General market news
    - Economic news (RBI, GDP, inflation)
    - Global market news
    - FII/DII flow news

    Args:
        categories: "all" or comma-separated (market,economy,global,flows)

    Returns:
        Market mood index with breakdown by category.
    """
    try:
        mood_data = {}

        category_queries = {
            "market": "Indian stock market Nifty Sensex today",
            "economy": "Indian economy RBI inflation GDP",
            "global": "global markets US Fed China impact India",
            "flows": "FII DII India investment flows",
        }

        if categories == "all":
            cats_to_fetch = list(category_queries.keys())
        else:
            cats_to_fetch = [c.strip() for c in categories.split(",")]

        overall_sentiment = 0
        total_count = 0

        for cat in cats_to_fetch:
            if cat not in category_queries:
                continue

            query = category_queries[cat]
            encoded = quote(query)
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

            news = _fetch_rss_news(url, "Google News", 5)

            cat_sentiment = 0
            for item in news:
                title = item["title"].lower()
                if any(w in title for w in ["rally", "rise", "gain", "bullish", "positive"]):
                    cat_sentiment += 0.3
                elif any(w in title for w in ["fall", "crash", "bearish", "negative", "fear"]):
                    cat_sentiment -= 0.3

            avg_cat = cat_sentiment / len(news) if news else 0
            overall_sentiment += avg_cat
            total_count += 1

            mood_data[cat] = {
                "sentiment": round(avg_cat, 3),
                "outlook": "Bullish" if avg_cat > 0.1 else "Bearish" if avg_cat < -0.1 else "Neutral",
                "article_count": len(news),
            }

        overall_mood = overall_sentiment / total_count if total_count else 0

        # Determine market mood level
        if overall_mood > 0.3:
            mood_level = "GREED"
            recommendation = "Market sentiment is very positive. Be cautious of overvaluation."
        elif overall_mood > 0.1:
            mood_level = "OPTIMISTIC"
            recommendation = "Positive market sentiment. Good environment for quality stocks."
        elif overall_mood < -0.3:
            mood_level = "FEAR"
            recommendation = "Market sentiment is very negative. Look for buying opportunities in quality names."
        elif overall_mood < -0.1:
            mood_level = "CAUTIOUS"
            recommendation = "Negative sentiment. Be selective and focus on defensive plays."
        else:
            mood_level = "NEUTRAL"
            recommendation = "Mixed market sentiment. Stick to fundamentals."

        result = {
            "fetch_time": datetime.now().isoformat(),
            "overall_mood_score": round(overall_mood, 3),
            "mood_level": mood_level,
            "category_breakdown": mood_data,
            "recommendation": recommendation,
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to calculate market mood: {str(e)}"
        })
