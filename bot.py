import os
import time
import logging
import numpy as np
import requests
from metaapi_cloud_sdk import MetaApi

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations (GitHub Secrets se values automatically fetch hongi)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
METAAPI_TOKEN = os.environ.get('METAAPI_TOKEN')
ACCOUNT_ID = os.environ.get('ACCOUNT_ID', 'YOUR_MT5_ACCOUNT_ID')

def send_telegram_alert(message: str):
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logging.error("Telegram credentials missing!")
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Telegram error: {e}")

class UltraProScalperV5:
    def __init__(self, symbol="XAUUSD", lot_size=0.01, sl_pips=20, tp_pips=40):
        self.symbol = symbol
        self.lot_size = lot_size
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.prices = []

    def calculate_ema(self, data, period=14):
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()
        a = np.convolve(data, weights, mode='valid')
        return a[-1] if len(a) > 0 else None

    def calculate_rsi(self, data, period=14):
        if len(data) < period + 1:
            return 50.0
        deltas = np.diff(data)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        if down == 0:
            return 100.0
        rs = up / down
        return 100.0 - (100.0 / (1.0 + rs))

    def evaluate(self, current_bid, current_ask):
        self.prices.append(current_bid)
        if len(self.prices) > 50:
            self.prices.pop(0)
        if len(self.prices) < 20:
            return None

        ema_val = self.calculate_ema(self.prices, 14)
        rsi_val = self.calculate_rsi(self.prices, 14)

        if ema_val is None or rsi_val is None:
            return None

        if current_bid > ema_val and rsi_val < 45:
            return {"action": "BUY", "sl": current_bid - (self.sl_pips * 0.1), "tp": current_bid + (self.tp_pips * 0.1)}
        elif current_bid < ema_val and rsi_val > 55:
            return {"action": "SELL", "sl": current_bid + (self.sl_pips * 0.1), "tp": current_bid - (self.tp_pips * 0.1)}
        return None

if __name__ == "__main__":
    logging.info("Ultra Pro Scalper V5 Initialized on GitHub.")
    send_telegram_alert("🟢 *Ultra Pro Scalper V5* bot successfully start ho gaya hai aur GitHub Actions par run kar raha hai!")
