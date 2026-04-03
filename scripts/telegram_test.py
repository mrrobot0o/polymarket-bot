#!/usr/bin/env python3
"""
Telegram Notifier - إرسال إشعارات تيليجرام
"""

import httpx

def send_message(bot_token: str, chat_id: str, message: str) -> bool:
    """إرسال رسالة تيليجرام"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = httpx.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not token or not chat_id:
        print("❌ Telegram credentials not found in .env")
        print("Add to .env:")
        print("TELEGRAM_BOT_TOKEN=your_token")
        print("TELEGRAM_CHAT_ID=your_chat_id")
        exit(1)
    
    # Test message
    message = """
🤖 <b>Polymarket Bot</b>

✅ تم الاتصال بنجاح!

سأرسل لك إشعارات عند:
• صفقات جديدة
• فرص كبيرة
• تقارير يومية
"""
    
    if send_message(token, chat_id, message):
        print("✅ Telegram test successful!")
    else:
        print("❌ Telegram test failed!")
