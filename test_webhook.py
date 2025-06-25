#!/usr/bin/env python3
"""
Test script for Meraki NetBox Webhook Server

This script helps you test your webhook server before going live.
"""

import requests
import json
import time
import hmac
import hashlib
from datetime import datetime

def test_webhook_server(base_url, webhook_secret=None):
    """Test the webhook server endpoints."""
    
    print("🧪 Testing Meraki NetBox Webhook Server")
    print("=" * 50)
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # Test 1: Health Check
    print("1️⃣  Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   📊 Status: {data.get('status')}")
            print(f"   🔐 Webhook secret configured: {data.get('webhook_secret_configured')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print()
    
    # Test 2: Root Endpoint
    print("2️⃣  Testing Root Endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint working")
            print(f"   📋 Service: {data.get('service')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    print()
    
    # Test 3: Test Webhook Endpoint
    print("3️⃣  Testing Test Webhook Endpoint...")
    try:
        test_payload = {
            "network_id": "L_646829496481088735",
            "test": True
        }
        
        response = requests.post(
            f"{base_url}/webhook/test",
            json=test_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Test webhook passed")
            print(f"   📊 Status: {data.get('status')}")
            print(f"   📝 Message: {data.get('message')}")
        else:
            print(f"   ❌ Test webhook failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Test webhook error: {e}")
    
    print()
    
    # Test 4: Meraki Webhook Endpoint (with signature if provided)
    if webhook_secret:
        print("4️⃣  Testing Meraki Webhook Endpoint (with signature)...")
        try:
            # Create a mock Meraki webhook payload
            meraki_payload = {
                "version": "0.1",
                "sharedSecret": webhook_secret,
                "sentAt": datetime.now().isoformat(),
                "organizationId": "551485",
                "organizationName": "Test Organization",
                "networkId": "L_646829496481088735",
                "networkName": "Test Network",
                "alertType": "VLAN configuration changed",
                "alertData": {
                    "vlanId": "30",
                    "vlanName": "Test VLAN"
                }
            }
            
            # Convert to JSON string for signature calculation
            payload_json = json.dumps(meraki_payload, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            
            # Calculate signature
            signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Meraki-Signature': f'sha256={signature}'
            }
            
            response = requests.post(
                f"{base_url}/webhook/meraki",
                data=payload_json,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Meraki webhook passed")
                print(f"   📊 Status: {data.get('status')}")
                print(f"   📝 Message: {data.get('message')}")
            else:
                print(f"   ❌ Meraki webhook failed: {response.status_code}")
                print(f"   📝 Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Meraki webhook error: {e}")
    else:
        print("4️⃣  Skipping Meraki webhook test (no secret provided)")
    
    print()
    print("🎉 Testing Complete!")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Meraki NetBox Webhook Server')
    parser.add_argument('--url', required=True, help='Base URL of webhook server (e.g., https://your-domain.com)')
    parser.add_argument('--secret', help='Webhook secret for signature testing')
    
    args = parser.parse_args()
    
    # Remove trailing slash from URL
    base_url = args.url.rstrip('/')
    
    test_webhook_server(base_url, args.secret)

if __name__ == '__main__':
    main()
