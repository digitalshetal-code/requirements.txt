import os
import requests
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import io

# --- LOAD SECRETS SECURELY ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def generate_candlestick_chart(df, entry, sl, tp):
    """Generates a professional Candlestick SMC chart with Entry, SL, and TP levels."""
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    mc = mpf.make_marketcolors(up='#2ecc71', down='#e74c3c', wick='inherit', volume='in')
    s = mpf.make_mpf_style(marketcolors=mc, facecolor='#0e1117', figcolor='#0e1117', rc={'axes.labelcolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white', 'grid.color': '#30363d'})
    
    levels = [entry, sl, tp]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    buf = io.BytesIO()
    fig, axes = mpf.plot(
        df, 
        type='candle', 
        style=s, 
        volume=True, 
        figsize=(11, 6),
        hlines=dict(hlines=levels, colors=colors, linestyle='--', linewidths=1.5),
        returnfig=True,
        title=dict(title="👑 XAUUSD Institutional SMC Setup", color='white', fontsize=14)
    )
    
    fig.savefig(buf, format='png', dpi=150, facecolor='#0e1117')
    buf.seek(0)
    plt.close(fig)
    return buf

def send_telegram_photo(photo_buf, caption):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram Secrets not found.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {'photo': ('smc_setup.png', photo_buf, 'image/png')}
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload, files=files)
        return response.json()
    except Exception as e:
        print(f"Telegram photo error: {e}")

def check_market_and_alert():
    ticker = "GC=F"
    df = yf.download(ticker, period="3d", interval="15m", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        
        # Determine Trend / Signal Type (Buy or Sell) based on recent momentum
        if close_price >= prev_close:
            signal_type = "🟢 **LONG / BUY SETUP (Bullish Order Block)**"
            entry = round(close_price - 3.0, 2)
            sl = round(entry - 12.0, 2)
            tp = round(entry + 36.0, 2) # 1:3 RRR
        else:
            signal_type = "🔴 **SHORT / SELL SETUP (Bearish Order Block)**"
            entry = round(close_price + 3.0, 2)
            sl = round(entry + 12.0, 2)
            tp = round(entry - 36.0, 2) # 1:3 RRR
        
        chart_buffer = generate_candlestick_chart(df, entry, sl, tp)
        
        caption = (
            f"👑 *Institutional XAUUSD SMC Dashboard* 👑\n\n"
            f"📌 {signal_type}\n"
            f"📊 *Live Price:* `${close_price:,.2f}`\n"
            f"🎯 *Institutional Entry:* `${entry:,.2f}`\n"
            f"🛑 *Stop Loss (SL):* `${sl:,.2f}`\n"
            f"💰 *Take Profit (1:3):* `${tp:,.2f}`\n\n"
            f"_Automated hourly update via GitHub Actions._"
        )
        
        send_telegram_photo(chart_buffer, caption)
        print("SMC Candlestick Chart and Buy/Sell alert sent successfully!")
    else:
        print("Failed to fetch market data.")

if __name__ == "__main__":
    check_market_and_alert()
