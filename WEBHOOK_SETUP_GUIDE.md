# 🚀 Real-Time Meraki NetBox Sync with Webhooks

This guide will help you set up **real-time synchronization** that triggers automatically when changes happen in Meraki. This is the **sexiest** automation option that will set you apart!

## 🎯 What This Does

- **Real-time sync** when VLANs change in Meraki
- **Automatic IP updates** when DHCP reservations change  
- **Instant NetBox updates** when network configs change
- **Professional webhook server** running 24/7
- **Secure webhook validation** with signatures

## 🏗️ Architecture

```
Meraki Dashboard → Webhook → Your VPS → NetBox
     (Change)      (HTTP)    (Sync)     (Update)
```

## 📋 Requirements

1. **VPS/Droplet** (DigitalOcean, Linode, AWS, etc.)
2. **Domain name** (for HTTPS webhooks)
3. **Meraki Dashboard access** (to configure webhooks)
4. **NetBox instance** (your existing setup)

## 🚀 Step 1: Deploy to Your VPS

### Option A: Quick Deploy (Recommended)

```bash
# 1. Clone your repo to the VPS
git clone https://github.com/your-username/Meraki_NetBox.git
cd Meraki_NetBox

# 2. Run the deployment script
chmod +x deploy_webhook_server.sh
./deploy_webhook_server.sh

# 3. Create your .env file
cp .env.example .env
nano .env
```

### Option B: Manual Deploy

```bash
# Install dependencies
sudo apt update && sudo apt install -y python3 python3-pip nginx

# Install Python packages
pip3 install -r requirements.txt

# Run the webhook server
python3 meraki_netbox/src/automation/webhook_server.py
```

## 🔧 Step 2: Configure Your Environment

Create `.env` file with your credentials:

```bash
# Meraki API Configuration
MERAKI_API_KEY=your_meraki_api_key_here
MERAKI_WEBHOOK_SECRET=super-secret-webhook-key-123

# NetBox API Configuration  
NETBOX_URL=https://your-netbox-instance.com
NETBOX_TOKEN=your_netbox_token_here

# Webhook Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
```

## 🌐 Step 3: Set Up Domain and SSL

```bash
# 1. Point your domain to your VPS IP
# (Do this in your domain registrar's DNS settings)

# 2. Update nginx config with your domain
sudo nano /etc/nginx/sites-available/meraki-webhook
# Replace 'YOUR_DOMAIN_HERE' with your actual domain

# 3. Get SSL certificate
sudo certbot --nginx -d your-domain.com

# 4. Restart nginx
sudo systemctl restart nginx
```

## 📨 Step 4: Configure Meraki Webhooks

### In Meraki Dashboard:

1. **Go to Organization → Configure → Alerts**
2. **Click "Webhooks"**
3. **Add webhook with these settings:**

```
Name: NetBox Sync Webhook
URL: https://your-domain.com/webhook/meraki
Secret: super-secret-webhook-key-123
```

4. **Select these alert types:**
   - ✅ Appliance connectivity change
   - ✅ VLAN configuration changed
   - ✅ Network configuration changed
   - ✅ DHCP settings changed

## 🧪 Step 5: Test Your Setup

### Test the webhook server:

```bash
# Health check
curl https://your-domain.com/health

# Manual test
curl -X POST https://your-domain.com/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"network_id": "L_646829496481088735"}'
```

### Test from Meraki:

1. **Make a small change** in Meraki (like updating a VLAN name)
2. **Check your server logs:**
   ```bash
   sudo journalctl -u meraki-webhook -f
   ```
3. **Verify NetBox** was updated automatically

## 📊 Step 6: Monitor Your Webhook Server

```bash
# Check service status
sudo systemctl status meraki-webhook

# View recent logs
sudo journalctl -u meraki-webhook -n 50

# Follow logs in real-time
sudo journalctl -u meraki-webhook -f

# Use the monitoring script
./monitor_webhook.sh
```

## 🎉 What Richard Will See

When you demo this to Richard:

1. **Make a change in Meraki** (add a VLAN, change DHCP reservation)
2. **Show the webhook logs** receiving the alert in real-time
3. **Show NetBox** automatically updating within seconds
4. **Explain the architecture** and how it scales

## 🔧 Troubleshooting

### Common Issues:

**Webhook not receiving requests:**
- Check firewall settings (port 80/443 open)
- Verify domain DNS points to your VPS
- Check nginx configuration

**Sync failing:**
- Verify .env file has correct API credentials
- Check NetBox connectivity from VPS
- Review webhook logs for errors

**SSL certificate issues:**
- Ensure domain points to VPS before running certbot
- Check nginx configuration syntax

### Useful Commands:

```bash
# Restart webhook service
sudo systemctl restart meraki-webhook

# Check nginx config
sudo nginx -t

# View webhook server logs
sudo journalctl -u meraki-webhook -f

# Test webhook manually
curl -X POST https://your-domain.com/webhook/test
```

## 💡 Pro Tips for Impressing the Council

1. **Show real-time logs** during the demo
2. **Explain the security** (webhook signatures, HTTPS)
3. **Mention scalability** (handles multiple organizations)
4. **Highlight automation** (zero manual intervention)
5. **Show monitoring capabilities** (health checks, logs)

## 🎯 Next Level Features

Once this is working, you can add:
- **Slack notifications** when syncs complete
- **Dashboard** showing sync statistics
- **Multiple webhook endpoints** for different triggers
- **Backup sync scheduling** as fallback

---

**This setup will absolutely set you apart from the pseudo-authority folks!** 🔥

Real-time automation with webhooks is enterprise-level stuff that shows you understand modern infrastructure and automation. Richard will be impressed! 🚀
