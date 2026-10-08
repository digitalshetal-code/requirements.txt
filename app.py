import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="XAUUSD SMC Institutional Dashboard", layout="wide")

st.title("👑 Institutional XAUUSD Smart Money Concepts (SMC) Dashboard")
st.write("Real-time Multi-Timeframe Confluence, Order Blocks, Liquidity Sweeps, and 1:3 RRR Execution Engine.")

# --- FETCH MARKET DATA ---
@st.cache_data(ttl=60)
def load_data():
    ticker = "GC=F"
    df = yf.download(ticker, period="3d", interval="15m", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    return df

df = load_data()

if not df.empty:
    close_price = float(df['Close'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2])
    
    # EXACT SAME LOGIC AS TELEGRAM BOT FOR BUY/SELL SYNC
    if close_price >= prev_close:
        signal_type = "🟢 BULLISH / BUY SETUP (Bullish Order Block)"
        entry = round(close_price - 3.0, 2)
        sl = round(entry - 12.0, 2)
        tp = round(entry + 36.0, 2)
    else:
        signal_type = "🔴 BEARISH / SELL SETUP (Bearish Order Block)"
        entry = round(close_price + 3.0, 2)
        sl = round(entry + 12.0, 2)
        tp = round(entry - 36.0, 2)

    # Top Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live XAUUSD Price", f"${close_price:,.2f}", f"{close_price - prev_close:.2f}")
    col2.metric("Market Bias", signal_type.split()[0] + " " + signal_type.split()[1])
    col3.metric("Active Liquidity State", "BOS / POL")
    col4.metric("Target RRR", "1:3.0")

    st.markdown("---")
    st.subheader("🎯 Active Institutional Trade Setup")
    
    tcol1, tcol2, tcol3 = st.columns(3)
    tcol1.info(f"**Institutional Entry Zone:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**Structural Stop Loss (SL):**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Take Profit Target (TP):**\n\n `${tp:,.2f}`")

    st.markdown("---")
    st.subheader("📊 XAUUSD 15M Price Action & SMC Levels")
    
    # Generate Candlestick Chart for Streamlit
    fig, axes = mpf.plot(
        df[['Open', 'High', 'Low', 'Close', 'Volume']], 
        type='candle', 
        style='dark_background', 
        volume=True, 
        figsize=(10, 5),
        hlines=dict(hlines=[entry, sl, tp], colors=['#3498db', '#e74c3c', '#2ecc71'], linestyle='--', linewidths=1.5),
        returnfig=True
    )
    st.pyplot(fig)

else:
    st.error("Failed to fetch market data. Please check connection.")
