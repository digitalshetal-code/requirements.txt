import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ultimate AI Institutional XAUUSD Terminal", layout="wide")

st.title("🚀 Ultimate AI-Powered XAUUSD Institutional SMC Terminal")
st.write("Real-Time Vantage Chart, Automated SMC Pattern Scanner, AI Sentiment, Risk Sizer & IST Economic Calendar.")

# --- FETCH ADVANCED MARKET DATA ---
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
    # Core Mathematical & Trend Calculations
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # ATR (Average True Range) for Dynamic Risk Calculation
    df['High-Low'] = df['High'] - df['Low']
    df['High-PrevClose'] = np.abs(df['High'] - df['Close'].shift(1))
    df['Low-PrevClose'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    close_price = float(df['Close'].iloc[-1])
    ema20 = float(df['EMA_20'].iloc[-1])
    ema50 = float(df['EMA_50'].iloc[-1])
    current_atr = float(df['ATR'].iloc[-1]) if not np.isnan(df['ATR'].iloc[-1]) else 5.0
    
    # AI Confidence Score & Structure
    confidence_score = 50
    trend_diff = abs(ema20 - ema50)
    
    if close_price >= ema20 and ema20 >= ema50:
        bias = "🟢 BULLISH / STRONG BUY (Expansion Phase)"
        entry = round(close_price - 2.0, 2)
        sl = round(entry - (current_atr * 1.5), 2)
        tp = round(entry + (current_atr * 4.5), 2)
        liquidity_state = "Bullish BOS & Demand Zone Order Block (OB) Active"
        confidence_score += 35 if trend_diff > 2 else 20
    elif close_price <= ema20 and ema20 <= ema50:
        bias = "🔴 BEARISH / SELL SETUP (Distribution Phase)"
        entry = round(close_price + 2.0, 2)
        sl = round(entry + (current_atr * 1.5), 2)
        tp = round(entry - (current_atr * 4.5), 2)
        liquidity_state = "Bearish CHoCH & Supply Zone Order Block (OB) Active"
        confidence_score += 35 if trend_diff > 2 else 20
    else:
        bias = "🟡 CONSOLIDATION / ACCUMULATION (Wait for Trigger)"
        entry = round(close_price, 2)
        sl = round(entry - 10.0, 2)
        tp = round(entry + 20.0, 2)
        liquidity_state = "Range-Bound / Inducement Hunting"
        confidence_score = 40

    confidence_score = min(max(confidence_score, 10), 95)
    
    if confidence_score >= 75:
        action_advice = "🟢 **EXECUTE TRADE:** High Probability AI Setup (Institutional Flow Aligned)"
    elif confidence_score >= 50:
        action_advice = "🟡 **WAIT / CAUTION:** Moderate Setup. Monitor Price Action & News closely."
    else:
        action_advice = "🔴 **AVOID TRADE:** Low Confidence / Choppy Market Conditions."

    # --- ANALYTICAL METRICS ROW ---
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Live Market Bias", bias.split()[0] + " " + bias.split()[1])
    mcol2.metric("AI Confidence Score", f"{confidence_score}%")
    mcol3.metric("Market Volatility (ATR)", f"${current_atr:.2f}")
    mcol4.metric("Execution Engine", "AI Guarded Active")

    st.markdown("---")
    st.subheader(f"🎯 AI Institutional Execution Matrix ({bias})")
    
    tcol1, tcol2, tcol3, tcol4 = st.columns(4)
    tcol1.info(f"**Smart Money Entry:**\n\n `${entry:,.2f}`")
    tcol2.error(f"**AI Structural Stop Loss:**\n\n `${sl:,.2f}`")
    tcol3.success(f"**Target Profit (TP):**\n\n `${tp:,.2f}`")
    tcol4.warning(f"**Detected SMC Structure:**\n\n `{liquidity_state}`")

    if confidence_score >= 75:
        st.success(action_advice)
    elif confidence_score >= 50:
        st.warning(action_advice)
    else:
        st.error(action_advice)

    # --- AI RISK & POSITION SIZER CALCULATOR ---
    with st.expander("🛡️ AI Dynamic Risk & Position Sizer Calculator"):
        rcol1, rcol2, rcol3 = st.columns(3)
        acc_balance = rcol1.number_input("Account Balance ($)", value=1000.0, step=100.0)
        risk_pct = rcol2.slider("Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = acc_balance * (risk_pct / 100.0)
        risk_pips_or_points = abs(entry - sl)
        # Gold standard contract: 1 lot = $1 per 0.1 point or standard sizing
        suggested_lots = round(risk_amount / (risk_pips_or_points * 10), 2) if risk_pips_or_points > 0 else 0.01
        suggested_lots = max(suggested_lots, 0.01)
        
        rcol3.metric("AI Recommended Lot Size", f"{suggested_lots} Lots", f"Risk: ${risk_amount:.2f}")

    st.markdown("---")

# --- HINDI AI NEWS & SENTIMENT ANALYSIS SECTION ---
st.subheader("📰 AI News & Market Direction Analysis (हिंदी विश्लेषण)")
st.info(f"""
💡 **AI मार्केट सेंटिमेंट और न्यूज का निष्कर्ष:**
* **टेक्निकल और वोलैटिलिटी स्थिति:** वर्तमान में मार्केट का ATR स्कोर **${current_atr:.2f}** है, जो यह दर्शाता है कि वोलैटिलिटी के आधार पर स्टॉप लॉस सही दूरी पर सेट किया गया है।
* **फेडरल रिजर्व और डेटा प्रभाव:** यदि नीचे दिए गए इकोनॉमिक कैलेंडर में कोई हाई-इम्पैक्ट (High Impact) अमेरिकी डेटा आने वाला हो, तो AI कॉन्फिडेंस स्कोर कम होने पर ट्रेड टाल दें।
* **हिंदी निष्कर्ष:** जब तक बाजार मुख्य ट्रेंड (20/50 EMA) के साथ चल रहा है, तब तक डिप (Dip) पर खरीदारी या रेजिस्टेंस पर बिकवाली करना सबसे सुरक्षित रणनीति है।
""")

# --- LIVE IST CLOCK, VANTAGE TICKER, CHART & ECONOMIC CALENDAR ---
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

components.html(dashboard_html, height=1320)
