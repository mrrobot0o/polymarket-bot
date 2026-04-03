#!/bin/bash
# Setup Script - سكربت الإعداد

echo "🤖 Polymarket Bot Setup"
echo "========================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from example..."
    cp .env.example .env
    echo "⚠️ Please edit .env with your credentials!"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Add USDC and MATIC to your wallet"
echo "3. Run: python3 ultimate_bot.py --interval 120"
echo ""
