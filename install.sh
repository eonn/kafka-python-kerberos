#!/bin/bash
# Author: Eon (Himanshu Shekhar)
# Created: 2025-08-15
# Description: Installation script for Kafka Python utility with Kerberos
# License: MIT
# Repository: https://github.com/eonn/kafka-python-kerberos
"""
Installation script for Kafka Kerberos Utility

This script sets up the environment and installs dependencies for the Kafka utility.
"""

set -e

echo "🚀 Installing Kafka Kerberos Utility"
echo "====================================="

# Check if Python 3.7+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "🔧 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y libkrb5-dev libsasl2-dev libssl-dev krb5-config
    echo "✅ System dependencies installed"
else
    echo "⚠️  Please install system dependencies manually:"
    echo "   - libkrb5-dev"
    echo "   - libsasl2-dev" 
    echo "   - libssl-dev"
    echo "   - krb5-config"
fi

# Optional: Install gssapi for full Kerberos support
echo "🔐 Installing GSSAPI support (optional)..."
if pip install gssapi; then
    echo "✅ GSSAPI installed successfully"
else
    echo "⚠️  GSSAPI installation failed. The utility will work with limited Kerberos support."
    echo "   You can try installing it manually later with: pip install gssapi"
fi

# Run tests
echo "🧪 Running tests..."
python test_utility.py

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy env.example to .env and configure your Kafka settings:"
echo "   cp env.example .env"
echo ""
echo "2. Edit .env with your actual configuration:"
echo "   - KAFKA_BOOTSTRAP_SERVERS"
echo "   - KAFKA_TOPIC"
echo "   - KAFKA_KEYTAB_PATH"
echo "   - KAFKA_PRINCIPAL"
echo ""
echo "3. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Run the example:"
echo "   python example_usage.py"
echo ""
echo "📚 For more information, see README.md"
