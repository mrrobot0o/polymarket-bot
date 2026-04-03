#!/usr/bin/env python3
"""
Polymarket Bot with Bullpen CLI Integration
بوت Polymarket مدمج مع Bullpen CLI

Bullpen CLI: https://cli.bullpen.fi
"""

import os
import sys
import json
import time
import signal
import argparse
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

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
            logging.FileHandler(os.path.join(log_dir, 'bullpen_bot.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ============================================================================
# BULLPEN CLI WRAPPER
# ============================================================================

class BullpenCLI:
    """Wrapper for Bullpen CLI commands"""
    
    def __init__(self):
        self.installed = self._check_installation()
        if self.installed:
            logger.info("✅ Bullpen CLI found")
        else:
            logger.warning("⚠️ Bullpen CLI not found - installing...")
            self._install()
    
    def _check_installation(self) -> bool:
        """Check if bullpen is installed"""
        try:
            result = subprocess.run(
                ['bullpen', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _install(self):
        """Install Bullpen CLI"""
        try:
            logger.info("📥 Installing Bullpen CLI...")
            result = subprocess.run(
                'curl -fsSL https://cli.bullpen.fi/install.sh | sh',
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.installed = True
                logger.info("✅ Bullpen CLI installed")
            else:
                logger.error(f"❌ Installation failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Installation error: {e}")
    
    def run(self, command: str, json_output: bool = True) -> dict:
        """Run a bullpen command"""
        if not self.installed:
            return {'error': 'Bullpen CLI not installed'}
        
        cmd = ['bullpen'] + command.split()
        if json_output:
            cmd.append('--output')
            cmd.append('json')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                if json_output:
                    try:
                        return json.loads(result.stdout)
                    except:
                        return {'raw': result.stdout}
                return {'raw': result.stdout}
            else:
                return {'error': result.stderr}
        except Exception as e:
            return {'error': str(e)}
    
    # ========== MARKET DISCOVERY ==========
    
    def discover_markets(self, category: str = None) -> List[Dict]:
        """Discover trending markets"""
        cmd = 'polymarket discover'
        if category:
            cmd += f' --category {category}'
        
        result = self.run(cmd)
        if 'error' in result:
            logger.error(f"Discovery error: {result['error']}")
            return []
        
        return result if isinstance(result, list) else []
    
    def search_markets(self, query: str) -> List[Dict]:
        """Search for markets"""
        result = self.run(f'polymarket search "{query}"')
        if 'error' in result:
            return []
        return result if isinstance(result, list) else []
    
    def get_market(self, slug: str) -> Optional[Dict]:
        """Get market details"""
        result = self.run(f'polymarket market {slug}')
        if 'error' in result:
            return None
        return result
    
    # ========== TRADING ==========
    
    def buy(self, slug: str, outcome: str, amount: float, confirm: bool = False) -> dict:
        """Buy shares on a market"""
        cmd = f'polymarket buy "{slug}" "{outcome}" {amount}'
        if confirm:
            cmd += ' --yes'
        
        result = self.run(cmd, json_output=False)
        return result
    
    def sell(self, slug: str, outcome: str, amount: float, confirm: bool = False) -> dict:
        """Sell shares"""
        cmd = f'polymarket sell "{slug}" "{outcome}" {amount}'
        if confirm:
            cmd += ' --yes'
        
        result = self.run(cmd, json_output=False)
        return result
    
    def place_order(self, slug: str, outcome: str, amount: float, price: float, 
                    order_type: str = 'GTC') -> dict:
        """Place a limit order"""
        cmd = f'polymarket order create "{slug}" "{outcome}" {amount} {price} --type {order_type}'
        result = self.run(cmd, json_output=False)
        return result
    
    def cancel_orders(self, order_ids: List[str] = None) -> dict:
        """Cancel open orders"""
        if order_ids:
            cmd = f'polymarket order cancel {" ".join(order_ids)}'
        else:
            cmd = 'polymarket order cancel --all'
        
        result = self.run(cmd, json_output=False)
        return result
    
    # ========== PORTFOLIO ==========
    
    def get_balances(self) -> dict:
        """Get portfolio balances"""
        result = self.run('portfolio balances')
        return result
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        result = self.run('portfolio positions')
        if 'error' in result:
            return []
        return result if isinstance(result, list) else []
    
    def get_pnl(self) -> dict:
        """Get P&L summary"""
        result = self.run('portfolio pnl')
        return result
    
    # ========== SMART MONEY ==========
    
    def get_top_traders(self) -> List[Dict]:
        """Get top traders"""
        result = self.run('smart-money top')
        if 'error' in result:
            return []
        return result if isinstance(result, list) else []
    
    def follow_trader(self, address: str) -> dict:
        """Follow a trader"""
        result = self.run(f'smart-money follow {address}')
        return result
    
    # ========== COMMENTS ==========
    
    def get_comments(self, slug: str) -> List[Dict]:
        """Get market comments"""
        result = self.run(f'comments {slug}')
        if 'error' in result:
            return []
        return result if isinstance(result, list) else []
    
    def post_comment(self, slug: str, comment: str) -> dict:
        """Post a comment"""
        result = self.run(f'comments post {slug} "{comment}"', json_output=False)
        return result


# ============================================================================
# AI ANALYZER (Simple version)
# ============================================================================

class SimpleAnalyzer:
    """Simple market analyzer without external AI"""
    
    def analyze(self, market: Dict) -> Dict:
        """Analyze a market using rules"""
        try:
            question = market.get('question', '')
            yes_price = float(market.get('yes_price', 0.5))
            volume = float(market.get('volume', 0))
            
            edge = 0.0
            recommendation = 'SKIP'
            reasoning = ''
            
            # Contrarian strategy
            if yes_price < 0.10:
                edge = 0.20
                recommendation = 'BUY_YES'
                reasoning = 'سعر منخفض جداً - فرصة شراء'
            elif yes_price < 0.20:
                edge = 0.15
                recommendation = 'BUY_YES'
                reasoning = 'سعر منخفض - فرصة جيدة'
            elif yes_price > 0.90:
                edge = 0.20
                recommendation = 'BUY_NO'
                reasoning = 'سعر مرتفع جداً - فرصة بيع'
            elif yes_price > 0.80:
                edge = 0.15
                recommendation = 'BUY_NO'
                reasoning = 'سعر مرتفع - فرصة بيع'
            
            # Volume bonus
            if volume > 1_000_000:
                edge += 0.02
                reasoning += ' | حجم تداول عالي'
            
            return {
                'recommendation': recommendation,
                'confidence': min(edge * 100, 80),
                'edge': edge,
                'reasoning': reasoning
            }
        except Exception as e:
            return {
                'recommendation': 'SKIP',
                'confidence': 0,
                'edge': 0,
                'reasoning': f'خطأ: {str(e)}'
            }


# ============================================================================
# BULLPEN TRADING BOT
# ============================================================================

class BullpenBot:
    """Trading bot using Bullpen CLI"""
    
    def __init__(self, dry_run: bool = True, check_interval: int = 300):
        self.dry_run = dry_run
        self.check_interval = check_interval
        self.running = True
        self.cycle_count = 0
        
        self.bullpen = BullpenCLI()
        self.analyzer = SimpleAnalyzer()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info("🛑 Shutting down...")
        self.running = False
    
    def show_portfolio(self):
        """Show portfolio status"""
        logger.info("=" * 50)
        logger.info("💼 PORTFOLIO STATUS")
        logger.info("=" * 50)
        
        # Balances
        balances = self.bullpen.get_balances()
        if 'error' not in balances:
            logger.info(f"💰 Balances: {balances}")
        
        # Positions
        positions = self.bullpen.get_positions()
        if positions:
            logger.info(f"📊 Open positions: {len(positions)}")
            for pos in positions[:5]:
                logger.info(f"   • {pos.get('market', '?')}: {pos.get('outcome', '?')}")
        
        # PnL
        pnl = self.bullpen.get_pnl()
        if 'error' not in pnl:
            logger.info(f"📈 P&L: {pnl}")
    
    def run_cycle(self):
        """Run one analysis cycle"""
        self.cycle_count += 1
        
        logger.info("=" * 50)
        logger.info(f"🔄 Cycle {self.cycle_count} at {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 50)
        
        # Discover markets
        logger.info("🔍 Discovering markets...")
        markets = self.bullpen.discover_markets()
        
        if not markets:
            logger.warning("No markets found")
            return
        
        logger.info(f"📊 Found {len(markets)} trending markets")
        
        # Analyze top markets
        opportunities = []
        for i, market in enumerate(markets[:10]):
            slug = market.get('slug', '')
            question = market.get('question', '')[:50]
            
            logger.info(f"🔍 Analyzing {i+1}/10: {question}...")
            
            analysis = self.analyzer.analyze(market)
            
            if analysis['recommendation'] != 'SKIP' and analysis['edge'] >= 0.10:
                opportunities.append({
                    'market': market,
                    'slug': slug,
                    'question': market.get('question', ''),
                    'yes_price': float(market.get('yes_price', 0.5)),
                    'analysis': analysis
                })
        
        # Sort by edge
        opportunities.sort(key=lambda x: x['analysis']['edge'], reverse=True)
        
        if not opportunities:
            logger.info("❌ No opportunities found")
            return
        
        # Show top opportunities
        logger.info(f"✅ Found {len(opportunities)} opportunities!")
        for i, opp in enumerate(opportunities[:3]):
            logger.info(f"  {i+1}. {opp['question'][:40]}...")
            logger.info(f"     🎯 {opp['analysis']['recommendation']} | Edge: {opp['analysis']['edge']:.0%}")
            logger.info(f"     📝 {opp['analysis']['reasoning']}")
        
        # Execute best trade
        if opportunities and not self.dry_run:
            best = opportunities[0]
            outcome = 'Yes' if best['analysis']['recommendation'] == 'BUY_YES' else 'No'
            
            logger.info(f"⚡ Executing: {best['analysis']['recommendation']} on {best['slug']}")
            result = self.bullpen.buy(
                slug=best['slug'],
                outcome=outcome,
                amount=10,
                confirm=True
            )
            logger.info(f"📋 Result: {result}")
        else:
            logger.info(f"📝 DRY RUN: Would trade {opportunities[0]['slug']}")
        
        logger.info(f"✅ Cycle {self.cycle_count} complete")
    
    def run(self):
        """Main run loop"""
        logger.info("=" * 50)
        logger.info("🤖 POLYMARKET BOT with BULLPEN CLI")
        logger.info("=" * 50)
        logger.info(f"📍 Mode: {'DRY RUN' if self.dry_run else '🔴 LIVE'}")
        logger.info(f"⏱️  Interval: {self.check_interval}s")
        logger.info("=" * 50)
        
        # Show initial portfolio
        self.show_portfolio()
        
        while self.running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Cycle error: {e}")
            
            if self.running:
                logger.info(f"😴 Sleeping {self.check_interval}s...")
                time.sleep(self.check_interval)
        
        logger.info("🛑 Bot stopped")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Polymarket Bot with Bullpen CLI')
    parser.add_argument('--live', action='store_true', help='Enable live trading')
    parser.add_argument('--interval', type=int, default=300, help='Check interval')
    parser.add_argument('--portfolio', action='store_true', help='Show portfolio only')
    args = parser.parse_args()
    
    bot = BullpenBot(
        dry_run=not args.live,
        check_interval=args.interval
    )
    
    if args.portfolio:
        bot.show_portfolio()
    else:
        bot.run()


if __name__ == "__main__":
    main()
