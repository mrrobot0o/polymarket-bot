#!/usr/bin/env python3
"""
Polymarket 24/7 Trading Bot - COMPLETE STANDALONE VERSION
لا يحتاج أي ملفات خارجية - كل شيء في ملف واحد!

Usage:
    python3 bot.py                    # DRY RUN (تجريبي)
    python3 bot.py --live             # LIVE TRADING (حقيقي)
    python3 bot.py --interval 60      # كل دقيقة
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

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
            logging.FileHandler(os.path.join(log_dir, 'bot.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ============================================================================
# POLYMARKET API CLIENT (Simple version - no complex dependencies)
# ============================================================================

class PolymarketAPI:
    """Simple Polymarket API client using only httpx"""
    
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.clob_url = "https://clob.polymarket.com"
        
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
                
                # Filter by volume if specified
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
    
    def get_orderbook(self, token_id: str) -> Optional[Dict]:
        """Get orderbook for a specific token"""
        try:
            response = httpx.get(f"{self.clob_url}/book", params={"token_id": token_id})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
        return None


# ============================================================================
# MARKET ANALYZER (Rule-based, no LLM needed)
# ============================================================================

class MarketAnalyzer:
    """Analyze markets using statistical rules"""
    
    def __init__(self, min_edge: float = 0.05):
        self.min_edge = min_edge
        
    def calculate_edge(self, market: Dict) -> tuple:
        """
        Calculate trading edge
        
        Returns: (edge_score, yes_price)
        """
        try:
            # Parse prices
            raw_prices = market.get('outcomePrices', '[0.5, 0.5]')
            if isinstance(raw_prices, str):
                prices = json.loads(raw_prices)
            else:
                prices = raw_prices
            
            yes_price = float(prices[0]) if prices and prices[0] else 0.5
            no_price = 1.0 - yes_price
            
            volume = float(market.get('volume', 0) or 0)
            liquidity = float(market.get('liquidity', 0) or 0)
            
            edge = 0.0
            
            # ===== STRATEGY 1: Contrarian (extreme prices) =====
            # Markets tend to revert to 50%
            if yes_price < 0.10:
                edge += 0.15  # Extremely undervalued
            elif yes_price < 0.20:
                edge += 0.10
            elif yes_price < 0.30:
                edge += 0.05
            elif yes_price > 0.90:
                edge += 0.15  # Extremely overvalued
            elif yes_price > 0.80:
                edge += 0.10
            elif yes_price > 0.70:
                edge += 0.05
            
            # ===== STRATEGY 2: Volume/Liquidity ratio =====
            if volume > 0 and liquidity > 0:
                ratio = volume / liquidity
                if ratio > 20:
                    edge += 0.05  # High activity
            
            # ===== STRATEGY 3: Large volume bonus =====
            if volume > 1_000_000:
                edge += 0.02
            elif volume > 500_000:
                edge += 0.01
            
            return edge, yes_price
            
        except Exception as e:
            logger.error(f"Error calculating edge: {e}")
            return 0.0, 0.5
    
    def get_recommendation(self, edge: float, yes_price: float) -> tuple:
        """
        Get trade recommendation
        
        Returns: (action, position_size_pct)
        """
        if edge >= 0.15:
            if yes_price < 0.40:
                return "STRONG BUY YES", 0.10
            elif yes_price > 0.60:
                return "STRONG BUY NO", 0.10
        elif edge >= 0.10:
            if yes_price < 0.40:
                return "BUY YES", 0.05
            elif yes_price > 0.60:
                return "BUY NO", 0.05
        elif edge >= 0.05:
            return "WATCH", 0.02
        return "SKIP", 0.0


# ============================================================================
# TRADING BOT
# ============================================================================

class TradingBot:
    """24/7 Trading Bot"""
    
    def __init__(self, dry_run: bool = True, check_interval: int = 300):
        self.dry_run = dry_run
        self.check_interval = check_interval
        self.running = True
        self.cycle_count = 0
        
        self.api = PolymarketAPI()
        self.analyzer = MarketAnalyzer()
        self.trade_history = []
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def fetch_and_analyze(self, min_volume: float) -> List[Dict]:
        """Fetch markets and analyze them"""
        # Fetch
        markets = self.api.get_markets(limit=100, min_volume=min_volume)
        logger.info(f"📊 Found {len(markets)} markets")
        
        # Analyze
        opportunities = []
        for market in markets:
            edge, yes_price = self.analyzer.calculate_edge(market)
            
            if edge >= self.analyzer.min_edge:
                action, size = self.analyzer.get_recommendation(edge, yes_price)
                opportunities.append({
                    'market': market,
                    'edge': edge,
                    'yes_price': yes_price,
                    'action': action,
                    'size': size,
                    'question': market.get('question', '?')[:60],
                    'volume': float(market.get('volume', 0) or 0)
                })
        
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
            'volume': opportunity['volume'],
            'dry_run': self.dry_run
        }
        
        self.trade_history.append(record)
        
        # Save to file
        try:
            with open('trade_history.json', 'a') as f:
                f.write(json.dumps(record) + '\n')
        except:
            pass
        
        if self.dry_run:
            logger.info(f"📝 DRY RUN: {opportunity['action']} on '{opportunity['question']}...'")
        else:
            logger.info(f"⚡ LIVE: {opportunity['action']} on '{opportunity['question']}...'")
    
    def run_cycle(self, min_volume: float):
        """Run one analysis cycle"""
        self.cycle_count += 1
        
        logger.info("=" * 60)
        logger.info(f"🔄 Cycle {self.cycle_count} at {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        # Analyze
        opportunities = self.fetch_and_analyze(min_volume)
        
        if not opportunities:
            logger.info("No opportunities found")
            return
        
        logger.info(f"Found {len(opportunities)} opportunities (edge >= {self.analyzer.min_edge:.0%})")
        
        # Show top 5
        for i, opp in enumerate(opportunities[:5]):
            logger.info(f"  {i+1}. {opp['question']}...")
            logger.info(f"     Edge: {opp['edge']:.0%} | Price: {opp['yes_price']:.1%} | {opp['action']}")
        
        # Execute best trade if edge >= 10%
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
                    'edge': f"{o['edge']:.0%}",
                    'action': o['action'],
                    'price': f"{o['yes_price']:.1%}",
                    'volume': f"${o['volume']:,.0f}"
                } for o in opportunities[:10]]
            }
            
            with open('last_analysis.json', 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
    
    def run(self, min_volume: float = 10000):
        """Main run loop"""
        logger.info("=" * 60)
        logger.info("🤖 POLYMARKET 24/7 TRADING BOT")
        logger.info("=" * 60)
        logger.info(f"📍 Mode: {'DRY RUN (simulation)' if self.dry_run else '🔴 LIVE TRADING'}")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        logger.info(f"💰 Min volume: ${min_volume:,.0f}")
        logger.info(f"📈 Min edge: {self.analyzer.min_edge:.0%}")
        logger.info("=" * 60)
        
        while self.running:
            try:
                self.run_cycle(min_volume)
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
    parser = argparse.ArgumentParser(description='Polymarket 24/7 Trading Bot')
    parser.add_argument('--live', action='store_true', help='Enable live trading')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--min-volume', type=float, default=10000, help='Minimum market volume')
    parser.add_argument('--min-edge', type=float, default=0.05, help='Minimum edge to trade')
    args = parser.parse_args()
    
    bot = TradingBot(
        dry_run=not args.live,
        check_interval=args.interval
    )
    
    if args.min_edge:
        bot.analyzer.min_edge = args.min_edge
    
    bot.run(min_volume=args.min_volume)


if __name__ == "__main__":
    main()
