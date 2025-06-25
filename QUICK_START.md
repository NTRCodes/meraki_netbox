# 🚀 Meraki NetBox Sync - Quick Start Guide

This guide shows you how to run the entire Meraki NetBox synchronization process with a single simple command.

## Prerequisites

1. **Python 3.6+** installed on your system
2. **API Credentials** for both Meraki and NetBox
3. **Internet connection** to download dependencies

## 📋 Setup Your Environment File

Before running any commands, create a `.env` file in the project root with your API credentials:

```bash
# Meraki API Configuration
MERAKI_API_KEY=your_meraki_api_key_here

# NetBox API Configuration
NETBOX_URL=https://your-netbox-instance.com
NETBOX_TOKEN=your_netbox_token_here
```

**Example:**
```bash
# Meraki API Configuration
MERAKI_API_KEY=1234567890abcdef1234567890abcdef12345678

# NetBox API Configuration
NETBOX_URL=https://netbox.example.com
NETBOX_TOKEN=abcdef1234567890abcdef1234567890abcdef12
```

## 🎯 One-Command Solutions

Choose the method that works best for your operating system:

### Option 1: Python Script (Cross-Platform) ⭐ **RECOMMENDED**

```bash
# Sync all organizations
python3 setup_and_sync.py

# Sync specific organization
python3 setup_and_sync.py --org 551485

# Sync specific network
python3 setup_and_sync.py --network L_646829496481088735
```

### Option 2: Bash Script (Linux/macOS)

```bash
# Sync all organizations
./setup_and_sync.sh

# Sync specific organization
./setup_and_sync.sh --org 551485

# Sync specific network
./setup_and_sync.sh --network L_646829496481088735
```

### Option 3: Batch File (Windows)

```cmd
REM Sync all organizations
setup_and_sync.bat

REM Sync specific organization
setup_and_sync.bat --org 551485

REM Sync specific network
setup_and_sync.bat --network L_646829496481088735
```

## 🔧 What These Commands Do

Each command automatically:

1. ✅ **Checks** Python installation
2. ✅ **Installs** all required dependencies
3. ✅ **Validates** your .env file exists
4. ✅ **Runs** the Meraki NetBox synchronization
5. ✅ **Reports** results and any errors

## 📊 Expected Output

```
🚀 Meraki NetBox Sync - Setup and Run
========================================
✅ Python 3.10.12 found

📦 Installing dependencies...
✅ Dependencies installed successfully
✅ Environment file check complete

🔄 Starting Meraki NetBox synchronization...
Command: python3 meraki_netbox/src/sync_networks.py --network L_646829496481088735

Synchronizing network L_646829496481088735...
Network synchronization complete! Synced 5 VLANs.

✅ Sync process completed successfully!
```

## 🆘 Troubleshooting

### Missing .env File
If you see this warning:
```
⚠️  Warning: .env file not found!
```
Create the `.env` file as shown in the setup section above.

### Python Not Found
If you see:
```
❌ Error: Python is not installed
```
Install Python 3.6+ from [python.org](https://python.org)

### Permission Denied (Linux/macOS)
If you get permission errors with the bash script:
```bash
chmod +x setup_and_sync.sh
./setup_and_sync.sh
```

## 🎯 Quick Examples

```bash
# Most common use case - sync everything (VLANs, subnets, and IPs)
python3 setup_and_sync.py

# Test with a single network first
python3 setup_and_sync.py --network L_646829496481088735

# Sync a specific organization
python3 setup_and_sync.py --org 551485

# Sync only VLANs/subnets (skip IP addresses)
python3 setup_and_sync.py --no-sync-ips

# Sync only DHCP reservations (skip active client IPs)
python3 setup_and_sync.py --no-sync-clients
```

## 🆕 New IP Address Synchronization Features

The sync now includes **IP address synchronization** in addition to VLANs and subnets:

- **DHCP Reservations**: Static IP assignments from Meraki
- **Active Client IPs**: Currently connected devices with their IP addresses
- **Automatic Subnet Detection**: IPs are automatically associated with the correct subnets
- **DNS Name Sanitization**: Device names are cleaned for NetBox compatibility

That's it! The setup scripts handle everything else automatically. 🎉
