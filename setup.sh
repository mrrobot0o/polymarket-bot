#!/bin/bash
# Polymarket Trading Bot - Setup Script
# شغل هذا السكريبت مرة واحدة فقط

set -e

echo "================================================"
echo "🤖 Polymarket Trading Bot - Setup"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 تثبيت المتطلبات..."
pip install --break-system-packages -q langchain langchain-community langchain-core langchain-anthropic python-dotenv requests web3 pydantic py-clob-client httpx

# Create directories
echo ""
echo "📁 إنشاء المجلدات..."
mkdir -p logs

# Create .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 إنشاء ملف .env..."
    cat > .env << 'ENVEOF'
POLYGON_WALLET_PRIVATE_KEY="ضع_مفتاح_محفظتك_هنا"
ANTHROPIC_API_KEY=""
ANTHROPIC_BASE_URL="https://api.anthropic.com"
TAVILY_API_KEY=""
NEWSAPI_API_KEY=""
ENVEOF
    echo "⚠️ عدّل ملف .env بمفتاح محفظتك!"
fi

# Make scripts executable
chmod +x continuous_bot.py rule_bot.py 2>/dev/null || true

echo ""
echo "================================================"
echo "✅ اكتمل التثبيت!"
echo "================================================"
echo ""
echo "الخطوات التالية:"
echo "1. عدّل .env بمفتاح محفظتك"
echo "2. أرسل USDC إلى المحفظة"
echo "3. شغل: python3 continuous_bot.py"
echo ""
echo "للتداول الحقيقي: python3 continuous_bot.py --live"
echo "================================================"
