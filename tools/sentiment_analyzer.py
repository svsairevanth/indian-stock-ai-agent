"""
Enhanced Sentiment Analysis Tool - Combines multiple sentiment analysis approaches
for robust financial news sentiment scoring.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from agents import function_tool

# Import sentiment analyzers
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not installed. Run: pip install vaderSentiment")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not installed. Run: pip install textblob")


class CombinedSentimentAnalyzer:
    """
    Combines VADER and TextBlob for robust sentiment analysis.
    VADER is optimized for social media/news, TextBlob for general text.
    """

    def __init__(self):
        """Initialize sentiment analyzers."""
        self.vader = None
        if VADER_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores and label
        """
        if not text or not isinstance(text, str):
            return {
                "score": 0.0,
                "label": "Neutral",
                "vader_score": 0.0,
                "textblob_score": 0.0
            }

        scores = []

        # VADER Analysis (better for news/social media)
        vader_score = 0.0
        if self.vader:
            vader_scores = self.vader.polarity_scores(text)
            vader_score = vader_scores["compound"]
            scores.append(vader_score * 0.6)  # 60% weight

        # TextBlob Analysis (better for formal text)
        textblob_score = 0.0
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                textblob_score = blob.sentiment.polarity
                scores.append(textblob_score * 0.4)  # 40% weight
            except Exception:
                pass

        # Calculate combined score
        if scores:
            combined_score = sum(scores)
        else:
            combined_score = 0.0

        # Normalize to -1 to 1 range
        combined_score = max(-1.0, min(1.0, combined_score))

        return {
            "score": round(combined_score, 4),
            "label": self._get_label(combined_score),
            "vader_score": round(vader_score, 4),
            "textblob_score": round(textblob_score, 4)
        }

    def analyze_news_list(self, news_items: List[Dict]) -> Dict:
        """
        Analyze sentiment for a list of news items.

        Args:
            news_items: List of dicts with 'title' and optionally 'summary'

        Returns:
            Aggregate sentiment analysis results
        """
        if not news_items:
            return {
                "overall_score": 0.0,
                "overall_label": "Neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "news_count": 0,
                "key_positive_news": [],
                "key_negative_news": [],
                "analyzed_items": []
            }

        scores = []
        analyzed = []
        positive_news = []
        negative_news = []
        neutral_count = 0

        for item in news_items:
            # Combine title and summary for analysis
            title = item.get("title", "")
            text = title
            if item.get("summary"):
                text += " " + str(item["summary"])

            result = self.analyze_text(text)
            score = result["score"]
            scores.append(score)

            item_result = {
                "title": title[:150],
                "score": score,
                "label": result["label"]
            }
            analyzed.append(item_result)

            # Categorize
            if score >= 0.1:
                positive_news.append(title[:100])
            elif score <= -0.1:
                negative_news.append(title[:100])
            else:
                neutral_count += 1

        # Calculate overall score
        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 0.0

        return {
            "overall_score": round(overall_score, 4),
            "overall_label": self._get_label(overall_score),
            "positive_count": len(positive_news),
            "negative_count": len(negative_news),
            "neutral_count": neutral_count,
            "news_count": len(news_items),
            "key_positive_news": positive_news[:3],  # Top 3
            "key_negative_news": negative_news[:3],  # Top 3
            "analyzed_items": analyzed[:10]  # Top 10
        }

    def _get_label(self, score: float) -> str:
        """Convert score to sentiment label."""
        if score >= 0.25:
            return "Strongly Positive"
        elif score >= 0.1:
            return "Positive"
        elif score <= -0.25:
            return "Strongly Negative"
        elif score <= -0.1:
            return "Negative"
        return "Neutral"


def _interpret_sentiment(score: float) -> str:
    """Get interpretation of sentiment score."""
    if score >= 0.25:
        return "Strongly positive news flow - bullish sentiment in market"
    elif score >= 0.1:
        return "Mildly positive sentiment - favorable news coverage"
    elif score <= -0.25:
        return "Strongly negative news flow - bearish sentiment in market"
    elif score <= -0.1:
        return "Mildly negative sentiment - concerning news coverage"
    return "Neutral sentiment - mixed or no significant news impact"


def _get_sentiment_score_for_recommendation(score: float) -> float:
    """
    Convert sentiment score (-1 to 1) to a 0-10 scale for recommendation.
    """
    # Map -1 to 1 range to 0 to 10
    # -1 -> 0, 0 -> 5, 1 -> 10
    return round((score + 1) * 5, 2)


# Create global analyzer instance
_analyzer = CombinedSentimentAnalyzer()


@function_tool
def analyze_news_sentiment(symbol: str, news_json: str) -> str:
    """
    Analyze sentiment of news articles for a stock using multiple NLP techniques.

    This tool combines VADER (optimized for social media/news) and TextBlob
    (general purpose) sentiment analysis for robust results.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        news_json: JSON string containing list of news items with 'title' fields

    Returns:
        Comprehensive sentiment analysis with scores, labels, and key headlines.
    """
    try:
        # Parse news JSON
        try:
            news_data = json.loads(news_json)
            if isinstance(news_data, dict):
                # Handle case where news is nested in a 'news' key
                news_items = news_data.get("news", [])
            else:
                news_items = news_data
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid JSON format for news data",
                "symbol": symbol
            })

        # Analyze sentiment
        result = _analyzer.analyze_news_list(news_items)

        # Build response
        sentiment_result = {
            "symbol": symbol.upper(),
            "analysis_time": datetime.now().isoformat(),
            "sentiment_summary": {
                "overall_score": result["overall_score"],
                "overall_label": result["overall_label"],
                "interpretation": _interpret_sentiment(result["overall_score"]),
                "recommendation_score": _get_sentiment_score_for_recommendation(result["overall_score"]),
            },
            "news_breakdown": {
                "total_analyzed": result["news_count"],
                "positive_news": result["positive_count"],
                "negative_news": result["negative_count"],
                "neutral_news": result["neutral_count"],
            },
            "key_headlines": {
                "positive": result["key_positive_news"],
                "negative": result["key_negative_news"],
            },
            "detailed_analysis": result["analyzed_items"][:5]  # Top 5 for brevity
        }

        return json.dumps(sentiment_result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Sentiment analysis failed: {str(e)}",
            "symbol": symbol
        })


@function_tool
def get_sentiment_score(text: str) -> str:
    """
    Analyze sentiment of a single piece of text.

    Args:
        text: Text to analyze (headline, summary, etc.)

    Returns:
        Sentiment score and label for the text.
    """
    try:
        result = _analyzer.analyze_text(text)

        return json.dumps({
            "text": text[:200] + "..." if len(text) > 200 else text,
            "sentiment_score": result["score"],
            "sentiment_label": result["label"],
            "vader_score": result["vader_score"],
            "textblob_score": result["textblob_score"],
            "interpretation": _interpret_sentiment(result["score"])
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Sentiment analysis failed: {str(e)}",
            "text": text[:100]
        })


# Export for use in agents
__all__ = [
    "analyze_news_sentiment",
    "get_sentiment_score",
    "CombinedSentimentAnalyzer",
]
