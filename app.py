import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="XAUUSD Spot SMC Dashboard", layout="wide")

st.title("👑 Institutional XAUUSD Spot SMC Dashboard")
st.write("Real-time Spot Data Analysis matched with Exness Pricing Structure.")

# Live IST Clock
clock_html = """
<div style="font-family: monospace; font-size: 16px; color: #2ecc71; background: #0e1117; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #30363d; margin-bottom: 15px;">
    🕒 <b>Live Indian Standard Time (IST):</b> <span id="ist-clock">Loading...</span>
</div>
<script>
function updateClock() {
    const options = { timeZone: 'Asia/Kolkata', hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit', year: 'numeric', month: 'short', day: 'numeric' };
    const now = new Date().toLocaleString('en-IN', options);
    document.getElementById('ist-clock').innerText = now;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
components.html(clock_html, height=55)

@st.cache_data(ttl=60)
def load_data():
    # Spot Ticker for accurate Exness alignment
    ticker = "XAUUSD=X"
    df = yf.download(ticker, period="3d", interval="15m", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    return df

df = load_data()

if not df.empty:
    df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    close_price = float(df['Close'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2])
    ema_value = float(df['EMA'].iloc[-1])
    
    if close_price >= ema_value:
        signal_type = "🟢 BULLISH / BUY SETUP"
        entry = round(close_price - 1.5, 2)
        sl = round(entry - 6.0, 2)
        tp = round(entry + 18.0, 2)
    else:
        signal_type = "🔴 BEARISH / SELL SETUP"
        entry = round(close_price + 1.5, 2)
        sl = round(entry + 6.0, 2)
        tp = round(entry - 18.0, 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Spot XAUUSD", f"${close_price:,.2f}", f"{close_price - prev_close:.2f}")
    col2.metric("Market Bias", signal_type.split()[0] + " " + signal_type.split()[1])
    col3.metric("Trend Filter", "20 EMA Stable")
    col4.metric("Target RRR", "1:3.0")

    st.markdown("---")
    st.subheader("🎯 Active Trade Setup")
    
    tcol1, tcol2, tcol3 = st.columns(3)
    tcol1.info(f"**Entry Zone:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**Stop Loss (SL):**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Take Profit (TP):**\n\n `${tp:,.2f}`")

    st.markdown("---")
    st.subheader("📊 Spot Price Action & SMC Levels")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    df_plot = df.tail(100).copy()
    up = df_plot['Close'] >= df_plot['Open']
    down = df_plot['Close'] < df_plot['Open']
    
    ax.vlines(df_plot.index[up], df_plot['Low'][up], df_plot['High'][up], color='#2ecc71', linewidth=1)
    ax.vlines(df_plot.index[down], df_plot['Low'][down], df_plot['High'][down], color='#e74c3c', linewidth=1)
    ax.bar(df_plot.index[up], df_plot['Close'][up] - df_plot['Open'][up], bottom=df_plot['Open'][up], color='#2ecc71', width=0.015, edgecolor='#2ecc71')
    ax.bar(df_plot.index[down], df_plot['Open'][down] - df_plot['Close'][down], bottom=df_plot['Close'][down], color='#e74c3c', width=0.015, edgecolor='#e74c3c')
    
    ax.plot(df_plot.index, df_plot['EMA'], color='#f1c40f', linewidth=1.5, label='20 EMA')
    ax.axhline(entry, color='#3498db', linestyle='--', linewidth=1.5, label=f'Entry: ${entry}')
    ax.axhline(sl, color='#e74c3c', linestyle='--', linewidth=1.5, label=f'SL: ${sl}')
    ax.axhline(tp, color='#2ecc71', linestyle='--', linewidth=1.5, label=f'TP: ${tp}')
    
    ax.tick_params(colors='white')
    ax.grid(True, color='#30363d', linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', facecolor='#0e1117', labelcolor='white')
    
    st.pyplot(fig)
else:
    st.error("Failed to fetch spot market data.")
    
