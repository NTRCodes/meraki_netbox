#!/usr/bin/env python3
"""
Meraki NetBox Sync - Setup and Run Script
This script handles installation of dependencies and runs the sync process
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_env_file():
    """Check if .env file exists and provide guidance if not."""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found!")
        print("Please create a .env file with your API credentials:")
        print("\nExample .env file content:")
        print("=" * 50)
        print("# Meraki API Configuration")
        print("MERAKI_API_KEY=1234567890abcdef1234567890abcdef12345678")
        print("")
        print("# NetBox API Configuration") 
        print("NETBOX_URL=https://netbox.example.com")
        print("NETBOX_TOKEN=abcdef1234567890abcdef1234567890abcdef12")
        print("=" * 50)
        print("\nReplace the example values with your actual API credentials.")
        
        response = input("\nPress Enter to continue once you've created the .env file, or 'q' to quit: ")
        if response.lower() == 'q':
            sys.exit(0)
        
        # Check again after user input
        if not env_file.exists():
            print("❌ .env file still not found. Please create it and run the script again.")
            sys.exit(1)

def main():
    print("🚀 Meraki NetBox Sync - Setup and Run")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} found")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip3 install -r requirements.txt", "Installing Python packages"):
        print("❌ Failed to install dependencies. Please check your pip3 installation.")
        sys.exit(1)
    
    print("✅ Dependencies installed successfully")
    
    # Check environment file
    check_env_file()
    print("✅ Environment file check complete")
    
    # Parse arguments for the sync script
    parser = argparse.ArgumentParser(description='Setup and run Meraki NetBox sync')
    parser.add_argument('--org', help='Meraki organization ID to synchronize')
    parser.add_argument('--network', help='Meraki network ID to synchronize')
    args = parser.parse_args()
    
    # Build sync command
    sync_command = "python3 meraki_netbox/src/sync_networks.py"
    if args.org:
        sync_command += f" --org {args.org}"
    elif args.network:
        sync_command += f" --network {args.network}"
    
    # Run the sync
    print(f"\n🔄 Starting Meraki NetBox synchronization...")
    print(f"Command: {sync_command}")
    print("")
    
    if not run_command(sync_command, "Running sync"):
        print("❌ Sync failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n✅ Sync process completed successfully!")
    print("\nUsage examples for next time:")
    print("  python3 setup_and_sync.py                           # Sync all organizations")
    print("  python3 setup_and_sync.py --org 551485              # Sync specific organization") 
    print("  python3 setup_and_sync.py --network L_646829496...  # Sync specific network")

if __name__ == "__main__":
    main()
