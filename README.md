# 🤖 Polymarket AI Trading Bot - Ultimate Edition

**بوت تداول Polymarket الذكي مع Claude AI**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ الميزات

| الميزة | الوصف |
|--------|-------|
| 🧠 **Claude AI Analysis** | تحليل ذكي للأسواق باستخدام Claude |
| 💰 **Real Trading** | تداول حقيقي على Polymarket |
| 🛡️ **Risk Management** | إدارة مخاطر متقدمة |
| 📱 **Telegram Alerts** | إشعارات فورية |
| 💵 **Auto Reinvestment** | إعادة استثمار الأرباح |
| 📊 **Backtesting** | اختبار الاستراتيجية |
| 📈 **Advanced Reports** | تقارير CSV/JSON |
| 🌍 **Multi-Category** | رياضة، سياسة، كريبتو |

---

## 🚀 التثبيت السريع

```bash
# استنساخ المشروع
git clone https://github.com/mrrobot0o/polymarket-bot.git
cd polymarket-bot

# تثبيت المتطلبات
pip install -r requirements.txt

# نسخ الإعدادات
cp .env.example .env

# تعديل الإعدادات
nano .env
```

---

## ⚙️ الإعدادات

أنشئ ملف `.env`:

```env
# المحفظة
POLYGON_WALLET_PRIVATE_KEY=your_private_key_here

# Claude API
ANTHROPIC_API_KEY=your_claude_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-6
```

---

## 🎮 التشغيل

### بوت بسيط (قواعد فقط)
```bash
python3 bot.py --interval 120
```

### بوت Claude AI (تحليل ذكي)
```bash
python3 claude_bot_standalone.py --interval 120
```

### بوت التداول الكامل
```bash
python3 trading_bot.py --interval 120
```

### البوت الشامل (كل الميزات) ⭐
```bash
python3 ultimate_bot.py --interval 120
```

### تداول حقيقي
```bash
python3 ultimate_bot.py --live --interval 120
```

### اختبار الاستراتيجية
```bash
python3 ultimate_bot.py --backtest
```

### تقرير الأداء
```bash
python3 ultimate_bot.py --report
```

---

## 📁 هيكل المشروع

```
polymarket-bot/
├── ultimate_bot.py          # البوت الشامل ⭐
├── trading_bot.py           # بوت التداول
├── claude_bot_standalone.py # بوت Claude
├── bot.py                   # بوت بسيط
├── requirements.txt         # المتطلبات
├── .env.example             # نموذج الإعدادات
├── README.md                # الدليل الإنجليزي
├── README_AR.md             # الدليل العربي
├── SETUP_GUIDE.md           # دليل الإعداد
└── setup.sh                 # سكربت التثبيت
```

---

## 🛡️ إدارة المخاطر

```python
MAX_DAILY_LOSS = 50       # أقصى خسارة يومية $
MAX_DAILY_TRADES = 20     # أقصى صفقات يومية
STOP_LOSS_PERCENT = 20    # إيقاف خسارة %
TAKE_PROFIT_PERCENT = 50  # جني أرباح %
```

---

## 📱 إعدادات تيليجرام

```python
# في ultimate_bot.py
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

---

## 💰 المتطلبات

| العملة | المبلغ | السبب |
|--------|--------|-------|
| **USDC** | $50+ | للتداول |
| **MATIC** | 0.5+ | للـ gas fees |
| **الشبكة** | Polygon | مطلوبة |

---

## 📊 أمثلة على الاستخدام

### تحليل سوق
```
🧠 Claude Analysis:
Market: "Will GTA VI release before June 2026?"
Price: 1.4%
Recommendation: BUY_YES
Confidence: 85%
Edge: 22%
Reasoning: سعر منخفض جداً مقارنة بالتوقعات
```

### تنفيذ صفقة
```
⚡ LIVE TRADE: BUY_YES
💰 Size: $10.00
📊 Price: 1.4%
🧠 Edge: 22%
📝 Reason: فرصة كبيرة - سعر غير عادل
```

---

## ⚠️ تنبيه مهم

```
⚠️ التداول ينطوي على مخاطر!
⚠️ لا تتداول بأموال لا تستطيع خسارتها.
⚠️ هذا البوت للأغراض التعليمية.
⚠️ الأداء السابق لا يضمن النتائج المستقبلية.
```

---

## 📄 الرخصة

MIT License - استخدم بحرية!

---

## 🤝 المساهمة

المساهمات مرحب بها! افتح Issue أو Pull Request.

---

## 📞 الدعم

- **GitHub Issues**: [رابط المشكلات](https://github.com/mrrobot0o/polymarket-bot/issues)
- **Telegram**: تفعله من الإعدادات

---

**⚠️ لا تشارك ملف `.env` أبداً!**
