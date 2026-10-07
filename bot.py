import os
import time
import logging
import asyncio
import numpy as np
import pandas as pd
import yfinance as yf
import requests

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations (Telegram tokens aapke GitHub Secrets me hone chahiye)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_alert(message: str):
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Telegram error: {e}")

def calculate_ema(prices, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(prices, weights, mode='full')[:len(prices)]
    a[:period] = a[period]
    return a

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    if down == 0:
        return 100.0
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        if down == 0:
            rsi[i] = 100.0
        else:
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
    return rsi

class FreeScalperBot:
    def __init__(self, symbol="GC=F"): # GC=F is Gold / XAUUSD equivalent
        self.symbol = symbol

    def analyze_market(self):
        try:
            # Yahoo Finance se 1-minute ka data fetch karna (100% Free)
            data = yf.download(tickers=self.symbol, period="1d", interval="1m", progress=False)
            if data.empty or len(data) < 30:
                logging.error("Data kam mila hai analysis ke liye.")
                return

            closes = data['Close'].values.flatten()
            current_close = float(closes[-1])

            ema_fast = calculate_ema(closes, 9)
            ema_slow = calculate_ema(closes, 21)
            rsi = calculate_rsi(closes, 14)

            current_rsi = float(rsi[-1])
            current_ema_fast = float(ema_fast[-1])
            current_ema_slow = float(ema_slow[-1])

            signal_msg = f"⚡ *Ultra Pro Scalper V5 [Free Mode]*\n\n" \
                         f"Symbol: `XAUUSD`\n" \
                         f"Price: `{current_close:.2f}`\n" \
                         f"RSI (14): `{current_rsi:.2f}`\n" \
                         f"EMA (9/21): `{current_ema_fast:.2f}` / `{current_ema_slow:.2f}`\n"

            if current_ema_fast > current_ema_slow and current_rsi < 70:
                signal_msg += "\n🟢 *Signal:* **BUY Setup Active** (Bullish)"
            elif current_ema_fast < current_ema_slow and current_rsi > 30:
                signal_msg += "\n🔴 *Signal:* **SELL Setup Active** (Bearish)"
            else:
                signal_msg += "\n⏳ *Status:* Market Neutral"

            send_telegram_alert(signal_msg)

        except Exception as e:
            logging.error(f"Error during analysis: {e}")

async def main():
    bot = FreeScalperBot(symbol="GC=F")
    send_telegram_alert("🚀 *Free Scalper Bot Started!* (XAUUSD Live Updates)")

    # Har 5 minute (300 seconds) me update bhejne ka loop
    for _ in range(12):
        bot.analyze_market()
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
    
