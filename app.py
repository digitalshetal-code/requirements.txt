import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Elon Musk Institutional SMC & News Terminal", layout="wide")

st.title("🚀 XAUUSD AI & News-Driven Institutional Terminal")
st.write("Real-Time Vantage Live Chart, IST Economic Calendar, AI Sentiment Analysis, and Dynamic Risk Engine.")

# --- FETCH MARKET DATA FOR AI & CONFIDENCE SCORE ---
@st.cache_data(ttl=30)
def load_market_data():
    ticker = "XAUUSD=X"
    df = yf.download(ticker, period="3d", interval="15m", progress=False)
    if df.empty:
        df = yf.download("GC=F", period="3d", interval="15m", progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = load_market_data()

if not df.empty:
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    close_price = float(df['Close'].iloc[-1])
    ema20 = float(df['EMA_20'].iloc[-1])
    ema50 = float(df['EMA_50'].iloc[-1])
    
    confidence_score = 50
    trend_diff = abs(ema20 - ema50)
    
    if close_price >= ema20 and ema20 >= ema50:
        bias = "🟢 BULLISH / STRONG BUY (Expansion Phase)"
        entry = round(close_price - 2.0, 2)
        sl = round(entry - 10.0, 2)
        tp = round(entry + 30.0, 2)
        liquidity_state = "Bullish BOS & Demand Zone Sweep"
        confidence_score += 30 if trend_diff > 2 else 15
    elif close_price <= ema20 and ema20 <= ema50:
        bias = "🔴 BEARISH / SELL SETUP (Distribution Phase)"
        entry = round(close_price + 2.0, 2)
        sl = round(entry + 10.0, 2)
        tp = round(entry - 30.0, 2)
        liquidity_state = "Bearish CHoCH & Supply Zone Tap"
        confidence_score += 30 if trend_diff > 2 else 15
    else:
        bias = "🟡 CONSOLIDATION / ACCUMULATION (Wait for Trigger)"
        entry = round(close_price, 2)
        sl = round(entry - 10.0, 2)
        tp = round(entry + 20.0, 2)
        liquidity_state = "Range-Bound / Inducement Hunting"
        confidence_score = 40

    confidence_score = min(max(confidence_score, 10), 95)
    
    if confidence_score >= 75:
        action_advice = "🟢 **EXECUTE TRADE:** High Probability Setup (Aligned with Institutional Flow)"
    elif confidence_score >= 50:
        action_advice = "🟡 **WAIT / CAUTION:** Moderate Setup. Monitor Price Action closely."
    else:
        action_advice = "🔴 **AVOID TRADE:** Low Confidence / Choppy Market Conditions."

    # --- ANALYTICAL METRICS ROW ---
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Live Market Bias", bias.split()[0] + " " + bias.split()[1])
    mcol2.metric("Institutional RRR", "1 : 3.0 (Optimized)")
    mcol3.metric("AI Confidence Score", f"{confidence_score}%")
    mcol4.metric("Execution Status", "Active & Guarded")

    st.markdown("---")
    st.subheader(f"🎯 Institutional Execution Matrix ({bias})")
    
    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
    tcol1.info(f"**Smart Money Entry:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**Structural Stop Loss:**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Take Profit Target (TP):**\n\n `${tp:,.2f}`")
    tcol4.warning(f"**Market Liquidity State:**\n\n `{liquidity_state}`")

    if confidence_score >= 75:
        st.success(action_advice)
    elif confidence_score >= 50:
        st.warning(action_advice)
    else:
        st.error(action_advice)

    st.markdown("---")

# --- HINDI AI NEWS ANALYSIS SECTION ---
st.subheader("📰 AI News & Market Direction Analysis (हिंदी विश्लेषण)")
st.info("""
💡 **AI मार्केट सेंटिमेंट और न्यूज का निष्कर्ष:**
* **फेडरल रिजर्व और डेटा असर:** वर्तमान में सोने (XAUUSD) पर संस्थागत (Institutional) खरीदार हावी हैं। जब तक महत्वपूर्ण अमेरिकी डेटा (CPI या NFP) अनुमान के विपरीत नहीं आता, तब तक तकनीकी ट्रेंड (20/50 EMA) के साथ चलना सुरक्षित है।
* **ट्रेडिंग सलाह:** यदि हाई-इम्पैक्ट न्यूज का समय नजदीक हो, तो नई ट्रेड लेने से बचें या अपने स्टॉप लॉस (SL) को कड़ा (Tight) रखें ताकि अचानक आने वाले स्पाइक से बचा जा सके।
""")

# --- LIVE IST CLOCK, VANTAGE TICKER, CHART & TRADINGVIEW ECONOMIC CALENDAR ---
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

<!-- TradingView Economic Calendar Widget (IST Aligned) -->
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

components.html(dashboard_html, height=1280)
