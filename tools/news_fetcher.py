"""
News Fetcher Tools - Functions to fetch stock-related and market news
for Indian stocks using yfinance and web scraping.
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from agents import function_tool
from datetime import datetime
import json


def _normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to include exchange suffix."""
    symbol = symbol.upper().strip()
    if symbol.endswith(".NS") or symbol.endswith(".BO") or symbol.startswith("^"):
        return symbol
    return f"{symbol}.NS"


def _get_company_name(symbol: str) -> str:
    """Get company name from symbol for better news search."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info.get("longName", symbol.replace(".NS", "").replace(".BO", ""))
    except:
        return symbol.replace(".NS", "").replace(".BO", "")


@function_tool
def get_stock_news(symbol: str, num_articles: int = 10) -> str:
    """Get recent news articles related to a specific stock from multiple sources.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS). Will auto-add .NS suffix.
        num_articles: Number of news articles to fetch (max 15). Default: 10

    Returns:
        List of recent news articles with titles, sources, and links.
    """
    try:
        symbol = _normalize_symbol(symbol)
        num_articles = min(num_articles, 15)

        all_news = []

        # 1. Get news from yfinance
        try:
            stock = yf.Ticker(symbol)
            yf_news = stock.news or []

            for item in yf_news[:num_articles]:
                published_time = item.get("providerPublishTime")
                if published_time:
                    published_date = datetime.fromtimestamp(published_time).strftime("%Y-%m-%d %H:%M")
                else:
                    published_date = "N/A"

                all_news.append({
                    "title": item.get("title", "No title"),
                    "publisher": item.get("publisher", "Unknown"),
                    "link": item.get("link", ""),
                    "published": published_date,
                    "source": "Yahoo Finance",
                    "type": item.get("type", "news"),
                })
        except Exception as e:
            print(f"yfinance news error: {e}")

        # 2. Get news from Google News RSS
        try:
            company_name = _get_company_name(symbol)
            search_query = f"{company_name} stock NSE"
            encoded_query = quote(search_query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

            response = requests.get(rss_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")

                for item in items[:num_articles - len(all_news)]:
                    title = item.title.text if item.title else "No title"
                    link = item.link.text if item.link else ""
                    pub_date = item.pubDate.text if item.pubDate else "N/A"
                    source = item.source.text if item.source else "Google News"

                    # Avoid duplicates
                    if not any(n["title"] == title for n in all_news):
                        all_news.append({
                            "title": title,
                            "publisher": source,
                            "link": link,
                            "published": pub_date,
                            "source": "Google News",
                            "type": "news",
                        })
        except Exception as e:
            print(f"Google News error: {e}")

        if not all_news:
            return json.dumps({
                "symbol": symbol,
                "message": "No news articles found for this stock",
                "news": []
            })

        result = {
            "symbol": symbol,
            "company_name": _get_company_name(symbol),
            "fetch_time": datetime.now().isoformat(),
            "total_articles": len(all_news),
            "news": all_news[:num_articles],
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error fetching news for {symbol}: {str(e)}",
            "symbol": symbol
        })


@function_tool
def get_market_news(category: str = "general", num_articles: int = 10) -> str:
    """Get general Indian stock market news and updates.

    Args:
        category: News category - general, nifty, sensex, economy, ipo, earnings. Default: general
        num_articles: Number of news articles to fetch (max 15). Default: 10

    Returns:
        List of market news articles with titles, sources, and links.
    """
    try:
        num_articles = min(num_articles, 15)

        # Define search queries based on category
        search_queries = {
            "general": "Indian stock market news NSE BSE",
            "nifty": "Nifty 50 index news today",
            "sensex": "Sensex BSE news today",
            "economy": "Indian economy news RBI",
            "ipo": "IPO India 2026 listing",
            "earnings": "quarterly results India companies earnings",
        }

        query = search_queries.get(category.lower(), search_queries["general"])
        encoded_query = quote(query)

        all_news = []

        # Get news from Google News RSS
        try:
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

            response = requests.get(rss_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "xml")
                items = soup.find_all("item")

                for item in items[:num_articles]:
                    title = item.title.text if item.title else "No title"
                    link = item.link.text if item.link else ""
                    pub_date = item.pubDate.text if item.pubDate else "N/A"
                    source = item.source.text if item.source else "News"

                    all_news.append({
                        "title": title,
                        "publisher": source,
                        "link": link,
                        "published": pub_date,
                        "source": "Google News",
                    })
        except Exception as e:
            print(f"Google News error: {e}")

        # Also try to get index news from yfinance
        if category.lower() in ["nifty", "general"]:
            try:
                nifty = yf.Ticker("^NSEI")
                nifty_news = nifty.news or []
                for item in nifty_news[:3]:
                    published_time = item.get("providerPublishTime")
                    if published_time:
                        published_date = datetime.fromtimestamp(published_time).strftime("%Y-%m-%d %H:%M")
                    else:
                        published_date = "N/A"

                    title = item.get("title", "No title")
                    if not any(n["title"] == title for n in all_news):
                        all_news.append({
                            "title": title,
                            "publisher": item.get("publisher", "Yahoo Finance"),
                            "link": item.get("link", ""),
                            "published": published_date,
                            "source": "Yahoo Finance",
                        })
            except:
                pass

        if not all_news:
            return json.dumps({
                "category": category,
                "message": "No market news found",
                "news": []
            })

        result = {
            "category": category,
            "fetch_time": datetime.now().isoformat(),
            "total_articles": len(all_news),
            "news": all_news[:num_articles],
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error fetching market news: {str(e)}",
            "category": category
        })
