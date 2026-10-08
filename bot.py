import requests

def send_telegram_alert(message):
    TOKEN = "YAHAN_APNA_BOT_TOKEN_DAALIYE"
    CHAT_ID = "YAHAN_APNI_CHAT_ID_DAALIYE"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")

# Example usage jab signal mile:
# send_telegram_alert("🚨 *XAUUSD SMC Alert* \n\n🔹 *Action:* Buy Limit \n🔹 *Entry:* $2,350.00 \n🔹 *SL:* $2,338.00 \n🔹 *TP:* $2,386.00 (1:3 RRR)")
