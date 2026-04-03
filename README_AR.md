# Polymarket AI Trading Bot

## التثبيت السريع

```bash
# 1. استنساخ المشروع
git clone https://github.com/Polymarket/agents.git polymarket-bot
cd polymarket-bot

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إعداد الملف .env
cp .env.example .env
# عدّل .env بمفاتيحك

# 4. تشغيل البوت
python3 continuous_bot.py
```

## المتطلبات

- Python 3.9+
- محفظة Polygon مع USDC
- MATIC للـ gas fees

## الملفات

```
polymarket-bot/
├── continuous_bot.py   # البوت الرئيسي 24/7
├── rule_bot.py         # تحليل لمرة واحدة
├── .env                # المفاتيح (أنشئه)
├── requirements.txt    # المتطلبات
└── agents/             # المكتبات
```

## .env المطلوب

```env
POLYGON_WALLET_PRIVATE_KEY=مفتاح_محفظتك
ANTHROPIC_API_KEY=مفتاح_claude_اختياري
ANTHROPIC_BASE_URL=https://api.anthropic.com
```

## أوامر التشغيل

```bash
# تحليل فقط (تجريبي)
python3 continuous_bot.py

# تداول حقيقي
python3 continuous_bot.py --live

# تغيير الفاصل الزمني (ثواني)
python3 continuous_bot.py --interval 300
```
