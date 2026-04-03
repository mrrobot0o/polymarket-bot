#!/usr/bin/env python3
"""
Polymarket Telegram Bot
بوت تيليجرام للتحكم في التداول

Commands:
/start - بدء البوت
/balance - رصيد المحفظة
/markets - الأسواق الرائجة
/analyze <slug> - تحليل سوق
/buy <slug> <yes/no> <amount> - شراء
/sell <slug> <yes/no> <amount> - بيع
/positions - المراكز المفتوحة
/report - تقرير الأداء
/start_bot - تشغيل التداول التلقائي
/stop_bot - إيقاف التداول التلقائي
/settings - الإعدادات
/help - المساعدة
"""

import os
import sys
import json
import time
import asyncio
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("❌ Install httpx: pip install httpx")
    sys.exit(1)

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'telegram_bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", ""),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    "ANTHROPIC_BASE_URL": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
    "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6"),
    "POLYGON_WALLET_PRIVATE_KEY": os.getenv("POLYGON_WALLET_PRIVATE_KEY", ""),
    
    # Trading settings
    "MIN_EDGE": 0.10,
    "TRADE_SIZE": 10,
    "MAX_POSITIONS": 5,
    "AUTO_TRADING": False,
}

# Load from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    for key in CONFIG:
        if key in os.environ:
            CONFIG[key] = os.environ[key]
except:
    pass


# ============================================================================
# TELEGRAM API
# ============================================================================

class TelegramAPI:
    """Simple Telegram Bot API wrapper"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.commands = {}
    
    def register_command(self, command: str, handler):
        """Register a command handler"""
        self.commands[command] = handler
    
    async def request(self, method: str, data: dict = None) -> dict:
        """Make API request"""
        url = f"{self.base_url}/{method}"
        try:
            async with httpx.AsyncClient() as client:
                if data:
                    resp = await client.post(url, json=data, timeout=30)
                else:
                    resp = await client.get(url, timeout=30)
                return resp.json()
        except Exception as e:
            logger.error(f"Telegram API error: {e}")
            return {"ok": False, "error": str(e)}
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML"):
        """Send message"""
        await self.request("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })
    
    async def send_typing(self, chat_id: str):
        """Send typing indicator"""
        await self.request("sendChatAction", {
            "chat_id": chat_id,
            "action": "typing"
        })
    
    async def get_updates(self) -> List[dict]:
        """Get new updates"""
        data = {"offset": self.last_update_id + 1, "timeout": 30}
        result = await self.request("getUpdates", data)
        
        if result.get("ok"):
            updates = result.get("result", [])
            if updates:
                self.last_update_id = updates[-1]["update_id"]
            return updates
        return []
    
    async def set_commands(self):
        """Set bot commands"""
        commands = [
            {"command": "start", "description": "Start the bot"},
            {"command": "balance", "description": "Check wallet balance"},
            {"command": "markets", "description": "Trending markets"},
            {"command": "analyze", "description": "Analyze a market"},
            {"command": "buy", "description": "Buy shares"},
            {"command": "sell", "description": "Sell shares"},
            {"command": "positions", "description": "Open positions"},
            {"command": "report", "description": "Performance report"},
            {"command": "start_bot", "description": "Start auto trading"},
            {"command": "stop_bot", "description": "Stop auto trading"},
            {"command": "settings", "description": "Bot settings"},
            {"command": "help", "description": "Help"},
        ]
        await self.request("setMyCommands", {"commands": commands})


# ============================================================================
# POLYMARKET API
# ============================================================================

class PolymarketAPI:
    """Polymarket API client"""
    
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
    
    async def get_markets(self, limit: int = 10) -> List[dict]:
        """Get trending markets"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/markets",
                    params={"limit": limit, "active": "true"},
                    timeout=30
                )
                data = resp.json()
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    async def get_market(self, slug: str) -> Optional[dict]:
        """Get market by slug"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/markets",
                    params={"slug": slug},
                    timeout=30
                )
                data = resp.json()
                if isinstance(data, list) and data:
                    return data[0]
                return None
        except Exception as e:
            logger.error(f"Error fetching market: {e}")
            return None


# ============================================================================
# CLAUDE AI ANALYZER
# ============================================================================

class ClaudeAnalyzer:
    """Claude AI market analyzer"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    async def analyze(self, market: dict) -> dict:
        """Analyze market with Claude"""
        if not self.api_key:
            return self._simple_analysis(market)
        
        prompt = f"""Analyze this prediction market and return JSON only:

Market: {market.get('question', 'Unknown')}
Description: {market.get('description', 'No description')}
Current Yes Price: {float(market.get('outcome_prices', ['0.5', '0.5'])[0]):.1%}
Volume: ${float(market.get('volume', 0)):,.0f}

Return ONLY valid JSON:
{{"recommendation": "BUY_YES|BUY_NO|SKIP", "confidence": 0-100, "edge": 0.0-1.0, "reasoning": "brief reason"}}"""
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 200,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60
                )
                
                data = resp.json()
                content = data.get("content", [{}])[0].get("text", "{}")
                
                # Extract JSON
                import re
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    return json.loads(json_match.group())
                return self._simple_analysis(market)
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._simple_analysis(market)
    
    def _simple_analysis(self, market: dict) -> dict:
        """Simple rule-based analysis"""
        try:
            yes_price = float(market.get('outcome_prices', ['0.5', '0.5'])[0])
            
            if yes_price < 0.15:
                return {"recommendation": "BUY_YES", "confidence": 75, "edge": 0.20, "reasoning": "Very low price - contrarian opportunity"}
            elif yes_price > 0.85:
                return {"recommendation": "BUY_NO", "confidence": 75, "edge": 0.20, "reasoning": "Very high price - contrarian opportunity"}
            else:
                return {"recommendation": "SKIP", "confidence": 0, "edge": 0, "reasoning": "No clear edge"}
        except:
            return {"recommendation": "SKIP", "confidence": 0, "edge": 0, "reasoning": "Analysis error"}


# ============================================================================
# TELEGRAM BOT
# ============================================================================

class PolymarketTelegramBot:
    """Main Telegram bot"""
    
    def __init__(self, config: dict):
        self.config = config
        self.telegram = TelegramAPI(config["TELEGRAM_BOT_TOKEN"])
        self.polymarket = PolymarketAPI()
        self.analyzer = ClaudeAnalyzer(
            config["ANTHROPIC_API_KEY"],
            config["ANTHROPIC_BASE_URL"],
            config["ANTHROPIC_MODEL"]
        )
        
        self.auto_trading = False
        self.trading_task = None
        self.stats = {
            "trades": 0,
            "profit": 0,
            "started": datetime.now()
        }
        
        # Register commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all command handlers"""
        self.telegram.register_command("start", self.cmd_start)
        self.telegram.register_command("balance", self.cmd_balance)
        self.telegram.register_command("markets", self.cmd_markets)
        self.telegram.register_command("analyze", self.cmd_analyze)
        self.telegram.register_command("buy", self.cmd_buy)
        self.telegram.register_command("sell", self.cmd_sell)
        self.telegram.register_command("positions", self.cmd_positions)
        self.telegram.register_command("report", self.cmd_report)
        self.telegram.register_command("start_bot", self.cmd_start_bot)
        self.telegram.register_command("stop_bot", self.cmd_stop_bot)
        self.telegram.register_command("settings", self.cmd_settings)
        self.telegram.register_command("help", self.cmd_help)
    
    async def cmd_start(self, chat_id: str, args: List[str]):
        """Start command"""
        msg = """🤖 <b>Welcome to Polymarket Trading Bot!</b>

Available commands:
📊 /markets - Trending markets
💰 /balance - Wallet balance
🧠 /analyze <slug> - AI analysis
💵 /buy <slug> <yes/no> <amount> - Buy
💸 /sell <slug> <yes/no> <amount> - Sell
📈 /positions - Open positions
📉 /report - Performance report
🤖 /start_bot - Auto trading ON
⏹️ /stop_bot - Auto trading OFF
⚙️ /settings - Bot settings

Ready to trade! 🚀"""
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_balance(self, chat_id: str, args: List[str]):
        """Balance command"""
        await self.telegram.send_typing(chat_id)
        
        # Mock balance (replace with real API)
        msg = """💰 <b>Wallet Balance</b>

💵 USDC: $0.00
⛽ MATIC: 0.000
📍 Network: Polygon

⚠️ Fund your wallet to start trading!"""
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_markets(self, chat_id: str, args: List[str]):
        """Markets command"""
        await self.telegram.send_typing(chat_id)
        
        markets = await self.polymarket.get_markets(10)
        
        if not markets:
            await self.telegram.send_message(chat_id, "❌ No markets found")
            return
        
        msg = "📊 <b>Trending Markets</b>\n\n"
        
        for i, m in enumerate(markets[:8], 1):
            question = m.get('question', 'Unknown')[:40]
            try:
                yes_price = float(m.get('outcome_prices', ['0.5'])[0])
                price_str = f"{yes_price:.0%}"
            except:
                price_str = "?%"
            
            slug = m.get('slug', '')[:15]
            msg += f"{i}. {question}...\n"
            msg += f"   💵 Yes: {price_str} | 📝 {slug}\n\n"
        
        msg += "🧠 Use /analyze <slug> for AI analysis"
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_analyze(self, chat_id: str, args: List[str]):
        """Analyze command"""
        if not args:
            await self.telegram.send_message(chat_id, "❌ Usage: /analyze <market-slug>")
            return
        
        await self.telegram.send_typing(chat_id)
        
        slug = args[0]
        market = await self.polymarket.get_market(slug)
        
        if not market:
            await self.telegram.send_message(chat_id, f"❌ Market '{slug}' not found")
            return
        
        analysis = await self.analyzer.analyze(market)
        
        emoji = "🟢" if analysis['recommendation'] == "BUY_YES" else "🔴" if analysis['recommendation'] == "BUY_NO" else "⚪"
        
        msg = f"""🧠 <b>AI Analysis</b>

📊 Market: {market.get('question', 'Unknown')[:50]}
💵 Price: {float(market.get('outcome_prices', ['0.5'])[0]):.1%}

{emoji} <b>Recommendation: {analysis['recommendation']}</b>
🎯 Confidence: {analysis['confidence']}%
📈 Edge: {analysis['edge']:.0%}

📝 Reasoning:
{analysis['reasoning']}"""
        
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_buy(self, chat_id: str, args: List[str]):
        """Buy command"""
        if len(args) < 3:
            await self.telegram.send_message(chat_id, "❌ Usage: /buy <slug> <yes/no> <amount>")
            return
        
        slug, outcome, amount = args[0], args[1].upper(), args[2]
        
        if outcome not in ["YES", "NO"]:
            await self.telegram.send_message(chat_id, "❌ Outcome must be 'yes' or 'no'")
            return
        
        try:
            amount_float = float(amount)
        except:
            await self.telegram.send_message(chat_id, "❌ Invalid amount")
            return
        
        msg = f"""✅ <b>Trade Executed (DRY RUN)</b>

📊 Market: {slug}
💵 Outcome: {outcome}
💰 Amount: ${amount_float:.2f}

📝 Use /start_bot for live trading"""
        
        self.stats["trades"] += 1
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_sell(self, chat_id: str, args: List[str]):
        """Sell command"""
        if len(args) < 3:
            await self.telegram.send_message(chat_id, "❌ Usage: /sell <slug> <yes/no> <amount>")
            return
        
        slug, outcome, amount = args[0], args[1].upper(), args[2]
        
        msg = f"""✅ <b>Sell Order (DRY RUN)</b>

📊 Market: {slug}
💵 Outcome: {outcome}
💰 Amount: ${float(amount):.2f}"""
        
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_positions(self, chat_id: str, args: List[str]):
        """Positions command"""
        msg = """📈 <b>Open Positions</b>

No open positions.

Use /buy to open a position."""
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_report(self, chat_id: str, args: List[str]):
        """Report command"""
        uptime = datetime.now() - self.stats["started"]
        
        msg = f"""📊 <b>Performance Report</b>

⏰ Uptime: {str(uptime).split('.')[0]}
📈 Total Trades: {self.stats['trades']}
💰 Profit/Loss: ${self.stats['profit']:.2f}
🤖 Auto Trading: {'ON ✅' if self.auto_trading else 'OFF ❌'}

Trade Size: ${self.config['TRADE_SIZE']}
Min Edge: {self.config['MIN_EDGE']:.0%}"""
        
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_start_bot(self, chat_id: str, args: List[str]):
        """Start auto trading"""
        if self.auto_trading:
            await self.telegram.send_message(chat_id, "⚠️ Auto trading already running!")
            return
        
        self.auto_trading = True
        msg = """🤖 <b>Auto Trading Started!</b>

✅ Bot will analyze markets automatically
⏰ Interval: 2 minutes
💰 Trade size: $10

Use /stop_bot to stop."""
        
        await self.telegram.send_message(chat_id, msg)
        
        # Start trading loop
        self.trading_task = asyncio.create_task(self._auto_trading_loop(chat_id))
    
    async def cmd_stop_bot(self, chat_id: str, args: List[str]):
        """Stop auto trading"""
        self.auto_trading = False
        
        if self.trading_task:
            self.trading_task.cancel()
        
        msg = """⏹️ <b>Auto Trading Stopped</b>

Use /start_bot to resume."""
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_settings(self, chat_id: str, args: List[str]):
        """Settings command"""
        msg = f"""⚙️ <b>Bot Settings</b>

💰 Trade Size: ${self.config['TRADE_SIZE']}
📊 Min Edge: {self.config['MIN_EDGE']:.0%}
📈 Max Positions: {self.config['MAX_POSITIONS']}
🤖 Model: {self.config['ANTHROPIC_MODEL']}

To change settings, edit .env file."""
        await self.telegram.send_message(chat_id, msg)
    
    async def cmd_help(self, chat_id: str, args: List[str]):
        """Help command"""
        msg = """📚 <b>Help</b>

<b>Commands:</b>
/start - Start bot
/balance - Check balance
/markets - Trending markets
/analyze <slug> - AI analysis
/buy <slug> <yes/no> <amount> - Buy
/sell <slug> <yes/no> <amount> - Sell
/positions - Open positions
/report - Performance
/start_bot - Auto trade ON
/stop_bot - Auto trade OFF
/settings - Settings

<b>Tips:</b>
• Start with /markets to find opportunities
• Use /analyze for AI recommendations
• Test with DRY RUN first
• Always check /balance before trading"""
        await self.telegram.send_message(chat_id, msg)
    
    async def _auto_trading_loop(self, chat_id: str):
        """Auto trading loop"""
        while self.auto_trading:
            try:
                # Get markets
                markets = await self.polymarket.get_markets(10)
                
                if markets:
                    # Analyze top market
                    market = markets[0]
                    analysis = await self.analyzer.analyze(market)
                    
                    if analysis['edge'] >= self.config['MIN_EDGE']:
                        # Found opportunity
                        msg = f"""🔔 <b>Opportunity Found!</b>

📊 {market.get('question', 'Unknown')[:40]}
🎯 {analysis['recommendation']}
📈 Edge: {analysis['edge']:.0%}

{analysis['reasoning']}"""
                        await self.telegram.send_message(chat_id, msg)
                
                # Wait 2 minutes
                await asyncio.sleep(120)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto trading error: {e}")
                await asyncio.sleep(60)
    
    async def handle_update(self, update: dict):
        """Handle incoming update"""
        try:
            message = update.get("message", {})
            chat_id = str(message.get("chat", {}).get("id", ""))
            text = message.get("text", "")
            
            if not text or not text.startswith("/"):
                return
            
            # Parse command
            parts = text.split()
            command = parts[0].lower().replace("/", "")
            args = parts[1:] if len(parts) > 1 else []
            
            # Check auth
            allowed_chat = self.config.get("TELEGRAM_CHAT_ID", "")
            if allowed_chat and chat_id != allowed_chat:
                await self.telegram.send_message(chat_id, "⛔ Unauthorized")
                return
            
            # Execute command
            handler = self.telegram.commands.get(command)
            if handler:
                await handler(chat_id, args)
            else:
                await self.telegram.send_message(chat_id, f"❌ Unknown command: /{command}")
                
        except Exception as e:
            logger.error(f"Error handling update: {e}")
    
    async def run(self):
        """Run the bot"""
        logger.info("🤖 Starting Polymarket Telegram Bot...")
        
        # Set commands
        await self.telegram.set_commands()
        
        # Send startup message
        if self.config.get("TELEGRAM_CHAT_ID"):
            await self.telegram.send_message(
                self.config["TELEGRAM_CHAT_ID"],
                "🤖 <b>Polymarket Bot Online!</b>\n\nUse /help for commands."
            )
        
        logger.info("✅ Bot started - listening for messages...")
        
        # Main loop
        while True:
            try:
                updates = await self.telegram.get_updates()
                
                for update in updates:
                    await self.handle_update(update)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Bot error: {e}")
                await asyncio.sleep(5)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Polymarket Telegram Bot')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    parser.add_argument('--chat-id', type=str, help='Allowed chat ID')
    args = parser.parse_args()
    
    # Override config with args
    if args.token:
        CONFIG["TELEGRAM_BOT_TOKEN"] = args.token
    if args.chat_id:
        CONFIG["TELEGRAM_CHAT_ID"] = args.chat_id
    
    # Check token
    if not CONFIG["TELEGRAM_BOT_TOKEN"]:
        print("❌ TELEGRAM_BOT_TOKEN required!")
        print("\nSet it in .env or use --token")
        print("\nTo create a bot:")
        print("1. Open @BotFather on Telegram")
        print("2. Send /newbot")
        print("3. Copy the token")
        sys.exit(1)
    
    # Run bot
    bot = PolymarketTelegramBot(CONFIG)
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
