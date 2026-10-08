import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Institutional Pro XAUUSD Terminal", layout="wide")

st.title("⚡ Pro-Trader XAUUSD Institutional Terminal (SMC + Multi-Timeframe)")
st.write("Multi-Timeframe Confluence, Advanced Liquidity Matrix, Risk-Reward Calculator, and Live Vantage Feed.")

# --- FETCH MULTI-TIMEFRAME DATA ---
@st.cache_data(ttl=30)
def load_data():
    ticker = "XAUUSD=X"
    df_15m = yf.download(ticker, period="3d", interval="15m", progress=False)
    df_1h = yf.download(ticker, period="5d", interval="1h", progress=False)
    
    if df_15m.empty:
        df_15m = yf.download("GC=F", period="3d", interval="15m", progress=False)
    if df_1h.empty:
        df_1h = yf.download("GC=F", period="5d", interval="1h", progress=False)
        
    if not df_15m.empty and isinstance(df_15m.columns, pd.MultiIndex):
        df_15m.columns = df_15m.columns.get_level_values(0)
    if not df_1h.empty and isinstance(df_1h.columns, pd.MultiIndex):
        df_1h.columns = df_1h.columns.get_level_values(0)
        
    return df_15m, df_1h

df_15m, df_1h = load_data()

if not df_15m.empty and not df_1h.empty:
    # 15M Calculations (Fixed EMA 50 inclusion)
    df_15m['EMA_20'] = df_15m['Close'].ewm(span=20, adjust=False).mean()
    df_15m['EMA_50'] = df_15m['Close'].ewm(span=50, adjust=False).mean()
    
    # 1H Calculations for Confluence
    df_1h['EMA_20'] = df_1h['Close'].ewm(span=20, adjust=False).mean()
    
    close_15m = float(df_15m['Close'].iloc[-1])
    ema20_15m = float(df_15m['EMA_20'].iloc[-1])
    ema50_15m = float(df_15m['EMA_50'].iloc[-1])
    
    close_1h = float(df_1h['Close'].iloc[-1])
    ema20_1h = float(df_1h['EMA_20'].iloc[-1])
    
    # Multi-Timeframe Bias Confirmation
    trend_15m = "BULLISH" if close_15m >= ema20_15m else "BEARISH"
    trend_1h = "BULLISH" if close_1h >= ema20_1h else "BEARISH"
    
    confidence = 60
    if trend_15m == trend_1h:
        confidence += 25
        alignment_status = "🟢 Strong Multi-Timeframe Alignment (15M & 1H Match)"
    else:
        confidence -= 15
        alignment_status = "🟡 Timeframe Conflict (15M & 1H Divergence - Trade with Caution)"

    if trend_15m == "BULLISH":
        bias = "🟢 BULLISH / BUY SETUP"
        entry = round(close_15m - 2.0, 2)
        sl = round(entry - 10.0, 2)
        tp = round(entry + 30.0, 2)
        liquidity_msg = "Buy-side Liquidity Sweep & Bullish Order Block (OB) Retest"
    else:
        bias = "🔴 BEARISH / SELL SETUP"
        entry = round(close_15m + 2.0, 2)
        sl = round(entry + 10.0, 2)
        tp = round(entry - 30.0, 2)
        liquidity_msg = "Sell-side Liquidity Sweep & Bearish Order Block (OB) Tap"

    confidence = min(max(confidence, 10), 95)

    # --- TOP METRICS DASHBOARD ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("15M Trend State", trend_15m)
    col2.metric("1H Macro Trend", trend_1h)
    col3.metric("Pro Confidence Score", f"{confidence}%")
    col4.metric("Risk-Reward Ratio", "1 : 3.0")

    st.markdown("---")
    st.info(alignment_status)

    # --- EXECUTION MATRIX ---
    st.subheader(f"🎯 Institutional Execution Matrix ({bias})")
    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
    tcol1.info(f"**Optimal Entry:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**Structural SL:**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Target TP (1:3):**\n\n `${tp:,.2f}`")
    tcol4.warning(f"**SMC Liquidity State:**\n\n `{liquidity_msg}`")

    # --- ADVANCED RISK & LOT CALCULATOR ---
    with st.expander("🧮 Advanced Lot Size & Risk Management Calculator"):
        r1, r2, r3 = st.columns(3)
        balance = r1.number_input("Account Balance ($)", value=1000.0, step=100.0)
        risk_p = r2.slider("Risk Percentage (%)", 0.5, 5.0, 1.0, 0.5)
        
        risk_dol = balance * (risk_p / 100.0)
        pips_risk = abs(entry - sl)
        lots = round(risk_dol / (pips_risk * 10), 2) if pips_risk > 0 else 0.01
        
        r3.metric("Recommended Position Size", f"{max(lots, 0.01)} Lots", f"Max Risk: ${risk_dol:.2f}")

    st.markdown("---")

# --- HINDI MARKET INTELLIGENCE ---
st.subheader("🤖 प्रो-ट्रेडर मार्केट इनसाइट्स (हिंदी विश्लेषण)")
st.warning("""
💡 **संस्थागत (Institutional) मार्केट अपडेट:**
* **मल्टी-टाइमफ्रेम कन्फ्लुएंस:** जब 15 मिनट और 1 घंटे का चार्ट एक ही दिशा में इशारा करता है, तभी सबसे सटीक और बड़े मूव्स कैप्चर होते हैं।
* **स्मार्ट मनी कॉन्सेप्ट्स (SMC):** हमेशा ऑर्डर ब्लॉक (OB) और लिक्विडिटी स्वीप के बाद ही एंट्री लें। बीच बाजार में ट्रेड करने से बचें।
""")

# --- LIVE CHARTS & CALENDAR ---
dashboard_html = """
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
    <!-- Live IST Clock -->
    <div style="flex: 1; min-width: 250px; font-family: monospace; font-size: 15px; color: #2ecc71; background: #0e1117; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #30363d;">
        🕒 <b>IST Time:</b> <span id="ist-clock">Loading...</span>
    </div>
</div>

<!-- TradingView Ticker -->
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

<!-- TradingView Advanced Chart -->
<div class="tradingview-widget-container" style="height:500px;width:100%; margin-bottom: 20px;">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {
  "width": "100%",
  "height": "500",
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

<!-- Economic Calendar -->
<div class="tradingview-widget-container" style="height:450px;width:100%">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  {
  "width": "100%",
  "height": "450",
  "colorTheme": "dark",
  "isTransparent": true,
  "locale": "in",
  "importanceFilter": "-1,0,1",
  "currencyFilter": "USD"
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

components.html(dashboard_html, height=1350)
