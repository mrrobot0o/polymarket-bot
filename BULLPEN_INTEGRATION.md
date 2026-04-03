# 🤖 Bullpen CLI Integration

## 📦 التثبيت

### 1️⃣ تثبيت Bullpen CLI:
```bash
# macOS
brew install bullpenfi/tap/bullpen

# Linux/Windows
curl -fsSL https://cli.bullpen.fi/install.sh | sh

# npm
npm install -g @bullpenfi/cli
```

### 2️⃣ تسجيل الدخول:
```bash
bullpen login
```

### 3️⃣ تثبيت AI Skills:
```bash
bullpen skill install
```

---

## 🎮 التشغيل

### عرض المحفظة:
```bash
python3 bullpen_bot.py --portfolio
```

### وضع المحاكاة:
```bash
python3 bullpen_bot.py --interval 120
```

### تداول حقيقي:
```bash
python3 bullpen_bot.py --live --interval 120
```

---

## 📋 أوامر Bullpen CLI

### الأسواق:
```bash
# اكتشاف الأسواق الرائجة
bullpen polymarket discover

# البحث عن سوق
bullpen polymarket search "bitcoin"

# تفاصيل سوق
bullpen polymarket market will-btc-hit-100k
```

### التداول:
```bash
# شراء
bullpen polymarket buy "will-btc-hit-100k" "Yes" 10 --yes

# بيع
bullpen polymarket sell "will-btc-hit-100k" "Yes" 5 --yes

# أمر محدود
bullpen polymarket order create "will-btc-hit-100k" "Yes" 10 0.65
```

### المحفظة:
```bash
# الأرصدة
bullpen portfolio balances

# المراكز
bullpen portfolio positions

# الأرباح/الخسائر
bullpen portfolio pnl
```

### المتداولين الناجحين:
```bash
# أفضل المتداولين
bullpen smart-money top

# متابعة متداول
bullpen smart-money follow 0x...
```

---

## 🌟 الميزات

| الميزة | الوصف |
|--------|-------|
| ✅ **AI Skills** | Claude Code يتاجر لك |
| ✅ **Trading** | شراء/بيع/أوامر محدودة |
| ✅ **Portfolio** | تتبع الأرصدة والمراكز |
| ✅ **Smart Money** | تتبع المتداولين الناجحين |
| ✅ **Comments** | قراءة ونشر التعليقات |
| ✅ **TUI** | واجهة تفاعلية |

---

## 🔗 روابط

- **الموقع**: https://cli.bullpen.fi
- **GitHub**: https://github.com/BullpenFi/bullpen-cli-releases
- **الدليل**: https://cli.bullpen.fi/#setup-4-steps
