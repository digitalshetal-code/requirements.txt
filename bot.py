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

def find_institutional_levels(df):
    """Institutional Order Blocks & Liquidity Levels Finder"""
    highs = df['High'].values.flatten()
    lows = df['Low'].values.flatten()
    closes = df['Close'].values.flatten()
    
    if len(closes) < 20:
        return 0.0, 0.0, "NEUTRAL"
    
    # Recent Institutional Swing Points (Supply & Demand Zones)
    resistance_level = float(np.max(highs[-15:]))
    support_level = float(np.min(lows[-15:]))
    
    current_price = float(closes[-1])
    prev_price = float(closes[-2])
    
    # Market Structure (BOS / ChoCH check)
    if current_price > resistance_level:
        structure = "BULLISH_BOS"
    elif current_price < support_level:
        structure = "BEARISH_BOS"
    elif current_price > prev_price:
        structure = "BULLISH_REVERSAL_ZONE" if current_price <= support_level + 2.0 else "BULLISH_IMPULSE"
    else:
        structure = "BEARISH_REVERSAL_ZONE" if current_price >= resistance_level - 2.0 else "BEARISH_IMPULSE"
        
    return resistance_level, support_level, structure

class InstitutionalLevelBot:
    def __init__(self, symbol="GC=F"):
        self.symbol = symbol

    def analyze_market(self):
        try:
            logging.info("Fetching 1D, 4H, 1H, 15M, 5M, 1M data for Institutional Levels...")
            
            # Multi-Timeframe Data Fetching
            df_1d = yf.download(tickers=self.symbol, period="30d", interval="1d", progress=False)
            df_1h = yf.download(tickers=self.symbol, period="7d", interval="1h", progress=False)
            df_15m = yf.download(tickers=self.symbol, period="5d", interval="15m", progress=False)
            df_5m = yf.download(tickers=self.symbol, period="2d", interval="5m", progress=False)
            df_1m = yf.download(tickers=self.symbol, period="1d", interval="1m", progress=False)

            if df_1d.empty or df_1h.empty or df_15m.empty or df_5m.empty or df_1m.empty:
                logging.error("Data fetching incomplete.")
                return

            # Resample 1h to 4h structure
            df_4h = df_1h.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

            # Analyze Institutional Levels across Timeframes
            res_1d, sup_1d, struct_1d = find_institutional_levels(df_1d)
            res_4h, sup_4h, struct_4h = find_institutional_levels(df_4h)
            res_1h, sup_1h, struct_1h = find_institutional_levels(df_1h)
            res_15m, sup_15m, struct_15m = find_institutional_levels(df_15m)
            res_5m, sup_5m, struct_5m = find_institutional_levels(df_5m)
            
            curr_price = float(df_1m['Close'].values[-1])

            signal_msg = f"🏛️ *Institutional Smart Money Engine*\n\n" \
                         f"Symbol: `XAUUSD (Gold)`\n" \
                         f"Current Price: `{curr_price:.2f}`\n\n" \
                         f"🔍 *Key Institutional Levels (Pre-Calculated):*\n" \
                         f"• **Major Resistance (Supply):** `{res_1h:.2f}`\n" \
                         f"• **Major Support (Demand):** `{sup_1h:.2f}`\n" \
                         f"• **5M Critical Zone:** `{sup_5m:.2f}` / `{res_5m:.2f}`\n\n" \
                         f"📊 *Timeframe Structure:*\n" \
                         f"• 1D: `{struct_1d}`\n" \
                         f"• 4H: `{struct_4h}`\n" \
                         f"• 15M: `{struct_15m}`\n" \
                         f"• 5M/1M: `{struct_5m}`\n\n"

            # Pre-planned Institutional Entry, Stop Loss & Targets
            if curr_price <= sup_5m + 1.5:
                # Price Demand / Support zone ke paas hai -> Reversal Buy Setup
                entry = curr_price
                sl = sup_5m - 2.0  # Support ke thoda niche strict SL
                tp = res_1h        # Target major resistance tak
                signal_msg += f"🚀 *INSTITUTIONAL DEMAND REVERSAL (BUY)*\n" \
                             f"• *Reason:* Rejection at Key Support Zone\n" \
                             f"• *Entry:* `{entry:.2f}`\n" \
                             f"• *Stop Loss (SL):* `{sl:.2f}`\n" \
                             f"• *Take Profit (TP):* `{tp:.2f}`"

            elif curr_price >= res_5m - 1.5:
                # Price Supply / Resistance zone ke paas hai -> Reversal Sell Setup
                entry = curr_price
                sl = res_5m + 2.0  # Resistance ke thoda upar strict SL
                tp = sup_1h        # Target major support tak
                signal_msg += f"📉 *INSTITUTIONAL SUPPLY REVERSAL (SELL)*\n" \
                             f"• *Reason:* Rejection at Key Resistance Zone\n" \
                             f"• *Entry:* `{entry:.2f}`\n" \
                             f"• *Stop Loss (SL):* `{sl:.2f}`\n" \
                             f"• *Take Profit (TP):* `{tp:.2f}`"

            elif "BUSH" in struct_15m or "BUSH" in struct_4h:
                entry = curr_price
                sl = sup_5m - 1.5
                tp = entry + (entry - sl) * 3.0
                signal_msg += f"🟢 *BOS BREAKOUT CONTINUATION (BUY)*\n" \
                             f"• *Entry:* `{entry:.2f}`\n" \
                             f"• *Stop Loss:* `{sl:.2f}`\n" \
                             f"• *TP (1:3):* `{tp:.2f}`"
            else:
                signal_msg += f"⏳ *Status:* Waiting for Price to Reach Key Institutional Levels"

            send_telegram_alert(signal_msg)

        except Exception as e:
            logging.error(f"Error in Institutional Levels execution: {e}")

async def main():
    bot = InstitutionalLevelBot(symbol="GC=F")
    send_telegram_alert("🚀 *Institutional Levels & Reversal Bot Active!*")

    for _ in range(12):
        bot.analyze_market()
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
