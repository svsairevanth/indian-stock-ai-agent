"""
PDF Report Generator - Creates professional stock analysis reports in PDF format.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pydantic import BaseModel, Field
from typing import Optional, List
from config import PDF_OUTPUT_DIR


class StockReportData(BaseModel):
    """Data model for stock analysis report."""
    symbol: str
    company_name: str
    current_price: float
    recommendation: str = Field(description="BUY, SELL, or HOLD")
    confidence_score: float = Field(ge=0, le=100, description="Confidence percentage")
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

    # Price Information
    day_change: Optional[float] = None
    day_change_percent: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None

    # Fundamental Data
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None

    # Technical Data
    rsi: Optional[float] = None
    macd_signal: Optional[str] = None
    trend_direction: Optional[str] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

    # Analysis
    fundamental_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    news_summary: Optional[str] = None
    risk_factors: Optional[List[str]] = None
    positive_factors: Optional[List[str]] = None

    # Final
    detailed_analysis: str
    investment_horizon: Optional[str] = None


def _format_number(value, prefix="", suffix="", decimals=2):
    """Format number with prefix/suffix, handling None."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) >= 1e9:
            return f"{prefix}{value/1e9:.2f}B{suffix}"
        elif abs(value) >= 1e7:
            return f"{prefix}{value/1e7:.2f}Cr{suffix}"
        elif abs(value) >= 1e5:
            return f"{prefix}{value/1e5:.2f}L{suffix}"
        else:
            return f"{prefix}{value:.{decimals}f}{suffix}"
    return str(value)


def _get_recommendation_color(recommendation: str) -> colors.Color:
    """Get color based on recommendation."""
    rec = recommendation.upper()
    if rec == "BUY":
        return colors.Color(0.13, 0.55, 0.13)  # Green
    elif rec == "SELL":
        return colors.Color(0.86, 0.08, 0.24)  # Red
    else:  # HOLD
        return colors.Color(1.0, 0.65, 0.0)  # Orange


def generate_stock_report(data: StockReportData) -> str:
    """
    Generate a professional PDF stock analysis report.

    Args:
        data: StockReportData containing all analysis information.

    Returns:
        Path to the generated PDF file.
    """
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data.symbol.replace('.', '_')}_{data.recommendation}_{timestamp}.pdf"
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)

    # Create document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a2e')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.gray,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#16213e')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY
    )

    recommendation_style = ParagraphStyle(
        'Recommendation',
        parent=styles['Heading1'],
        fontSize=28,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=10,
    )

    # Build content
    elements = []

    # Header
    elements.append(Paragraph("STOCK ANALYSIS REPORT", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    elements.append(Spacer(1, 20))

    # Company Info Section
    elements.append(Paragraph(f"<b>{data.company_name}</b>", ParagraphStyle(
        'Company', fontSize=20, alignment=TA_CENTER, spaceAfter=5
    )))
    elements.append(Paragraph(f"Symbol: {data.symbol}", ParagraphStyle(
        'Symbol', fontSize=12, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=20
    )))

    # Recommendation Box
    rec_color = _get_recommendation_color(data.recommendation)
    elements.append(Paragraph(
        f"<font color='{rec_color.hexval()}'><b>RECOMMENDATION: {data.recommendation.upper()}</b></font>",
        recommendation_style
    ))
    elements.append(Paragraph(
        f"Confidence: {data.confidence_score:.0f}%",
        ParagraphStyle('Confidence', fontSize=14, alignment=TA_CENTER, spaceAfter=20)
    ))
    elements.append(Spacer(1, 10))

    # Price Summary Table
    price_data = [
        ['Current Price', f"₹{data.current_price:,.2f}"],
        ['Target Price', _format_number(data.target_price, "₹") if data.target_price else "N/A"],
        ['Stop Loss', _format_number(data.stop_loss, "₹") if data.stop_loss else "N/A"],
        ['52-Week High', _format_number(data.week_52_high, "₹")],
        ['52-Week Low', _format_number(data.week_52_low, "₹")],
    ]

    if data.target_price:
        upside = ((data.target_price - data.current_price) / data.current_price) * 100
        price_data.append(['Potential Upside', f"{upside:+.1f}%"])

    price_table = Table(price_data, colWidths=[3*inch, 2.5*inch])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
    ]))
    elements.append(price_table)
    elements.append(Spacer(1, 20))

    # Fundamental Analysis Section
    if any([data.pe_ratio, data.pb_ratio, data.market_cap]):
        elements.append(Paragraph("FUNDAMENTAL ANALYSIS", heading_style))

        fund_data = [
            ['P/E Ratio', _format_number(data.pe_ratio), 'Market Cap', _format_number(data.market_cap, "₹")],
            ['P/B Ratio', _format_number(data.pb_ratio), 'Dividend Yield', _format_number(data.dividend_yield, suffix="%")],
            ['ROE', _format_number(data.roe, suffix="%"), 'Debt/Equity', _format_number(data.debt_to_equity)],
        ]

        fund_table = Table(fund_data, colWidths=[1.5*inch, 1.3*inch, 1.5*inch, 1.3*inch])
        fund_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8f4f8')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(fund_table)

        if data.fundamental_summary:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(data.fundamental_summary, body_style))
        elements.append(Spacer(1, 15))

    # Technical Analysis Section
    if any([data.rsi, data.macd_signal, data.trend_direction]):
        elements.append(Paragraph("TECHNICAL ANALYSIS", heading_style))

        tech_data = [
            ['RSI (14)', _format_number(data.rsi), 'Trend', data.trend_direction or "N/A"],
            ['MACD Signal', data.macd_signal or "N/A", 'Support', _format_number(data.support_level, "₹")],
            ['', '', 'Resistance', _format_number(data.resistance_level, "₹")],
        ]

        tech_table = Table(tech_data, colWidths=[1.5*inch, 1.3*inch, 1.5*inch, 1.3*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#fff3e0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(tech_table)

        if data.technical_summary:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(data.technical_summary, body_style))
        elements.append(Spacer(1, 15))

    # Positive Factors
    if data.positive_factors:
        elements.append(Paragraph("POSITIVE FACTORS", heading_style))
        for factor in data.positive_factors:
            elements.append(Paragraph(f"• {factor}", body_style))
        elements.append(Spacer(1, 10))

    # Risk Factors
    if data.risk_factors:
        elements.append(Paragraph("RISK FACTORS", heading_style))
        for risk in data.risk_factors:
            elements.append(Paragraph(f"• {risk}", body_style))
        elements.append(Spacer(1, 10))

    # News Summary
    if data.news_summary:
        elements.append(Paragraph("NEWS & SENTIMENT", heading_style))
        elements.append(Paragraph(data.news_summary, body_style))
        elements.append(Spacer(1, 15))

    # Detailed Analysis
    elements.append(Paragraph("DETAILED ANALYSIS", heading_style))
    # Split analysis into paragraphs
    analysis_paragraphs = data.detailed_analysis.split('\n\n')
    for para in analysis_paragraphs:
        if para.strip():
            elements.append(Paragraph(para.strip(), body_style))
            elements.append(Spacer(1, 8))

    # Investment Horizon
    if data.investment_horizon:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"<b>Recommended Investment Horizon:</b> {data.investment_horizon}",
            body_style
        ))

    # Footer / Disclaimer
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 10))

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_JUSTIFY
    )

    disclaimer = """
    <b>DISCLAIMER:</b> This report is generated by an AI-powered stock analysis system and is for
    informational purposes only. It does not constitute financial advice, investment recommendation,
    or an offer to buy or sell securities. Stock investments are subject to market risks. Past
    performance is not indicative of future results. Please consult a qualified financial advisor
    before making any investment decisions. The creators of this report are not responsible for
    any financial losses incurred based on this analysis.
    """
    elements.append(Paragraph(disclaimer, disclaimer_style))

    # Build PDF
    doc.build(elements)

    return filepath


# Function tool wrapper for the agent
from agents import function_tool
import json


@function_tool
def create_stock_report(
    symbol: str,
    company_name: str,
    current_price: float,
    recommendation: str,
    confidence_score: float,
    detailed_analysis: str,
    target_price: float = None,
    stop_loss: float = None,
    pe_ratio: float = None,
    pb_ratio: float = None,
    market_cap: float = None,
    rsi: float = None,
    trend_direction: str = None,
    support_level: float = None,
    resistance_level: float = None,
    positive_factors: str = None,
    risk_factors: str = None,
    investment_horizon: str = None,
) -> str:
    """Generate a professional PDF stock analysis report with buy/sell/hold recommendation.

    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS)
        company_name: Full company name
        current_price: Current stock price
        recommendation: Must be BUY, SELL, or HOLD
        confidence_score: Confidence percentage (0-100)
        detailed_analysis: Detailed analysis text explaining the recommendation
        target_price: Target price for the stock (optional)
        stop_loss: Recommended stop loss price (optional)
        pe_ratio: Price to Earnings ratio (optional)
        pb_ratio: Price to Book ratio (optional)
        market_cap: Market capitalization (optional)
        rsi: RSI indicator value (optional)
        trend_direction: Trend direction - uptrend, downtrend, sideways (optional)
        support_level: Key support level (optional)
        resistance_level: Key resistance level (optional)
        positive_factors: Comma-separated list of positive factors (optional)
        risk_factors: Comma-separated list of risk factors (optional)
        investment_horizon: Short-term, Medium-term, or Long-term (optional)

    Returns:
        Path to the generated PDF report file.
    """
    try:
        # Parse comma-separated factors into lists
        pos_factors = [f.strip() for f in positive_factors.split(',')] if positive_factors else None
        risk_factors_list = [f.strip() for f in risk_factors.split(',')] if risk_factors else None

        # Create report data
        report_data = StockReportData(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            recommendation=recommendation.upper(),
            confidence_score=min(max(confidence_score, 0), 100),
            detailed_analysis=detailed_analysis,
            target_price=target_price,
            stop_loss=stop_loss,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            market_cap=market_cap,
            rsi=rsi,
            trend_direction=trend_direction,
            support_level=support_level,
            resistance_level=resistance_level,
            positive_factors=pos_factors,
            risk_factors=risk_factors_list,
            investment_horizon=investment_horizon,
        )

        # Generate PDF
        pdf_path = generate_stock_report(report_data)

        return json.dumps({
            "success": True,
            "message": f"Stock analysis report generated successfully",
            "pdf_path": pdf_path,
            "recommendation": recommendation.upper(),
            "symbol": symbol,
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error generating PDF report: {str(e)}",
            "symbol": symbol,
        })
