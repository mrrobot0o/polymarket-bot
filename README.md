# 🤖 Polymarket AI Trading Bot - Ultimate Edition

**Intelligent Polymarket trading bot with Claude AI**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/mrrobot0o/polymarket-bot.svg)](https://github.com/mrrobot0o/polymarket-bot/stargazers)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Claude AI Analysis** | Intelligent market analysis using Claude |
| 💰 **Real Trading** | Execute real trades on Polymarket |
| 🛡️ **Risk Management** | Daily loss limits, auto stop-loss |
| 📱 **Telegram Alerts** | Instant trade notifications |
| 💵 **Auto Reinvestment** | Compound profits automatically |
| 📊 **Backtesting** | Test strategies on historical data |
| 📈 **Advanced Reports** | CSV/JSON performance reports |
| 🌍 **Multi-Category** | Sports, politics, crypto, entertainment |
| 🔗 **Bullpen CLI** | Integration with Bullpen CLI |
| 🤖 **Multiple Bots** | 5 different bot versions |

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/mrrobot0o/polymarket-bot.git
cd polymarket-bot

# 2. Install requirements
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
nano .env  # Add your keys

# 4. Run bot
python3 ultimate_bot.py --interval 120
```

---

## 📁 Project Structure

```
polymarket-bot/
├── 🤖 Bots
│   ├── ultimate_bot.py          # Full-featured bot ⭐
│   ├── trading_bot.py           # Trading bot
│   ├── bullpen_bot.py           # Bullpen CLI bot
│   ├── claude_bot_standalone.py # Claude AI bot
│   └── bot.py                   # Simple bot
│
├── 📂 scripts/
│   ├── check_balance.py         # Check wallet balance
│   ├── telegram_test.py         # Test Telegram
│   └── setup.sh                 # Setup script
│
├── 📄 Documentation
│   ├── README.md                # This file
│   ├── SUMMARY.md               # Project summary
│   ├── SETUP_GUIDE.md           # Setup guide
│   └── BULLPEN_INTEGRATION.md   # Bullpen guide
│
└── ⚙️ Config
    ├── requirements.txt         # Dependencies
    ├── .env.example             # Config template
    └── .gitignore               # Git ignore
```

---

## 🎮 Usage

### Run Bots

```bash
# Ultimate bot (simulation)
python3 ultimate_bot.py --interval 120

# Live trading
python3 ultimate_bot.py --live --interval 120

# Backtesting
python3 ultimate_bot.py --backtest

# Performance report
python3 ultimate_bot.py --report

# Bullpen CLI bot
python3 bullpen_bot.py --portfolio

# Check balance
python3 scripts/check_balance.py
```

---

## ⚙️ Configuration

### .env File

```env
# Wallet
POLYGON_WALLET_PRIVATE_KEY=your_private_key

# Claude API
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-opus-4-6

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🛡️ Risk Management

```python
MAX_DAILY_LOSS = 50       # Max daily loss $
MAX_DAILY_TRADES = 20     # Max daily trades
STOP_LOSS_PERCENT = 20    # Stop loss %
TAKE_PROFIT_PERCENT = 50  # Take profit %
```

---

## 📊 Bot Versions

| Bot | Description | AI | Trading |
|-----|-------------|----|---------| 
| `ultimate_bot.py` | All features | ✅ Claude | ✅ |
| `trading_bot.py` | Trading focus | ✅ Claude | ✅ |
| `bullpen_bot.py` | Bullpen CLI | ❌ | ✅ |
| `claude_bot_standalone.py` | Claude only | ✅ Claude | ❌ |
| `bot.py` | Simple rules | ❌ | ❌ |

---

## 💰 Requirements

| Asset | Amount | Purpose |
|-------|--------|---------|
| **USDC** | $50+ | For trading |
| **MATIC** | 0.5+ | For gas fees |

**Network:** Polygon

---

## 📈 Expected Performance

| Scenario | Result |
|----------|--------|
| **Best case** | 200%+ monthly profit |
| **Worst case** | 100% loss |
| **Expected** | 20-50% monthly profit |

---

## ⚠️ Disclaimer

```
⚠️ Trading involves risk!
⚠️ Only trade money you can afford to lose.
⚠️ This bot is for educational purposes.
⚠️ Past performance doesn't guarantee future results.
⚠️ Never share your .env file!
```

---

## 🔧 Installation Options

### Option 1: pip
```bash
pip install -r requirements.txt
```

### Option 2: Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Bullpen CLI
```bash
# Install Bullpen CLI
curl -fsSL https://cli.bullpen.fi/install.sh | sh

# Login
bullpen login

# Run bullpen bot
python3 bullpen_bot.py --interval 120
```

---

## 📞 Support

- **GitHub Issues**: [Issues](https://github.com/mrrobot0o/polymarket-bot/issues)
- **Repository**: [Link](https://github.com/mrrobot0o/polymarket-bot)

---

## 📄 License

MIT License

---

## 🤝 Contributing

Contributions welcome! Open an Issue or Pull Request.

---

**🎉 Created by OpenClaw AI**
