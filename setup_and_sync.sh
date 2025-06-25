#!/bin/bash

# Meraki NetBox Sync - Setup and Run Script
# This script handles installation of dependencies and runs the sync process

set -e  # Exit on any error

echo "🚀 Meraki NetBox Sync - Setup and Run"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python 3
if ! command_exists python3; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for pip3
if ! command_exists pip3; then
    echo "❌ Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API credentials:"
    echo ""
    echo "MERAKI_API_KEY=your_meraki_api_key_here"
    echo "NETBOX_URL=https://your-netbox-instance.com"
    echo "NETBOX_TOKEN=your_netbox_token_here"
    echo ""
    echo "Example .env file:"
    cat << 'EOF'
# Meraki API Configuration
MERAKI_API_KEY=1234567890abcdef1234567890abcdef12345678

# NetBox API Configuration
NETBOX_URL=https://netbox.example.com
NETBOX_TOKEN=abcdef1234567890abcdef1234567890abcdef12
EOF
    echo ""
    read -p "Press Enter to continue once you've created the .env file, or Ctrl+C to exit..."
fi

echo ""
echo "🔧 Environment file check complete"

# Parse command line arguments
SYNC_ARGS=""
if [ $# -gt 0 ]; then
    SYNC_ARGS="$@"
fi

# Run the sync
echo ""
echo "🔄 Starting Meraki NetBox synchronization..."
echo "Arguments: $SYNC_ARGS"
echo ""

python3 meraki_netbox/src/sync_networks.py $SYNC_ARGS

echo ""
echo "✅ Sync process completed!"
echo ""
echo "Usage examples for next time:"
echo "  ./setup_and_sync.sh                           # Sync all organizations"
echo "  ./setup_and_sync.sh --org 551485              # Sync specific organization"
echo "  ./setup_and_sync.sh --network L_646829496...  # Sync specific network"
