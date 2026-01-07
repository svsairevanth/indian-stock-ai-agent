"""
Document Analysis Tools - RAG-based analysis for company filings, annual reports,
and earnings call transcripts. Provides insights from company documents.
"""

import re
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
from agents import function_tool
from bs4 import BeautifulSoup


# Simple in-memory document store for RAG
class DocumentStore:
    """Simple document store for company filings."""

    def __init__(self):
        self.documents = {}  # symbol -> list of documents
        self.chunks = {}  # symbol -> list of text chunks

    def add_document(self, symbol: str, doc_type: str, content: str, metadata: dict = None):
        """Add a document to the store."""
        if symbol not in self.documents:
            self.documents[symbol] = []
            self.chunks[symbol] = []

        doc = {
            "type": doc_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.documents[symbol].append(doc)

        # Create chunks for retrieval
        chunks = self._chunk_text(content, doc_type)
        for chunk in chunks:
            self.chunks[symbol].append({
                "text": chunk,
                "doc_type": doc_type,
                "metadata": metadata,
            })

    def _chunk_text(self, text: str, doc_type: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for better retrieval."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def search(self, symbol: str, query: str, top_k: int = 5) -> List[Dict]:
        """Simple keyword-based search (in production, use embeddings)."""
        if symbol not in self.chunks:
            return []

        query_terms = query.lower().split()
        results = []

        for chunk in self.chunks[symbol]:
            text_lower = chunk["text"].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            if score > 0:
                results.append({
                    "text": chunk["text"],
                    "doc_type": chunk["doc_type"],
                    "score": score,
                })

        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_all_docs(self, symbol: str) -> List[Dict]:
        """Get all documents for a symbol."""
        return self.documents.get(symbol, [])


# Global document store
doc_store = DocumentStore()


@function_tool
def fetch_company_announcements(symbol: str, limit: int = 10) -> str:
    """Fetch recent company announcements and filings from BSE/NSE.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        limit: Maximum number of announcements to fetch. Default: 10

    Returns:
        Recent company announcements including quarterly results, board meetings, etc.
    """
    try:
        # Clean symbol
        symbol_clean = symbol.upper().strip().replace(".NS", "").replace(".BO", "")

        # Try to fetch from BSE API (public endpoint)
        # Note: In production, you'd use official BSE/NSE APIs
        announcements = []

        # Simulated announcement structure (in production, scrape from BSE/NSE)
        # This would be replaced with actual API calls

        # Try Yahoo Finance news as a proxy for announcements
        import yfinance as yf
        symbol_yf = f"{symbol_clean}.NS"
        stock = yf.Ticker(symbol_yf)

        # Get stock info for company name
        info = stock.info
        company_name = info.get("longName", symbol_clean)

        # Get news (includes announcements)
        try:
            news = stock.news
            for item in news[:limit]:
                announcements.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "publish_time": datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ).strftime("%Y-%m-%d %H:%M") if item.get("providerPublishTime") else "Unknown",
                    "type": _categorize_announcement(item.get("title", "")),
                })
        except:
            pass

        # Add to document store for RAG
        for ann in announcements:
            doc_store.add_document(
                symbol_clean,
                "announcement",
                f"{ann['title']}\n{ann.get('summary', '')}",
                {"source": ann.get("publisher"), "date": ann.get("publish_time")}
            )

        result = {
            "symbol": symbol_clean,
            "company_name": company_name,
            "announcements": announcements,
            "note": "For detailed filings, check BSE (bseindia.com) or NSE (nseindia.com) directly",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error fetching announcements: {str(e)}"})


def _categorize_announcement(title: str) -> str:
    """Categorize announcement type based on title."""
    title_lower = title.lower()

    if "result" in title_lower or "earnings" in title_lower or "quarter" in title_lower:
        return "Quarterly Results"
    elif "dividend" in title_lower:
        return "Dividend"
    elif "board" in title_lower or "meeting" in title_lower:
        return "Board Meeting"
    elif "acquisition" in title_lower or "merger" in title_lower:
        return "M&A"
    elif "rating" in title_lower or "upgrade" in title_lower or "downgrade" in title_lower:
        return "Rating Action"
    elif "buy" in title_lower or "sell" in title_lower or "target" in title_lower:
        return "Analyst Action"
    else:
        return "Corporate Announcement"


@function_tool
def analyze_quarterly_results(symbol: str, quarter: str = "latest") -> str:
    """Analyze quarterly financial results for a company.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        quarter: Quarter to analyze - 'latest', 'Q1', 'Q2', 'Q3', 'Q4'. Default: latest

    Returns:
        Analysis of quarterly results including revenue, profit, margins, and YoY comparison.
    """
    try:
        import yfinance as yf

        symbol_clean = symbol.upper().strip().replace(".NS", "").replace(".BO", "")
        symbol_yf = f"{symbol_clean}.NS"
        stock = yf.Ticker(symbol_yf)

        # Get financial data
        info = stock.info
        company_name = info.get("longName", symbol_clean)

        # Get quarterly financials
        quarterly_financials = stock.quarterly_financials
        quarterly_income = stock.quarterly_income_stmt

        if quarterly_financials.empty and quarterly_income.empty:
            return json.dumps({
                "symbol": symbol_clean,
                "error": "Quarterly data not available. Check BSE/NSE for detailed results."
            })

        # Get most recent quarter data
        results = {}

        if not quarterly_income.empty:
            latest_quarter = quarterly_income.columns[0]
            prev_quarter = quarterly_income.columns[1] if len(quarterly_income.columns) > 1 else None
            prev_year_quarter = quarterly_income.columns[4] if len(quarterly_income.columns) > 4 else None

            def safe_get(df, row, col):
                try:
                    val = df.loc[row, col]
                    return float(val) if val and not pd.isna(val) else None
                except:
                    return None

            import pandas as pd

            # Revenue
            revenue = safe_get(quarterly_income, "Total Revenue", latest_quarter)
            revenue_prev = safe_get(quarterly_income, "Total Revenue", prev_year_quarter) if prev_year_quarter else None

            # Net Income
            net_income = safe_get(quarterly_income, "Net Income", latest_quarter)
            net_income_prev = safe_get(quarterly_income, "Net Income", prev_year_quarter) if prev_year_quarter else None

            # Operating Income
            operating_income = safe_get(quarterly_income, "Operating Income", latest_quarter)

            # EBITDA
            ebitda = safe_get(quarterly_income, "EBITDA", latest_quarter)

            # Calculate growth rates
            revenue_growth = ((revenue - revenue_prev) / revenue_prev * 100) if revenue and revenue_prev else None
            profit_growth = ((net_income - net_income_prev) / abs(net_income_prev) * 100) if net_income and net_income_prev and net_income_prev != 0 else None

            # Margins
            net_margin = (net_income / revenue * 100) if net_income and revenue else None
            operating_margin = (operating_income / revenue * 100) if operating_income and revenue else None

            results = {
                "quarter_ending": latest_quarter.strftime("%Y-%m-%d") if hasattr(latest_quarter, 'strftime') else str(latest_quarter),
                "financials": {
                    "revenue_cr": round(revenue / 10000000, 2) if revenue else None,  # Convert to Crores
                    "net_income_cr": round(net_income / 10000000, 2) if net_income else None,
                    "operating_income_cr": round(operating_income / 10000000, 2) if operating_income else None,
                    "ebitda_cr": round(ebitda / 10000000, 2) if ebitda else None,
                },
                "growth": {
                    "revenue_growth_yoy": round(revenue_growth, 2) if revenue_growth else None,
                    "profit_growth_yoy": round(profit_growth, 2) if profit_growth else None,
                },
                "margins": {
                    "net_margin_percent": round(net_margin, 2) if net_margin else None,
                    "operating_margin_percent": round(operating_margin, 2) if operating_margin else None,
                },
            }

        # Quality assessment
        quality_score = _assess_results_quality(results)

        # Add analysis to document store
        analysis_text = f"""
        Quarterly Results Analysis for {company_name}:
        Revenue: {results.get('financials', {}).get('revenue_cr')} Cr
        Net Profit: {results.get('financials', {}).get('net_income_cr')} Cr
        Revenue Growth YoY: {results.get('growth', {}).get('revenue_growth_yoy')}%
        Profit Growth YoY: {results.get('growth', {}).get('profit_growth_yoy')}%
        Net Margin: {results.get('margins', {}).get('net_margin_percent')}%
        """
        doc_store.add_document(symbol_clean, "quarterly_results", analysis_text)

        output = {
            "symbol": symbol_clean,
            "company_name": company_name,
            "results": results,
            "quality_assessment": quality_score,
            "note": "All figures in INR Crores. For detailed breakdown, refer to official filings.",
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error analyzing quarterly results: {str(e)}"})


def _assess_results_quality(results: dict) -> dict:
    """Assess quality of quarterly results."""
    score = 5  # Start neutral
    factors = []

    growth = results.get("growth", {})
    margins = results.get("margins", {})

    # Revenue growth
    rev_growth = growth.get("revenue_growth_yoy")
    if rev_growth:
        if rev_growth > 20:
            score += 2
            factors.append("Strong revenue growth")
        elif rev_growth > 10:
            score += 1
            factors.append("Good revenue growth")
        elif rev_growth < 0:
            score -= 2
            factors.append("Revenue decline")

    # Profit growth
    profit_growth = growth.get("profit_growth_yoy")
    if profit_growth:
        if profit_growth > 25:
            score += 2
            factors.append("Strong profit growth")
        elif profit_growth > 10:
            score += 1
            factors.append("Good profit growth")
        elif profit_growth < 0:
            score -= 2
            factors.append("Profit decline")

    # Margins
    net_margin = margins.get("net_margin_percent")
    if net_margin:
        if net_margin > 15:
            score += 1
            factors.append("Healthy margins")
        elif net_margin < 5:
            score -= 1
            factors.append("Low margins")

    score = max(0, min(10, score))

    return {
        "score": score,
        "rating": "excellent" if score >= 8 else (
            "good" if score >= 6 else (
                "average" if score >= 4 else "poor"
            )
        ),
        "factors": factors,
    }


@function_tool
def search_company_documents(symbol: str, query: str) -> str:
    """Search through stored company documents using RAG-style retrieval.

    Args:
        symbol: Stock symbol
        query: Search query (e.g., "dividend policy", "expansion plans", "debt levels")

    Returns:
        Relevant document snippets related to the query.
    """
    try:
        symbol_clean = symbol.upper().strip().replace(".NS", "").replace(".BO", "")

        # Search document store
        results = doc_store.search(symbol_clean, query, top_k=5)

        if not results:
            return json.dumps({
                "symbol": symbol_clean,
                "query": query,
                "results": [],
                "note": "No relevant documents found. Try fetching announcements or quarterly results first.",
            })

        output = {
            "symbol": symbol_clean,
            "query": query,
            "results": [
                {
                    "snippet": r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"],
                    "doc_type": r["doc_type"],
                    "relevance_score": r["score"],
                }
                for r in results
            ],
            "total_matches": len(results),
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error searching documents: {str(e)}"})


@function_tool
def get_management_commentary(symbol: str) -> str:
    """Extract and analyze management commentary from recent filings.

    Args:
        symbol: Stock symbol

    Returns:
        Key management commentary points and forward-looking statements.
    """
    try:
        import yfinance as yf

        symbol_clean = symbol.upper().strip().replace(".NS", "").replace(".BO", "")
        symbol_yf = f"{symbol_clean}.NS"
        stock = yf.Ticker(symbol_yf)

        info = stock.info
        company_name = info.get("longName", symbol_clean)

        # Get analyst recommendations as proxy for management sentiment
        recommendations = {}
        try:
            rec = stock.recommendations
            if rec is not None and not rec.empty:
                recent_rec = rec.tail(10)
                recommendations = {
                    "total_analysts": len(recent_rec),
                    "strong_buy": int((recent_rec['strongBuy'] if 'strongBuy' in recent_rec else recent_rec.get('To Grade', '') == 'Buy').sum()),
                    "buy": int((recent_rec['buy'] if 'buy' in recent_rec else 0)),
                    "hold": int((recent_rec['hold'] if 'hold' in recent_rec else 0)),
                    "sell": int((recent_rec['sell'] if 'sell' in recent_rec else 0)),
                }
        except:
            pass

        # Get institutional holders as proxy for confidence
        institutional = {}
        try:
            holders = stock.institutional_holders
            if holders is not None and not holders.empty:
                institutional = {
                    "top_holders": holders.head(5).to_dict('records') if not holders.empty else [],
                }
        except:
            pass

        # Business summary as management description
        business_summary = info.get("longBusinessSummary", "")

        # Key metrics that indicate management focus
        metrics = {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "employees": info.get("fullTimeEmployees"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
        }

        # Infer management themes from data
        themes = []
        if metrics.get("revenue_growth") and metrics["revenue_growth"] > 0.15:
            themes.append("Growth-focused strategy")
        if metrics.get("employees") and metrics["employees"] > 100000:
            themes.append("Large-scale operations")

        dividend_yield = info.get("dividendYield")
        if dividend_yield and dividend_yield > 0.02:
            themes.append("Shareholder returns priority")

        # Add to document store
        doc_store.add_document(
            symbol_clean,
            "management_profile",
            f"Business: {business_summary}\nSector: {metrics.get('sector')}\nEmployees: {metrics.get('employees')}",
        )

        output = {
            "symbol": symbol_clean,
            "company_name": company_name,
            "business_summary": business_summary[:500] + "..." if len(business_summary) > 500 else business_summary,
            "key_metrics": metrics,
            "inferred_themes": themes,
            "analyst_sentiment": recommendations,
            "institutional_interest": institutional,
            "note": "For actual management commentary, refer to earnings call transcripts on BSE/NSE",
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting management commentary: {str(e)}"})


@function_tool
def get_peer_comparison(symbol: str) -> str:
    """Get peer comparison data for a company.

    Args:
        symbol: Stock symbol

    Returns:
        Comparison with industry peers on key metrics.
    """
    try:
        import yfinance as yf

        symbol_clean = symbol.upper().strip().replace(".NS", "").replace(".BO", "")
        symbol_yf = f"{symbol_clean}.NS"
        stock = yf.Ticker(symbol_yf)

        info = stock.info
        sector = info.get("sector", "Unknown")
        industry = info.get("industry", "Unknown")

        # Define peer groups by sector (Indian stocks)
        peer_groups = {
            "Technology": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
            "Financial Services": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN"],
            "Energy": ["RELIANCE", "ONGC", "IOC", "BPCL", "GAIL"],
            "Consumer Defensive": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"],
            "Healthcare": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON"],
            "Industrials": ["LT", "SIEMENS", "ABB", "HAVELLS", "BHEL"],
            "Basic Materials": ["TATASTEEL", "HINDALCO", "JSWSTEEL", "VEDL", "COALINDIA"],
            "Consumer Cyclical": ["TITAN", "MARUTI", "BAJAJ-AUTO", "TVSMOTOR", "EICHERMOT"],
        }

        # Find peers
        peers = peer_groups.get(sector, [])

        # Remove the target stock from peers
        peers = [p for p in peers if p != symbol_clean][:4]

        if not peers:
            return json.dumps({
                "symbol": symbol_clean,
                "error": f"No predefined peers for sector: {sector}"
            })

        # Fetch comparison data
        comparison = []
        target_data = _get_comparison_metrics(symbol_yf)
        target_data["symbol"] = symbol_clean
        target_data["is_target"] = True
        comparison.append(target_data)

        for peer in peers:
            try:
                peer_yf = f"{peer}.NS"
                peer_data = _get_comparison_metrics(peer_yf)
                peer_data["symbol"] = peer
                peer_data["is_target"] = False
                comparison.append(peer_data)
            except:
                continue

        # Calculate rankings
        metrics_to_rank = ["pe_ratio", "pb_ratio", "roe", "revenue_growth", "profit_margin"]

        for metric in metrics_to_rank:
            values = [(c["symbol"], c.get(metric)) for c in comparison if c.get(metric) is not None]
            if values:
                # Sort (lower is better for PE/PB, higher is better for ROE/growth/margin)
                reverse = metric in ["roe", "revenue_growth", "profit_margin"]
                sorted_values = sorted(values, key=lambda x: x[1], reverse=reverse)
                rankings = {v[0]: i+1 for i, v in enumerate(sorted_values)}

                for c in comparison:
                    c[f"{metric}_rank"] = rankings.get(c["symbol"])

        # IMPORTANT: Peer groups are static reference mappings
        DATA_VERSION = "2024-12-06"

        output = {
            "symbol": symbol_clean,
            "sector": sector,
            "industry": industry,
            "peers": peers,
            "comparison": comparison,
            "interpretation": _interpret_peer_comparison(comparison, symbol_clean),
            "disclaimer": {
                "warning": "STATIC PEER MAPPINGS - May become outdated",
                "message": "Peer groups are hardcoded reference lists. Industry composition changes over time.",
                "recommendation": "For authoritative peer lists, consult Screener.in, Moneycontrol, or NSE sector indices.",
                "data_version": DATA_VERSION,
            },
        }

        return json.dumps(output, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting peer comparison: {str(e)}"})


def _get_comparison_metrics(symbol: str) -> dict:
    """Get key metrics for peer comparison."""
    import yfinance as yf

    stock = yf.Ticker(symbol)
    info = stock.info

    return {
        "name": info.get("shortName", symbol),
        "market_cap_cr": round(info.get("marketCap", 0) / 10000000, 0) if info.get("marketCap") else None,
        "pe_ratio": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
        "pb_ratio": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else None,
        "roe": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
        "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
        "profit_margin": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
        "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
    }


def _interpret_peer_comparison(comparison: list, target: str) -> dict:
    """Interpret peer comparison results."""
    target_data = next((c for c in comparison if c["symbol"] == target), None)

    if not target_data:
        return {"error": "Target not found"}

    strengths = []
    weaknesses = []
    num_peers = len(comparison)

    # Check rankings
    if target_data.get("pe_ratio_rank") == 1:
        strengths.append("Most attractively valued (lowest P/E)")
    elif target_data.get("pe_ratio_rank") == num_peers:
        weaknesses.append("Most expensive (highest P/E)")

    if target_data.get("roe_rank") == 1:
        strengths.append("Best return on equity")
    elif target_data.get("roe_rank") == num_peers:
        weaknesses.append("Lowest return on equity")

    if target_data.get("revenue_growth_rank") == 1:
        strengths.append("Fastest revenue growth")
    elif target_data.get("revenue_growth_rank") == num_peers:
        weaknesses.append("Slowest revenue growth")

    return {
        "relative_strengths": strengths if strengths else ["No standout strengths vs peers"],
        "relative_weaknesses": weaknesses if weaknesses else ["No significant weaknesses vs peers"],
        "overall": "outperformer" if len(strengths) > len(weaknesses) else (
            "underperformer" if len(weaknesses) > len(strengths) else "in-line with peers"
        ),
    }
