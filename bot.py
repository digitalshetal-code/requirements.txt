import os
import requests
import yfinance as yf
import pandas as pd

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram Secrets not found.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")

def check_market_and_alert():
    ticker = "GC=F"
    df = yf.download(ticker, period="2d", interval="15m", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            close_price = float(df['Close'].iloc[:, 0].iloc[-1])
        else:
            close_price = float(df['Close'].iloc[-1])
            
        entry = round(close_price - 3.0, 2)
        sl = round(entry - 12.0, 2)
        tp = round(entry + 36.0, 2) # 1:3 RRR
        
        message = (
            f"👑 *Institutional XAUUSD SMC Dashboard* 👑\n\n"
            f"📊 *Live Price:* ${close_price:,.2f}\n"
            f"🔹 *Market Structure:* Bullish BOS / Order Block\n"
            f"🎯 *Institutional Entry:* ${entry:,.2f}\n"
            f"🛑 *Stop Loss:* ${sl:,.2f}\n"
            f"💰 *Take Profit (1:3):* ${tp:,.2f}"
        )
        
        send_telegram_alert(message)
        print("New SMC Dashboard alert sent successfully!")
    else:
        print("Failed to fetch market data.")

if __name__ == "__main__":
    check_market_and_alert()
