# 🚀 Setup Guide

## 📋 Prerequisites

- Python 3.9+
- pip
- git

---

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/mrrobot0o/polymarket-bot.git
cd polymarket-bot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
nano .env
```

Add your configuration:

```env
# Wallet (required)
POLYGON_WALLET_PRIVATE_KEY=your_private_key_here

# Claude API (required for AI)
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-6

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 💰 Fund Your Wallet

### 1. Get Your Wallet Address

```bash
python3 scripts/check_balance.py
```

### 2. Send Funds

| Asset | Amount | Network |
|--------|--------|---------|
| **USDC** | $50+ | Polygon |
| **MATIC** | 0.5+ | Polygon |

### 3. Verify Balance

```bash
python3 scripts/check_balance.py
```

---

## 🎮 Run the Bot

### Simulation Mode (Safe)

```bash
python3 ultimate_bot.py --interval 120
```

### Live Trading

```bash
python3 ultimate_bot.py --live --interval 120
```

---

## 📱 Setup Telegram (Optional)

### 1. Create Bot

1. Open @BotFather on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy the token

### 2. Get Chat ID

1. Message your bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find your chat_id

### 3. Test

```bash
python3 scripts/telegram_test.py
```

---

## 🔗 Bullpen CLI Setup (Optional)

### 1. Install Bullpen CLI

```bash
# macOS
brew install bullpenfi/tap/bullpen

# Linux/Windows
curl -fsSL https://cli.bullpen.fi/install.sh | sh
```

### 2. Login

```bash
bullpen login
```

### 3. Install AI Skills

```bash
bullpen skill install
```

### 4. Run Bullpen Bot

```bash
python3 bullpen_bot.py --interval 120
```

---

## ✅ Verify Installation

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep -E "httpx|web3|anthropic"

# Check configuration
cat .env

# Test run
python3 ultimate_bot.py --interval 60
```

---

## 🛠️ Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "Insufficient balance"
```bash
# Check your balance
python3 scripts/check_balance.py

# Add more USDC/MATIC to your wallet
```

### "API error"
```bash
# Check your API keys
cat .env | grep API_KEY
```

---

## 📞 Need Help?

- **GitHub Issues**: [Issues](https://github.com/mrrobot0o/polymarket-bot/issues)
- **Documentation**: See README.md

---

**🎉 You're ready to trade!**
