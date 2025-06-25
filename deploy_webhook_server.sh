#!/bin/bash

# 🚀 Meraki NetBox Webhook Server - Production Deployment Script
# This script sets up the webhook server on a VPS/droplet for real-time sync

set -e  # Exit on any error

echo "🚀 Meraki NetBox Webhook Server - Production Deployment"
echo "======================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root. Consider creating a dedicated user."
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Create application directory
APP_DIR="/opt/meraki-netbox-sync"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo "📋 Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/meraki-webhook.service > /dev/null <<EOF
[Unit]
Description=Meraki NetBox Webhook Server
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 300 meraki_netbox.src.automation.webhook_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "🌐 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/meraki-webhook > /dev/null <<EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_HERE;  # Replace with your actual domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/meraki-webhook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Create environment file template
echo "📝 Creating environment file template..."
cat > .env.example <<EOF
# Meraki API Configuration
MERAKI_API_KEY=your_meraki_api_key_here
MERAKI_WEBHOOK_SECRET=your_webhook_secret_here

# NetBox API Configuration
NETBOX_URL=https://your-netbox-instance.com
NETBOX_TOKEN=your_netbox_token_here

# Webhook Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
EOF

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  IMPORTANT: Create your .env file!"
    echo "Copy .env.example to .env and fill in your actual values:"
    echo ""
    echo "cp .env.example .env"
    echo "nano .env"
    echo ""
    echo "Required values:"
    echo "- MERAKI_API_KEY: Your Meraki Dashboard API key"
    echo "- MERAKI_WEBHOOK_SECRET: A secret key for webhook security"
    echo "- NETBOX_URL: Your NetBox instance URL"
    echo "- NETBOX_TOKEN: Your NetBox API token"
    echo ""
    read -p "Press Enter once you've created the .env file..."
fi

# Enable and start services
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable meraki-webhook
sudo systemctl start meraki-webhook
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check service status
echo "📊 Service Status:"
echo "=================="
sudo systemctl status meraki-webhook --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l

# Create log monitoring script
echo "📋 Creating log monitoring script..."
cat > monitor_webhook.sh <<'EOF'
#!/bin/bash
echo "🔍 Meraki Webhook Server Monitoring"
echo "==================================="
echo ""
echo "📊 Service Status:"
sudo systemctl status meraki-webhook --no-pager -l
echo ""
echo "📋 Recent Logs:"
sudo journalctl -u meraki-webhook -n 20 --no-pager
echo ""
echo "🌐 Nginx Status:"
sudo systemctl status nginx --no-pager -l
EOF

chmod +x monitor_webhook.sh

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "🌐 Your webhook server is running at:"
echo "   http://YOUR_DOMAIN/webhook/meraki"
echo ""
echo "🧪 Test endpoint:"
echo "   http://YOUR_DOMAIN/webhook/test"
echo ""
echo "❤️  Health check:"
echo "   http://YOUR_DOMAIN/health"
echo ""
echo "📋 Next Steps:"
echo "1. Replace 'YOUR_DOMAIN_HERE' in /etc/nginx/sites-available/meraki-webhook"
echo "2. Set up SSL with: sudo certbot --nginx -d YOUR_DOMAIN"
echo "3. Configure Meraki webhooks to point to your server"
echo "4. Monitor with: ./monitor_webhook.sh"
echo ""
echo "🔧 Useful Commands:"
echo "   sudo systemctl restart meraki-webhook  # Restart webhook service"
echo "   sudo systemctl restart nginx           # Restart nginx"
echo "   sudo journalctl -u meraki-webhook -f   # Follow webhook logs"
echo ""
echo "🎉 You're ready to impress Richard and the council!"
