import yfinance as yf
import pandas as pd
import google.generativeai as genai

GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

def get_indian_stock_data(symbol, days=30):
    stock = yf.Ticker(f"{symbol}.NS")
    df = stock.history(period=f"{days}d")
    return df[["Close", "Volume"]]

def add_volume_analysis(df, period=50):
    df["Volume_MA"] = df["Volume"].rolling(window=period, min_periods=1).mean()
    return df

def add_moving_averages(df):
    df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["SMA_200"] = df["Close"].rolling(window=200, min_periods=1).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    return df


def calculate_rsi(df, period=16):
    """Calculates RSI for a given stock DataFrame."""
    delta = df["Close"].diff(1)  # Get daily price change
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
    rs = gain / loss
    df[f"RSI_{period}"] = 100 - (100 / (1 + rs))
    return df


def get_gemini_stock_insight(symbol, df):
    """Generates AI-powered technical analysis using Gemini AI."""

    # Extract latest values
    latest_close = df["Close"].iloc[-1]
    latest_sma_50 = df["SMA_50"].iloc[-1]
    latest_sma_200 = df["SMA_200"].iloc[-1]
    latest_ema_20 = df["EMA_20"].iloc[-1]
    latest_rsi_14 = df["RSI_14"].iloc[-1]
    latest_volume = df["Volume"].iloc[-1]
    latest_volume_ma = df["Volume_MA"].iloc[-1]

    # Prepare prompt for Gemini AI
    prompt = f"""
    Stock Symbol: {symbol}
    - Latest Close Price: {latest_close}
    - 50-day SMA: {latest_sma_50}
    - 200-day SMA: {latest_sma_200}
    - 20-day EMA: {latest_ema_20}
    - 14-day RSI: {latest_rsi_14}
    - Latest Trading Volume: {latest_volume}
    - 50-day Average Volume: {latest_volume_ma}

    Based on these indicators:
    1. Analyze if the stock is in a bullish or bearish trend.
    2. Suggest potential buy/sell opportunities.
    3. Highlight key support/resistance levels.
    4. Provide insights on volume trends and RSI signals.
    5. Give a trading recommendation based on the current trend.
    6. Also tell other stocks within same range.
    """

    # Call Gemini AI for analysis
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    return response.text


def analyze_stock(symbol, days=90):
  stock_data = get_indian_stock_data(symbol, days)
  stock_data = add_volume_analysis(stock_data, 50);
  stock_data = add_moving_averages(stock_data);
  stock_data = calculate_rsi(stock_data, 14);
  ai_insight = get_gemini_stock_insight(symbol, stock_data);
  return ai_insight;

symbol = "TCS"
insight = analyze_stock(symbol)
print(insight)
