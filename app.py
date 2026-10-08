import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="XAUUSD Live SMC Trading Dashboard", layout="wide")

st.title("👑 XAUUSD Live SMC Institutional Dashboard")

# --- FETCH MARKET DATA FOR SMC CALCULATIONS ---
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
    df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
    close_price = float(df['Close'].iloc[-1])
    ema_value = float(df['EMA'].iloc[-1])
    
    if close_price >= ema_value:
        signal_title = "🟢 BULLISH / BUY SETUP (Above 20 EMA)"
        entry = round(close_price - 3.0, 2)
        sl = round(entry - 12.0, 2)
        tp = round(entry + 36.0, 2)
    else:
        signal_title = "🔴 BEARISH / SELL SETUP (Below 20 EMA)"
        entry = round(close_price + 3.0, 2)
        sl = round(entry + 12.0, 2)
        tp = round(entry - 36.0, 2)

    # Active SMC Trade Setup Display
    st.subheader(f"🎯 Active SMC Trade Setup ({signal_title})")
    
    tcol1, tcol2, tcol3 = st.columns(3)
    tcol1.info(f"**Institutional Entry Zone:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**Structural Stop Loss (SL):**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Take Profit Target (TP):**\n\n `${tp:,.2f}`")

    st.markdown("---")

# --- LIVE IST CLOCK, VANTAGE TICKER & LIVE MOVING CHART ---
dashboard_html = """
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
    <!-- Live IST Clock -->
    <div style="flex: 1; min-width: 250px; font-family: monospace; font-size: 15px; color: #2ecc71; background: #0e1117; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #30363d;">
        🕒 <b>IST Time:</b> <span id="ist-clock">Loading...</span>
    </div>
</div>

<!-- TradingView Live XAUUSD Ticker Widget (Vantage) -->
<div class="tradingview-widget-container" style="margin-bottom: 15px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>
  {
  "symbol": "VANTAGE:XAUUSD",
  "width": "100%",
  "colorTheme": "dark",
  "isTransparent": true,
  "locale": "in"
}
  </script>
</div>

<!-- TradingView Advanced Real-Time Live Moving Candlestick Chart (Vantage) -->
<div class="tradingview-widget-container" style="height:550px;width:100%">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {
  "width": "100%",
  "height": "550",
  "symbol": "VANTAGE:XAUUSD",
  "interval": "15",
  "timezone": "Asia/Kolkata",
  "theme": "dark",
  "style": "1",
  "locale": "in",
  "allow_symbol_change": false,
  "calendar": false,
  "support_host": "https://www.tradingview.com"
}
  </script>
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

components.html(dashboard_html, height=740)
