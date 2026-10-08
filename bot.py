import os
import requests
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import io

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def generate_candlestick_chart(df, entry, sl, tp):
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
        title=dict(title="👑 XAUUSD Spot SMC Setup (Exness Matched)", color='white', fontsize=14)
    )
    fig.savefig(buf, format='png', dpi=150, facecolor='#0e1117')
    buf.seek(0)
    plt.close(fig)
    return buf

def send_telegram_photo(photo_buf, caption):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {'photo': ('smc_setup.png', photo_buf, 'image/png')}
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, files=files)
    except Exception as e:
        print(f"Error: {e}")

def check_market_and_alert():
    # Using Spot Gold Ticker to match Exness pricing closely
    ticker = "XAUUSD=X"
    df = yf.download(ticker, period="3d", interval="15m", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
        close_price = float(df['Close'].iloc[-1])
        ema_value = float(df['EMA'].iloc[-1])
        
        if close_price >= ema_value:
            signal_type = "🟢 **LONG / BUY SETUP (Spot Bullish)**"
            entry = round(close_price - 1.5, 2)
            sl = round(entry - 6.0, 2)
            tp = round(entry + 18.0, 2)
        else:
            signal_type = "🔴 **SHORT / SELL SETUP (Spot Bearish)**"
            entry = round(close_price + 1.5, 2)
            sl = round(entry + 6.0, 2)
            tp = round(entry - 18.0, 2)
        
        chart_buffer = generate_candlestick_chart(df, entry, sl, tp)
        
        caption = (
            f"👑 *XAUUSD Spot SMC Dashboard* 👑\n\n"
            f"📌 {signal_type}\n"
            f"📊 *Spot Price:* `${close_price:,.2f}`\n"
            f"🎯 *Entry Zone:* `${entry:,.2f}`\n"
            f"🛑 *Stop Loss:* `${sl:,.2f}`\n"
            f"💰 *Take Profit:* `${tp:,.2f}`\n\n"
            f"_Synced with Spot Data._"
        )
        send_telegram_photo(chart_buffer, caption)

if __name__ == "__main__":
    check_market_and_alert()
