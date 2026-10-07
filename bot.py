import os
import time
import logging
import asyncio
import numpy as np
import requests
from metaapi_cloud_sdk import MetaApi

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
METAAPI_TOKEN = os.environ.get('METAAPI_TOKEN')
ACCOUNT_ID = os.environ.get('ACCOUNT_ID')

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

class UltraProScalperV5:
    def __init__(self, symbol="XAUUSDm", lot_size=0.01):
        self.symbol = symbol
        self.lot_size = lot_size

    async def analyze_and_trade(self, connection):
        try:
            candles = await connection.get_candles(self.symbol, '1m', 50)
            if not candles or len(candles) < 30:
                logging.error("Candle data kam mila hai analysis ke liye.")
                return

            closes = np.array([c['close'] for c in candles])
            
            ema_fast = calculate_ema(closes, 9)
            ema_slow = calculate_ema(closes, 21)
            rsi = calculate_rsi(closes, 14)

            current_close = closes[-1]
            current_rsi = rsi[-1]
            current_ema_fast = ema_fast[-1]
            current_ema_slow = ema_slow[-1]

            price = await connection.get_symbol_price(self.symbol)
            bid, ask = price['bid'], price['ask']

            signal_msg = f"⚡ *Ultra Pro Scalper V5 [XAUUSDm]*\n\n" \
                         f"Symbol: `{self.symbol}`\n" \
                         f"Bid/Ask: `{bid}` / `{ask}`\n" \
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
    if not METAAPI_TOKEN or not ACCOUNT_ID:
        logging.error("MetaApi Token ya Account ID missing hai!")
        return

    metaapi = MetaApi(METAAPI_TOKEN)
    account = await metaapi.metatrader_account_api.get_account(ACCOUNT_ID)
    
    if account.state != 'DEPLOYED':
        logging.info("Deploying MT5 account...")
        await account.deploy()
        
    await account.wait_connected()
    connection = account.get_rpc_connection()
    await connection.connect()

    scalper = UltraProScalperV5(symbol="XAUUSDm", lot_size=0.01)
    
    send_telegram_alert("🚀 *XAUUSDm 5-Min Scalper Bot Started!* (Har 5 minute me update milega)")

    # Har 5 minute (300 seconds) me update bhejne ka loop (Total 12 iterations = 1 ghanta)
    for _ in range(12):
        await scalper.analyze_and_trade(connection)
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
