#!/usr/bin/env python3
"""
Polymarket Trading Bot with Claude AI Analysis - STANDALONE VERSION
بوت تداول Polymarket مع تحليل Claude الذكي - نسخة مستقلة

Usage:
    python3 claude_bot_standalone.py                    # DRY RUN + Claude
    python3 claude_bot_standalone.py --live             # LIVE TRADING
    python3 claude_bot_standalone.py --interval 120     # كل 2 دقيقة
"""

import os
import sys
import json
import time
import signal
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# HTTP client
try:
    import httpx
except ImportError:
    print("❌ Install httpx: pip install httpx")
    sys.exit(1)

# Setup logging
def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'claude_bot.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ============================================================================
# CONFIGURATION - عدل هنا
# ============================================================================

CONFIG = {
    # المحفظة
    "WALLET_PRIVATE_KEY": "3969a19a1a639a76c0cea7dfffdcab2d0ae41b065cf0abf9ea23bd6e08bf6fd6",
    
    # Claude API
    "CLAUDE_API_KEY": "sk-3f061db1d058f8b7506f1911032775961bc5e0f86f17272c",
    "CLAUDE_BASE_URL": "https://api.ecomagent.in",
    "CLAUDE_MODEL": "claude-opus-4.6",
}


# ============================================================================
# CLAUDE AI ANALYZER
# ============================================================================

class ClaudeAnalyzer:
    """Analyze markets using Claude AI"""
    
    def __init__(self):
        self.api_key = CONFIG["CLAUDE_API_KEY"]
        self.base_url = CONFIG["CLAUDE_BASE_URL"]
        self.model = CONFIG["CLAUDE_MODEL"]
        self.enabled = True
        logger.info(f"🧠 Claude AI enabled: {self.model}")
        logger.info(f"🌐 API URL: {self.base_url}")
    
    def analyze_market(self, market: Dict) -> Dict:
        """
        Analyze a market using Claude AI
        
        Returns: {
            'recommendation': 'BUY_YES' | 'BUY_NO' | 'SKIP',
            'confidence': 0-100,
            'reasoning': str,
            'edge': float
        }
        """
        try:
            question = market.get('question', 'Unknown')
            description = market.get('description', '')[:500]
            
            # Parse prices
            raw_prices = market.get('outcomePrices', '[0.5, 0.5]')
            if isinstance(raw_prices, str):
                prices = json.loads(raw_prices)
            else:
                prices = raw_prices
            
            yes_price = float(prices[0]) if prices and prices[0] else 0.5
            volume = float(market.get('volume', 0) or 0)
            liquidity = float(market.get('liquidity', 0) or 0)
            
            # Create prompt for Claude
            prompt = f"""أنت محلل أسواق تداول خبير. حلل هذا السوق وأعطني توصية.

السوق: {question}

الوصف: {description[:300] if description else 'لا يوجد وصف'}

البيانات الحالية:
- سعر YES: {yes_price:.1%}
- سعر NO: {1-yes_price:.1%}
- حجم التداول: ${volume:,.0f}
- السيولة: ${liquidity:,.0f}

أجب بصيغة JSON فقط:
{{
    "recommendation": "BUY_YES" أو "BUY_NO" أو "SKIP",
    "confidence": رقم من 0 إلى 100,
    "reasoning": "سبب التوصية بالعربية",
    "edge": رقم من 0 إلى 50 (النسبة المئوية للميزة المتوقعة)
}}

قواعد:
1. BUY_YES إذا كان السعر أقل من القيمة الحقيقية المتوقعة
2. BUY_NO إذا كان السعر أعلى من القيمة الحقيقية المتوقعة
3. SKIP إذا لم تكن هناك ميزة واضحة
4. اعتبر حجم التداول والسيولة في قرارك

أجب بـ JSON فقط، بدون شرح إضافي."""

            # Call Claude API
            api_url = f"{self.base_url}/v1/messages"
            
            response = httpx.post(
                api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 500,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [{}])[0].get('text', '{}')
                
                # Extract JSON from response
                try:
                    if '{' in content:
                        json_start = content.index('{')
                        json_end = content.rindex('}') + 1
                        json_str = content[json_start:json_end]
                        result = json.loads(json_str)
                        
                        logger.info(f"🧠 Claude: {result.get('recommendation')} ({result.get('confidence')}%)")
                        
                        return {
                            'recommendation': result.get('recommendation', 'SKIP'),
                            'confidence': float(result.get('confidence', 0)),
                            'reasoning': result.get('reasoning', ''),
                            'edge': float(result.get('edge', 0)) / 100
                        }
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Failed to parse Claude response: {e}")
                    logger.error(f"Response: {content[:200]}")
            else:
                logger.error(f"Claude API error: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
        
        # Fallback to rule-based
        return self._rule_based_analysis(market)
    
    def _rule_based_analysis(self, market: Dict) -> Dict:
        """Fallback rule-based analysis"""
        try:
            raw_prices = market.get('outcomePrices', '[0.5, 0.5]')
            if isinstance(raw_prices, str):
                prices = json.loads(raw_prices)
            else:
                prices = raw_prices
            
            yes_price = float(prices[0]) if prices and prices[0] else 0.5
            volume = float(market.get('volume', 0) or 0)
            
            edge = 0.0
            recommendation = 'SKIP'
            reasoning = ''
            
            # Contrarian strategy
            if yes_price < 0.10:
                edge = 0.22
                recommendation = 'BUY_YES'
                reasoning = 'سعر منخفض جداً - فرصة للشراء'
            elif yes_price < 0.20:
                edge = 0.15
                recommendation = 'BUY_YES'
                reasoning = 'سعر منخفض - فرصة جيدة'
            elif yes_price > 0.90:
                edge = 0.22
                recommendation = 'BUY_NO'
                reasoning = 'سعر مرتفع جداً - فرصة للبيع'
            elif yes_price > 0.80:
                edge = 0.15
                recommendation = 'BUY_NO'
                reasoning = 'سعر مرتفع - فرصة للبيع'
            
            # Volume bonus
            if volume > 1_000_000:
                edge += 0.02
            
            return {
                'recommendation': recommendation,
                'confidence': min(edge * 100, 80),
                'reasoning': reasoning,
                'edge': edge
            }
            
        except Exception as e:
            return {
                'recommendation': 'SKIP',
                'confidence': 0,
                'reasoning': f'خطأ في التحليل: {str(e)}',
                'edge': 0
            }


# ============================================================================
# POLYMARKET API CLIENT
# ============================================================================

class PolymarketAPI:
    """Simple Polymarket API client"""
    
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com"
        
    def get_markets(self, limit: int = 100, min_volume: float = 0) -> List[Dict]:
        """Get active markets from Polymarket"""
        try:
            params = {
                "active": "true",
                "closed": "false", 
                "archived": "false",
                "limit": limit
            }
            
            response = httpx.get(f"{self.gamma_url}/markets", params=params, timeout=30)
            
            if response.status_code == 200:
                markets = response.json()
                
                if min_volume > 0:
                    markets = [m for m in markets 
                              if float(m.get('volume', 0) or 0) >= min_volume]
                
                return markets
            else:
                logger.error(f"API error: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []


# ============================================================================
# TRADING BOT WITH CLAUDE
# ============================================================================

class ClaudeTradingBot:
    """24/7 Trading Bot with Claude AI Analysis"""
    
    def __init__(self, dry_run: bool = True, check_interval: int = 300):
        self.dry_run = dry_run
        self.check_interval = check_interval
        self.running = True
        self.cycle_count = 0
        
        self.api = PolymarketAPI()
        self.claude = ClaudeAnalyzer()
        self.trade_history = []
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def fetch_and_analyze(self, min_volume: float, max_analyze: int = 10) -> List[Dict]:
        """Fetch markets and analyze with Claude"""
        markets = self.api.get_markets(limit=100, min_volume=min_volume)
        logger.info(f"📊 Found {len(markets)} markets")
        
        opportunities = []
        
        # Analyze top markets by volume
        sorted_markets = sorted(markets, key=lambda m: float(m.get('volume', 0) or 0), reverse=True)
        
        for i, market in enumerate(sorted_markets[:max_analyze]):
            logger.info(f"🔍 Analyzing {i+1}/{max_analyze}: {market.get('question', '?')[:40]}...")
            
            analysis = self.claude.analyze_market(market)
            
            if analysis['recommendation'] != 'SKIP' and analysis['edge'] >= 0.05:
                # Parse prices
                raw_prices = market.get('outcomePrices', '[0.5, 0.5]')
                if isinstance(raw_prices, str):
                    prices = json.loads(raw_prices)
                else:
                    prices = raw_prices
                yes_price = float(prices[0]) if prices and prices[0] else 0.5
                
                opportunities.append({
                    'market': market,
                    'edge': analysis['edge'],
                    'yes_price': yes_price,
                    'action': analysis['recommendation'],
                    'confidence': analysis['confidence'],
                    'reasoning': analysis['reasoning'],
                    'question': market.get('question', '?')[:60],
                    'volume': float(market.get('volume', 0) or 0)
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Sort by edge
        opportunities.sort(key=lambda x: x['edge'], reverse=True)
        return opportunities
    
    def log_trade(self, opportunity: Dict):
        """Log a trade"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.cycle_count,
            'question': opportunity['question'],
            'action': opportunity['action'],
            'price': opportunity['yes_price'],
            'edge': opportunity['edge'],
            'confidence': opportunity['confidence'],
            'reasoning': opportunity['reasoning'],
            'volume': opportunity['volume'],
            'dry_run': self.dry_run
        }
        
        self.trade_history.append(record)
        
        try:
            with open('trade_history.json', 'a') as f:
                f.write(json.dumps(record) + '\n')
        except:
            pass
        
        mode = "📝 DRY RUN" if self.dry_run else "⚡ LIVE"
        logger.info(f"{mode}: {opportunity['action']} on '{opportunity['question']}...'")
        logger.info(f"   🧠 السبب: {opportunity['reasoning']}")
    
    def run_cycle(self, min_volume: float, max_analyze: int = 10):
        """Run one analysis cycle"""
        self.cycle_count += 1
        
        logger.info("=" * 60)
        logger.info(f"🔄 Cycle {self.cycle_count} at {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        opportunities = self.fetch_and_analyze(min_volume, max_analyze)
        
        if not opportunities:
            logger.info("No opportunities found")
            return
        
        logger.info(f"Found {len(opportunities)} opportunities with Claude AI!")
        
        # Show top 5
        for i, opp in enumerate(opportunities[:5]):
            logger.info(f"  {i+1}. {opp['question']}...")
            logger.info(f"     🧠 {opp['action']} | Edge: {opp['edge']:.0%} | Confidence: {opp['confidence']:.0f}%")
            logger.info(f"     📝 {opp['reasoning'][:60]}...")
        
        # Execute best trade
        if opportunities and opportunities[0]['edge'] >= 0.10:
            self.log_trade(opportunities[0])
        
        # Save analysis
        self._save_analysis(opportunities)
        
        logger.info(f"✅ Cycle {self.cycle_count} complete")
    
    def _save_analysis(self, opportunities: List[Dict]):
        """Save analysis results"""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'opportunities_found': len(opportunities),
                'top_picks': [{
                    'question': o['question'],
                    'action': o['action'],
                    'edge': f"{o['edge']:.0%}",
                    'confidence': f"{o['confidence']:.0f}%",
                    'reasoning': o['reasoning'],
                    'price': f"{o['yes_price']:.1%}",
                    'volume': f"${o['volume']:,.0f}"
                } for o in opportunities[:10]]
            }
            
            with open('claude_analysis.json', 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
    
    def run(self, min_volume: float = 10000, max_analyze: int = 10):
        """Main run loop"""
        logger.info("=" * 60)
        logger.info("🤖 POLYMARKET TRADING BOT with CLAUDE AI")
        logger.info("=" * 60)
        logger.info(f"📍 Mode: {'DRY RUN (simulation)' if self.dry_run else '🔴 LIVE TRADING'}")
        logger.info(f"🧠 Claude AI: ✅ Enabled")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        logger.info(f"💰 Min volume: ${min_volume:,.0f}")
        logger.info(f"📊 Markets to analyze per cycle: {max_analyze}")
        logger.info("=" * 60)
        
        while self.running:
            try:
                self.run_cycle(min_volume, max_analyze)
            except Exception as e:
                logger.error(f"Cycle error: {e}")
            
            if self.running:
                logger.info(f"😴 Sleeping {self.check_interval}s until next cycle...")
                time.sleep(self.check_interval)
        
        logger.info("🛑 Bot stopped")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Polymarket Trading Bot with Claude AI')
    parser.add_argument('--live', action='store_true', help='Enable live trading')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--min-volume', type=float, default=10000, help='Minimum market volume')
    parser.add_argument('--max-analyze', type=int, default=10, help='Max markets to analyze per cycle')
    args = parser.parse_args()
    
    bot = ClaudeTradingBot(
        dry_run=not args.live,
        check_interval=args.interval
    )
    
    bot.run(min_volume=args.min_volume, max_analyze=args.max_analyze)


if __name__ == "__main__":
    main()
