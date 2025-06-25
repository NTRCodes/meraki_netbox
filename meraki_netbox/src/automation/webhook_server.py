#!/usr/bin/env python3
"""
Webhook Server for Automated Meraki NetBox Sync

This server listens for webhooks from Meraki and triggers synchronization
when network changes occur.
"""

import os
import sys
import json
import hmac
import hashlib
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('MERAKI_WEBHOOK_SECRET', 'your-webhook-secret-here')
SYNC_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'sync_networks.py')

def verify_webhook_signature(payload, signature):
    """Verify the webhook signature from Meraki."""
    if not signature:
        return False
    
    # Meraki sends signature as 'sha256=<hash>'
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = signature[7:]  # Remove 'sha256=' prefix
    
    # Calculate the expected signature
    calculated_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_signature, expected_signature)

def trigger_sync(network_id=None, org_id=None):
    """Trigger the synchronization script."""
    try:
        cmd = ['python3', SYNC_SCRIPT_PATH]
        
        if network_id:
            cmd.extend(['--network', network_id])
        elif org_id:
            cmd.extend(['--org', org_id])
        
        print(f"🔄 Triggering sync: {' '.join(cmd)}")
        
        # Run the sync in the background
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Sync completed successfully")
            return True, result.stdout
        else:
            print(f"❌ Sync failed: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print("⏰ Sync timed out after 5 minutes")
        return False, "Sync timed out"
    except Exception as e:
        print(f"❌ Error triggering sync: {e}")
        return False, str(e)

@app.route('/webhook/meraki', methods=['POST'])
def meraki_webhook():
    """Handle incoming Meraki webhooks."""
    try:
        # Get the raw payload for signature verification
        payload = request.get_data()
        signature = request.headers.get('X-Meraki-Signature')
        
        # Verify the webhook signature
        if not verify_webhook_signature(payload, signature):
            print("❌ Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse the JSON payload
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        print(f"📨 Received webhook: {json.dumps(data, indent=2)}")
        
        # Extract relevant information
        alert_type = data.get('alertType', '')
        network_id = data.get('networkId')
        org_id = data.get('organizationId')
        
        # Determine if this is a change that requires sync
        sync_triggers = [
            'VLAN configuration changed',
            'Network configuration changed', 
            'DHCP settings changed',
            'IP assignment changed',
            'Subnet changed',
            'appliance_connectivity_change'
        ]
        
        should_sync = any(trigger.lower() in alert_type.lower() for trigger in sync_triggers)
        
        if should_sync:
            print(f"🎯 Triggering sync for alert: {alert_type}")
            success, output = trigger_sync(network_id=network_id, org_id=org_id)
            
            return jsonify({
                'status': 'success' if success else 'error',
                'message': f'Sync {"completed" if success else "failed"}',
                'output': output,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"ℹ️  Ignoring alert (no sync needed): {alert_type}")
            return jsonify({
                'status': 'ignored',
                'message': 'Alert does not require sync',
                'alert_type': alert_type
            })
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test endpoint for manual webhook testing."""
    try:
        data = request.get_json() or {}
        network_id = data.get('network_id')
        org_id = data.get('org_id')
        
        print(f"🧪 Test webhook triggered")
        success, output = trigger_sync(network_id=network_id, org_id=org_id)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': f'Test sync {"completed" if success else "failed"}',
            'output': output,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in test webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'webhook_secret_configured': bool(WEBHOOK_SECRET and WEBHOOK_SECRET != 'your-webhook-secret-here')
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with information."""
    return jsonify({
        'service': 'Meraki NetBox Sync Webhook Server',
        'endpoints': {
            '/webhook/meraki': 'POST - Receive Meraki webhooks',
            '/webhook/test': 'POST - Test webhook endpoint',
            '/health': 'GET - Health check'
        },
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Meraki NetBox Sync Webhook Server")
    print("=" * 50)
    
    if not WEBHOOK_SECRET or WEBHOOK_SECRET == 'your-webhook-secret-here':
        print("⚠️  WARNING: MERAKI_WEBHOOK_SECRET not configured!")
        print("   Add MERAKI_WEBHOOK_SECRET=your-secret-key to your .env file")
    
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    
    print(f"🌐 Server starting on http://{host}:{port}")
    print(f"📨 Webhook endpoint: http://{host}:{port}/webhook/meraki")
    print(f"🧪 Test endpoint: http://{host}:{port}/webhook/test")
    print(f"❤️  Health check: http://{host}:{port}/health")
    
    app.run(host=host, port=port, debug=False)
