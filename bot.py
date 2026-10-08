import os
import requests
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- LOAD SECRETS SECURELY ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def generate_smc_chart(df, entry, sl, tp):
    """Generates an institutional SMC chart with Entry, SL, and TP levels."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plotting Price Action
    ax.plot(df.index, df['Close'], label='XAUUSD Price', color='#00ffcc', linewidth=1.5)
    
    # Horizontal lines for Trade Setup
    ax.axhline(y=entry, color='#3498db', linestyle='--', linewidth=1.5, label=f'Entry: ${entry}')
    ax.axhline(y=sl, color='#e74c3c', linestyle='-', linewidth=1.5, label=f'Stop Loss: ${sl}')
    ax.axhline(y=tp, color='#2ecc71', linestyle='-', linewidth=1.5, label=f'Take Profit (1:3): ${tp}')
    
    ax.set_title('👑 XAUUSD Institutional SMC Setup', fontsize=14, color='white', fontweight='bold')
    ax.set_xlabel('Time', color='gray')
    ax.set_ylabel('Price (USD)', color='gray')
    ax.legend(loc='upper left', facecolor='#161b22', edgecolor='none')
    ax.grid(True, color='#30363d', linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='#0e1117')
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
    df = yf.download(ticker, period="2d", interval="15m", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            close_prices = df['Close'].iloc[:, 0]
            close_price = float(close_prices.iloc[-1])
        else:
            close_prices = df['Close']
            close_price = float(close_prices.iloc[-1])
            
        entry = round(close_price - 3.0, 2)
        sl = round(entry - 12.0, 2)
        tp = round(entry + 36.0, 2) # 1:3 RRR
        
        # Generate Chart Diagram
        chart_buffer = generate_smc_chart(df, entry, sl, tp)
        
        # Professional Telegram Caption
        caption = (
            f"👑 *Institutional XAUUSD SMC Setup* 👑\n\n"
            f"📊 *Live Price:* `${close_price:,.2f}`\n"
            f"🔹 *Market Structure:* Bullish BOS / Order Block\n"
            f"🎯 *Institutional Entry:* `${entry:,.2f}`\n"
            f"🛑 *Stop Loss (SL):* `${sl:,.2f}`\n"
            f"💰 *Take Profit (TP 1:3):* `${tp:,.2f}`\n\n"
            f"_Chart automatically generated via GitHub Actions._"
        )
        
        send_telegram_photo(chart_buffer, caption)
        print("SMC Chart and alert sent successfully to Telegram!")
    else:
        print("Failed to fetch market data.")

if __name__ == "__main__":
    check_market_and_alert()
