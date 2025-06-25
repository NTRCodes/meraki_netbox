#!/usr/bin/env python3
"""
Synchronize Meraki networks to NetBox.
"""
import argparse
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.clients.meraki_client import MerakiClient
from src.clients.netbox_client import NetBoxClient
from src.sync.subnet_sync import SubnetSynchronizer

def main():
    """Main entry point for the script."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Synchronize Meraki networks to NetBox.')
    parser.add_argument('--org', help='Meraki organization ID to synchronize')
    parser.add_argument('--network', help='Meraki network ID to synchronize')
    args = parser.parse_args()
    
    try:
        # Initialize clients
        meraki_client = MerakiClient()
        netbox_client = NetBoxClient()
        
        # Initialize synchronizer
        synchronizer = SubnetSynchronizer(meraki_client, netbox_client)
        
        if args.network:
            # Sync a specific network
            print(f"Synchronizing network {args.network}...")
            # Get network name first
            orgs = meraki_client.get_organizations()
            network_name = None
            for org in orgs:
                networks = meraki_client.get_networks(org["id"])
                for network in networks:
                    if network["id"] == args.network:
                        network_name = network["name"]
                        break
                if network_name:
                    break
            
            if not network_name:
                network_name = "Unknown Network"
                
            vlans_synced = synchronizer.sync_network(args.network, network_name)
            print(f"Network synchronization complete! Synced {vlans_synced} VLANs.")
            
        elif args.org:
            # Sync an entire organization
            print(f"Synchronizing organization {args.org}...")
            vlans_synced = synchronizer.sync_organization(args.org)
            print(f"Organization synchronization complete! Synced {vlans_synced} VLANs.")
            
        else:
            # No specific org or network, sync all organizations
            print("Synchronizing all organizations...")
            total_vlans = 0
            orgs = meraki_client.get_organizations()
            for org in orgs:
                print(f"Synchronizing organization {org['name']}...")
                vlans_synced = synchronizer.sync_organization(org["id"])
                total_vlans += vlans_synced
            print(f"All organizations synchronized! Synced {total_vlans} VLANs.")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())