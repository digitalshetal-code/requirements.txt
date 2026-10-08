import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Elon Musk Neural XAUUSD Terminal", layout="wide")

st.title("🛰️ Elon Musk's Neural XAUUSD Institutional Command Center")
st.write("First-Principles Automated Liquidity Matrix, Neural Trend Engine, Risk-Reward Optimization, and Live IST Intelligence.")

# --- FETCH MULTI-TIMEFRAME DEEP DATA ---
@st.cache_data(ttl=20)
def load_deep_market_data():
    ticker = "XAUUSD=X"
    df_5m = yf.download(ticker, period="2d", interval="5m", progress=False)
    df_15m = yf.download(ticker, period="3d", interval="15m", progress=False)
    df_1h = yf.download(ticker, period="7d", interval="1h", progress=False)
    
    for df in [df_5m, df_15m, df_1h]:
        if not df.empty and isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
    if df_15m.empty:
        df_15m = yf.download("GC=F", period="3d", interval="15m", progress=False)
        if not df_15m.empty and isinstance(df_15m.columns, pd.MultiIndex):
            df_15m.columns = df_15m.columns.get_level_values(0)
            
    return df_5m, df_15m, df_1h

df_5m, df_15m, df_1h = load_deep_market_data()

if not df_15m.empty and not df_1h.empty:
    # --- QUANTITATIVE MATH & NEURAL ENGINE ---
    df_15m['EMA_9'] = df_15m['Close'].ewm(span=9, adjust=False).mean()
    df_15m['EMA_21'] = df_15m['Close'].ewm(span=21, adjust=False).mean()
    df_15m['EMA_50'] = df_15m['Close'].ewm(span=50, adjust=False).mean()
    df_1h['EMA_20'] = df_1h['Close'].ewm(span=20, adjust=False).mean()
    
    # Volatility & Momentum (ATR & RSI approximation)
    df_15m['HL_Spread'] = df_15m['High'] - df_15m['Low']
    atr = float(df_15m['HL_Spread'].rolling(14).mean().iloc[-1])
    
    close_price = float(df_15m['Close'].iloc[-1])
    ema9 = float(df_15m['EMA_9'].iloc[-1])
    ema21 = float(df['EMA_21'].iloc[-1])
    ema50 = float(df['EMA_50'].iloc[-1])
    macro_1h = float(df_1h['Close'].iloc[-1])
    macro_ema20 = float(df_1h['EMA_20'].iloc[-1])
    
    # Neural Bias & Confidence Calculation (Elon Musk First-Principles Logic)
    neural_score = 50
    if close_price > ema9 > ema21 > ema50:
        market_regime = "🟢 AGGRESSIVE BULLISH EXPANSION"
        bias = "LONG (BUY)"
        entry = round(close_price - (atr * 0.3), 2)
        sl = round(entry - (atr * 1.5), 2)
        tp = round(entry + (atr * 4.5), 2)
        neural_score += 35
        liquidity_status = "Smart Money Demand Zone Sweep & Bullish Order Block Active"
    elif close_price < ema9 < ema21 < ema50:
        market_regime = "🔴 AGGRESSIVE BEARISH DISTRIBUTION"
        bias = "SHORT (SELL)"
        entry = round(close_price + (atr * 0.3), 2)
        sl = round(entry + (atr * 1.5), 2)
        tp = round(entry - (atr * 4.5), 2)
        neural_score += 35
        liquidity_status = "Smart Money Supply Zone Tap & Bearish BOS Active"
    else:
        market_regime = "🟡 HIGH-FREQUENCY ACCUMULATION / CHOP"
        bias = "NEUTRAL (WAIT)"
        entry = round(close_price, 2)
        sl = round(entry - (atr * 1.2), 2)
        tp = round(entry + (atr * 2.5), 2)
        neural_score = 45
        liquidity_status = "Inducement Hunting / Range-Bound Liquidity Sweep"

    if macro_1h >= macro_ema20 and "BULLISH" in market_regime:
        neural_score += 10
    elif macro_1h < macro_ema20 and "BEARISH" in market_regime:
        neural_score += 10

    neural_score = min(max(neural_score, 10), 98)

    # --- COMMAND CENTER METRICS BAR ---
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Neural Market Regime", market_regime.split()[1])
    m2.metric("AI Execution Bias", bias)
    m3.metric("Neural Confidence", f"{neural_score}%")
    m4.metric("Volatility (ATR)", f"${atr:.2f}")
    m5.metric("Execution Engine", "ARMED & SECURE")

    st.markdown("---")

    # --- EXECUTION MATRIX DISPLAY ---
    st.subheader(f"⚡ Institutional Execution Setup ({market_regime})")
    
    t1, t2, t3, t4 = st.columns(4)
    t1.info(f"**Optimal Entry Target:**\n\n `${entry:,.2f}`")
    t2.error(f"**Neural Stop Loss (SL):**\n\n `${sl:,.2f}`")
    t3.success(f"**Take Profit Target (TP):**\n\n `${tp:,.2f}`")
    t4.warning(f"**Institutional Liquidity State:**\n\n `{liquidity_status}`")

    if neural_score >= 80:
        st.success("🟢 **SYSTEM STATUS: HIGH PROBABILITY EXECUTION ZONE.** Institutional flow matches multi-timeframe alignment. Trade authorized.")
    elif neural_score >= 50:
        st.warning("🟡 **SYSTEM STATUS: CAUTION / ACCUMULATION.** Price is testing institutional liquidity boundaries. Wait for structural breakout.")
    else:
        st.error("🔴 **SYSTEM STATUS: CHOPPY / NO-TRADE ZONE.** Market is hunting retail stop losses. Stand down.")

    # --- QUANTITATIVE RISK & POSITION SIZER ---
    with st.expander("🛡️ Autonomous Risk Management & Quantum Lot Sizer"):
        rc1, rc2, rc3 = st.columns(3)
        account_bal = rc1.number_input("Account Capital ($)", value=2000.0, step=100.0)
        risk_pct = rc2.slider("Risk Tolerance per Trade (%)", 0.5, 5.0, 1.0, 0.5)
        
        risk_capital = account_bal * (risk_pct / 100.0)
        pips_at_risk = abs(entry - sl)
        recommended_lots = round(risk_capital / (pips_at_risk * 10), 2) if pips_at_risk > 0 else 0.01
        
        rc3.metric("Calculated Lot Size", f"{max(recommended_lots, 0.01)} Lots", f"Max Financial Risk: ${risk_capital:.2f}")

    st.markdown("---")

# --- ELON MUSK STYLE DEEP AI NEWS & MACRO SENTIMENT (HINDI) ---
st.subheader("🌐 Neural News & Macroeconomic Impact Intelligence (डीप हिंदी विश्लेषण)")

st.info(f"""
### 🧠 एलन मस्क फर्स्ट-पर्पिनिपल्स मार्केट डीकोड (First-Principles Analysis):
1. **मार्केट का मूल सत्य (Root Truth):** 
   सोना (XAUUSD) किसी के कहने से नहीं चलता, यह पूरी तरह से **लिक्विडिटी (Liquidity) और संस्थागत ऑर्डर ब्लॉक्स (Institutional Order Blocks)** पर चलता है। जब बड़े बैंक और हेज फंड्स रिटेल ट्रेडर्स के स्टॉप लॉस को हंट करते हैं, तभी असली मूव आता है।
2. **वर्तमान तकनीकी और वोलैटिलिटी स्थिति:** 
   फिलहाल मार्केट का ATR **${atr:.2f}** है। इसका मतलब यह है कि स्टॉप लॉस को हमेशा इस वोलैटिलिटी के आधार पर ही सेट किया जाना चाहिए ताकि सामान्य उतार-चढ़ाव में ट्रेड न कटे।
3. **फेडरल रिजर्व और मैक्रो न्यूज का असर:** 
   * जब भी अमेरिका का इन्फ्लेशन (CPI) या जॉब डेटा (NFP) अनुमान से अलग आता है, तो एल्गोरिदम मिलीसेकंड में सोने को ऊपर या नीचे खींचते हैं। 
   * **फिनांस कमांड:** यदि नीचे दिए गए लाइव कैलेंडर में कोई 'High-Impact' लाल डेटा आने वाला हो, तो उससे 10 मिनट पहले अपनी सभी पोजीशन को न्यूट्रल कर लें या ट्रेलिंग स्टॉप लॉस का उपयोग करें।
""")

st.markdown("---")

# --- LIVE TRADINGVIEW CHARTS, TICKER & ECONOMIC CALENDAR ---
dashboard_html = """
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
    <!-- Live IST Clock -->
    <div style="flex: 1; min-width: 250px; font-family: monospace; font-size: 15px; color: #2ecc71; background: #0e1117; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #30363d;">
        🕒 <b>IST Time (Live):</b> <span id="ist-clock">Loading...</span>
    </div>
</div>

<!-- TradingView Vantage Ticker -->
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

<!-- TradingView Advanced Live Moving Chart -->
<div class="tradingview-widget-container" style="height:520px;width:100%; margin-bottom: 20px;">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {
  "width": "100%",
  "height": "520",
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

<!-- TradingView Economic Calendar (IST Aligned) -->
<div class="tradingview-widget-container" style="height:460px;width:100%">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  {
  "width": "100%",
  "height": "460",
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

components.html(dashboard_html, height=1380)
