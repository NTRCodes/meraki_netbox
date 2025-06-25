# 🚀 Richard's Quick Deploy Guide - Real-Time Meraki Sync

**This will set you apart from everyone else on the council!** 🔥

## 🎯 What You're Building

A **real-time webhook server** that automatically syncs Meraki changes to NetBox **instantly** when they happen. No more manual syncing, no more outdated data.

## 📋 What You Need

1. **VPS/Droplet** ($5-10/month) - DigitalOcean, Linode, or AWS
2. **Domain name** (any cheap domain works)
3. **30 minutes** of your time

## 🚀 Step-by-Step Deployment

### 1. Get a VPS

**DigitalOcean (Recommended):**
- Create $5/month droplet
- Choose Ubuntu 22.04
- Note the IP address

### 2. Point Domain to VPS

In your domain registrar:
```
A Record: @ → YOUR_VPS_IP
A Record: webhook → YOUR_VPS_IP
```

### 3. Deploy to VPS

SSH into your VPS and run:

```bash
# Clone the repo
git clone https://github.com/your-username/Meraki_NetBox.git
cd Meraki_NetBox

# Run the magic deployment script
./deploy_webhook_server.sh
```

### 4. Configure Your Credentials

```bash
# Create environment file
cp .env.example .env
nano .env
```

Fill in your actual values:
```bash
MERAKI_API_KEY=your_actual_meraki_key
MERAKI_WEBHOOK_SECRET=make-up-a-secret-password-123
NETBOX_URL=https://your-netbox-instance.com
NETBOX_TOKEN=your_actual_netbox_token
```

### 5. Update Domain in Config

```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/meraki-webhook

# Replace 'YOUR_DOMAIN_HERE' with your actual domain
# Save and exit (Ctrl+X, Y, Enter)

# Restart nginx
sudo systemctl restart nginx
```

### 6. Get SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

### 7. Test Your Setup

```bash
# Test the webhook server
python3 test_webhook.py --url https://your-domain.com --secret make-up-a-secret-password-123
```

### 8. Configure Meraki Webhooks

1. **Go to Meraki Dashboard**
2. **Organization → Configure → Alerts**
3. **Click "Webhooks"**
4. **Add webhook:**
   - **Name:** NetBox Sync
   - **URL:** `https://your-domain.com/webhook/meraki`
   - **Secret:** `make-up-a-secret-password-123`
5. **Select alerts:**
   - ✅ Appliance connectivity change
   - ✅ VLAN configuration changed
   - ✅ Network configuration changed
   - ✅ DHCP settings changed

## 🎉 Demo for Richard

### The Money Shot:

1. **Open two browser tabs:**
   - Tab 1: Meraki Dashboard
   - Tab 2: NetBox

2. **SSH into your VPS and run:**
   ```bash
   sudo journalctl -u meraki-webhook -f
   ```

3. **Make a change in Meraki** (add a VLAN, change DHCP)

4. **Watch the magic:**
   - Logs show webhook received **instantly**
   - NetBox updates **automatically**
   - No manual intervention needed

### What to Say to Richard:

> "Richard, I've implemented a real-time webhook system that automatically synchronizes any Meraki changes to NetBox within seconds. When someone adds a VLAN or changes DHCP settings, our NetBox is updated instantly without any manual intervention. This is enterprise-grade automation that ensures our IPAM is always current."

## 🔧 Monitoring Commands

```bash
# Check if everything is running
sudo systemctl status meraki-webhook nginx

# Watch logs in real-time
sudo journalctl -u meraki-webhook -f

# Check recent activity
sudo journalctl -u meraki-webhook -n 50

# Test health
curl https://your-domain.com/health
```

## 🚨 Troubleshooting

**If webhook isn't receiving requests:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# Check nginx
sudo nginx -t
sudo systemctl restart nginx
```

**If sync is failing:**
```bash
# Check logs
sudo journalctl -u meraki-webhook -n 20

# Verify .env file
cat .env

# Test manually
curl -X POST https://your-domain.com/webhook/test
```

## 💡 Pro Tips for Maximum Impact

1. **Show the architecture diagram** during your presentation
2. **Demonstrate real-time sync** with live changes
3. **Mention security features** (webhook signatures, HTTPS)
4. **Highlight cost savings** (automated vs manual processes)
5. **Explain scalability** (handles multiple organizations)

## 🎯 Total Cost

- **VPS:** $5-10/month
- **Domain:** $10-15/year
- **SSL:** Free (Let's Encrypt)
- **Your time:** 30 minutes setup
- **Council's reaction:** Priceless 😎

---

**This webhook solution will absolutely blow away the pseudo-authority folks!** 🔥

You'll be the person who brought **real-time automation** to the council's infrastructure. Richard will be impressed, and everyone will know you're the one who actually gets things done! 🚀
