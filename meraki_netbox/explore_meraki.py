#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

from src.clients.meraki_client import MerakiClient

client = MerakiClient()

# Get organizations
print("=== Organizations ===")
orgs = client.get_organizations()
for org in orgs:
    print(f"Organization: {org['name']} (ID: {org['id']})")
    
    # Get networks for this organization
    print("\n=== Networks ===")
    networks = client.get_networks(org['id'])
    for network in networks:
        print(f"Network: {network['name']} (ID: {network['id']})")
        
        # Try to get VLANs if this network has an appliance
        try:
            print("\n=== VLANs ===")
            vlans = client.get_vlans(network['id'])
            for vlan in vlans:
                print(f"VLAN: {vlan['name']} (ID: {vlan['id']}, Subnet: {vlan.get('subnet', 'N/A')})")
        except Exception as e:
            print(f"Could not get VLANs: {e}")