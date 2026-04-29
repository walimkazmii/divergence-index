import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "divergence.db"

TICKER_MAP = {
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Netflix": "NFLX",
    "Meta": "META",
    "Nvidia": "NVDA",
    "Apple Inc": "AAPL",
    "Goldman Sachs": "GS"
}

def get_stock_data(ticker, days=30):
    """Fetch recent stock price data"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days}d")
        if hist.empty:
            return None
        return hist
    except Exception as e:
        print(f"Stock fetch error: {e}")
        return None

def get_ndi_data(company, limit=30):
    """Pull NDI history from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT date, ndi_score, mean_sentiment
        FROM ndi_scores WHERE company = ?
        ORDER BY date DESC LIMIT ?
    ''', (company, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def predict(company):
    """
    Generate a prediction for the next 7 days based on:
    - NDI score trend
    - Mean sentiment trend
    - Recent stock price trajectory
    """
    ticker = TICKER_MAP.get(company)
    if not ticker:
        return {"error": "Company not found"}

    # Get stock data
    stock_data = get_stock_data(ticker, days=30)
    if stock_data is None or len(stock_data) < 5:
        return {"error": "Not enough stock data"}

    # Get NDI history
    ndi_rows = get_ndi_data(company, limit=14)
    if not ndi_rows:
        return {"error": "No NDI data yet — run the pipeline first"}

    # Current stock info
    current_price = round(float(stock_data["Close"].iloc[-1]), 2)
    week_ago_price = round(float(stock_data["Close"].iloc[-5]), 2)
    price_change_7d = round(
        ((current_price - week_ago_price) / week_ago_price) * 100, 2
    )

    # Stock trajectory
    closes = stock_data["Close"].tolist()
    recent_closes = closes[-5:]
    trend_direction = "up" if recent_closes[-1] > recent_closes[0] else "down"
    trend_strength = abs(recent_closes[-1] - recent_closes[0]) / recent_closes[0]

    # NDI signals
    latest_ndi = ndi_rows[0][1]
    latest_sentiment = ndi_rows[0][2]
    avg_ndi = sum(r[1] for r in ndi_rows) / len(ndi_rows)
    avg_sentiment = sum(r[2] for r in ndi_rows) / len(ndi_rows)

    ndi_rising = latest_ndi > avg_ndi
    sentiment_positive = latest_sentiment > 0.05
    sentiment_negative = latest_sentiment < -0.05

    # Build price history for chart
    price_history = []
    for date, close in zip(
        stock_data.index[-14:],
        stock_data["Close"].tolist()[-14:]
    ):
        price_history.append({
            "date": str(date.date()),
            "price": round(float(close), 2)
        })

    # Generate signal
    signal_score = 0

    # Sentiment contribution
    if sentiment_positive:
        signal_score += 1
    elif sentiment_negative:
        signal_score -= 1

    # NDI contribution — high disagreement = uncertainty = caution
    if latest_ndi > 0.25:
        signal_score -= 1
    elif latest_ndi < 0.1:
        signal_score += 0.5

    # Price trend contribution
    if trend_direction == "up" and trend_strength > 0.01:
        signal_score += 1
    elif trend_direction == "down" and trend_strength > 0.01:
        signal_score -= 1

    # Translate score to prediction
    if signal_score >= 1.5:
        prediction = "BULLISH"
        confidence = "high"
        summary = (
            f"Positive sentiment and low disagreement suggest "
            f"{company} may continue trending upward over the next 7 days."
        )
        predicted_range = (
            round(current_price * 0.99, 2),
            round(current_price * 1.05, 2)
        )
    elif signal_score >= 0.5:
        prediction = "MILDLY BULLISH"
        confidence = "moderate"
        summary = (
            f"Mixed signals with a slight positive lean. "
            f"{company} may see modest gains but watch for volatility."
        )
        predicted_range = (
            round(current_price * 0.98, 2),
            round(current_price * 1.03, 2)
        )
    elif signal_score <= -1.5:
        prediction = "BEARISH"
        confidence = "high"
        summary = (
            f"High news disagreement and negative sentiment suggest "
            f"{company} may face downward pressure over the next 7 days."
        )
        predicted_range = (
            round(current_price * 0.95, 2),
            round(current_price * 1.01, 2)
        )
    elif signal_score <= -0.5:
        prediction = "MILDLY BEARISH"
        confidence = "moderate"
        summary = (
            f"Slightly negative signals. "
            f"{company} may dip but a reversal is possible."
        )
        predicted_range = (
            round(current_price * 0.97, 2),
            round(current_price * 1.02, 2)
        )
    else:
        prediction = "NEUTRAL"
        confidence = "low"
        summary = (
            f"Signals are mixed and inconclusive. "
            f"{company} is likely to trade sideways in the near term."
        )
        predicted_range = (
            round(current_price * 0.97, 2),
            round(current_price * 1.03, 2)
        )

    return {
        "company": company,
        "ticker": ticker,
        "current_price": current_price,
        "price_change_7d": price_change_7d,
        "prediction": prediction,
        "confidence": confidence,
        "summary": summary,
        "predicted_range": {
            "low": predicted_range[0],
            "high": predicted_range[1]
        },
        "signals": {
            "ndi_score": round(latest_ndi, 4),
            "ndi_vs_average": "above average" if ndi_rising else "below average",
            "sentiment": round(latest_sentiment, 4),
            "price_trend": trend_direction,
            "signal_score": round(signal_score, 2)
        },
        "price_history": price_history
    }