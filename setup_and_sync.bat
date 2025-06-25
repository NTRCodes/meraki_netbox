@echo off
REM Meraki NetBox Sync - Setup and Run Script for Windows
REM This script handles installation of dependencies and runs the sync process

echo 🚀 Meraki NetBox Sync - Setup and Run
echo ======================================

REM Check for Python 3
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3 and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check for .env file
if not exist ".env" (
    echo.
    echo ⚠️  Warning: .env file not found!
    echo Please create a .env file with your API credentials:
    echo.
    echo Example .env file content:
    echo ==================================================
    echo # Meraki API Configuration
    echo MERAKI_API_KEY=1234567890abcdef1234567890abcdef12345678
    echo.
    echo # NetBox API Configuration
    echo NETBOX_URL=https://netbox.example.com
    echo NETBOX_TOKEN=abcdef1234567890abcdef1234567890abcdef12
    echo ==================================================
    echo.
    echo Replace the example values with your actual API credentials.
    pause
)

echo ✅ Environment file check complete

REM Run the sync with any passed arguments
echo.
echo 🔄 Starting Meraki NetBox synchronization...
echo Arguments: %*
echo.

python meraki_netbox/src/sync_networks.py %*

echo.
echo ✅ Sync process completed!
echo.
echo Usage examples for next time:
echo   setup_and_sync.bat                           # Sync all organizations
echo   setup_and_sync.bat --org 551485              # Sync specific organization
echo   setup_and_sync.bat --network L_646829496...  # Sync specific network
pause
