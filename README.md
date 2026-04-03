# 🤖 Polymarket Ultimate Trading Bot

بوت تداول Polymarket الذكي مع Claude AI

## ✨ الميزات

| الميزة | الوصف |
|--------|-------|
| 🧠 **Claude AI** | تحليل ذكي للأسواق باستخدام Claude |
| 💰 **تداول تلقائي** | تنفيذ صفقات حقيقية على Polymarket |
| 🛡️ **إدارة المخاطر** | حدود خسارة يومية، إيقاف تلقائي |
| 📱 **إشعار تيليجرام** | تنبيهات فورية لكل صفقة |
| 💵 **إعادة الاستثمار** | نمو مركب تلقائي |
| 📊 **Backtesting** | اختبار الاستراتيجية |
| 📈 **تقارير متقدمة** | CSV و JSON |

## 🚀 التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/YOUR_USERNAME/polymarket-bot.git
cd polymarket-bot

# تثبيت المتطلبات
pip install httpx python-dotenv web3 py_clob_client

# نسخ ملف الإعدادات
cp .env.example .env

# تعديل الإعدادات
nano .env
```

## ⚙️ الإعدادات

أنشئ ملف `.env`:

```env
POLYGON_WALLET_PRIVATE_KEY=your_private_key
ANTHROPIC_API_KEY=your_claude_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-6
```

## 🎮 التشغيل

```bash
# وضع المحاكاة (آمن)
python3 ultimate_bot.py --interval 120

# تداول حقيقي
python3 ultimate_bot.py --live --interval 120

# اختبار الاستراتيجية
python3 ultimate_bot.py --backtest

# توليد تقرير
python3 ultimate_bot.py --report
```

## 📁 الملفات

| الملف | الوصف |
|-------|-------|
| `ultimate_bot.py` | البوت الشامل بكل الميزات ⭐ |
| `trading_bot.py` | بوت التداول الأساسي |
| `claude_bot_standalone.py` | بوت Claude فقط |
| `bot.py` | بوت بسيط بدون AI |

## 🛡️ إدارة المخاطر

```python
MAX_DAILY_LOSS = 50      # أقصى خسارة يومية $
MAX_DAILY_TRADES = 20    # أقصى صفقات يومية
STOP_LOSS_PERCENT = 20   # إيقاف خسارة %
```

## 📱 تيليجرام

للتفعيل، أضف في الكود:

```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

## 💰 المتطلبات

- **USDC**: $50+ على شبكة Polygon
- **MATIC**: 0.5+ للـ gas fees

## ⚠️ تنبيه

```
التداول ينطوي على مخاطر!
لا تتداول بأموال لا تستطيع خسارتها.
هذا البوت للأغراض التعليمية.
```

## 📄 الرخصة

MIT License

---

**⚠️ لا تشارك ملف `.env` أبداً!**
