# 🤖 Polymarket AI Trading Bot - Complete Project

## 📦 التحميل والتثبيت

### الطريقة 1: من GitHub (الأصل)
```bash
git clone https://github.com/Polymarket/agents.git polymarket-bot
cd polymarket-bot
```

### الطريقة 2: استخدام الملفات الجاهزة

## 📋 الملفات المطلوبة

### 1. `.env` (المفاتيح)
```env
POLYGON_WALLET_PRIVATE_KEY="0x..."   # مفتاح محفظتك
ANTHROPIC_API_KEY=""                  # اختياري - للـ AI
ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

### 2. `requirements.txt`
```
langchain>=0.2.0
langchain-community>=0.2.0
langchain-core>=0.2.0
langchain-anthropic>=0.3.0
python-dotenv>=1.0.0
requests>=2.28.0
httpx>=0.24.0
web3>=6.0.0
pydantic>=2.0.0
py-clob-client>=0.17.0
chromadb>=0.5.0
sentence-transformers>=2.2.0
```

### 3. الملفات الرئيسية

- `standalone_bot.py` - البوت المستقل الكامل
- `continuous_bot.py` - البوت 24/7
- `rule_bot.py` - تحليل لمرة واحدة
- `agents/` - مجلد المكتبات

## 🚀 التثبيت السريع

```bash
# 1. إنشاء المجلد
mkdir polymarket-bot && cd polymarket-bot

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. إنشاء .env
nano .env  # ضع مفتاح محفظتك

# 4. تشغيل
python3 standalone_bot.py
```

## ⚙️ التشغيل

```bash
# تحليل تجريبي
python3 standalone_bot.py

# تداول حقيقي
python3 standalone_bot.py --live

# تغيير الإعدادات
python3 standalone_bot.py --interval 300 --min-volume 50000
```

## 📊 المخرجات

- `logs/bot.log` - سجل النشاط
- `last_analysis.json` - آخر تحليل
- `trade_history.json` - سجل الصفقات

## ⚠️ المتطلبات

1. **Python 3.9+**
2. **محفظة Polygon** مع:
   - USDC للتداول
   - MATIC للـ gas
3. **مفتاح المحفظة الخاص**

## 🔒 الأمان

- لا تشارك مفتاح محفظتك
- ابدأ بمبلغ صغير
- راقب البوت بانتظام
