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
from src.sync.ip_sync import IPSynchronizer
from src.sync.ip_sync import IPSynchronizer

def main():
    """Main entry point for the script."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Synchronize Meraki networks to NetBox.')
    parser.add_argument('--org', help='Meraki organization ID to synchronize')
    parser.add_argument('--network', help='Meraki network ID to synchronize')
    parser.add_argument('--sync-ips', action='store_true', default=True,
                       help='Sync IP addresses (default: True)')
    parser.add_argument('--no-sync-ips', action='store_false', dest='sync_ips',
                       help='Skip IP address synchronization')
    parser.add_argument('--sync-clients', action='store_true', default=True,
                       help='Sync active client IP addresses (default: True)')
    parser.add_argument('--no-sync-clients', action='store_false', dest='sync_clients',
                       help='Skip active client IP synchronization')
    parser.add_argument('--sync-reservations', action='store_true', default=True,
                       help='Sync DHCP reservations (default: True)')
    parser.add_argument('--no-sync-reservations', action='store_false', dest='sync_reservations',
                       help='Skip DHCP reservation synchronization')
    args = parser.parse_args()
    
    try:
        # Initialize clients
        meraki_client = MerakiClient()
        netbox_client = NetBoxClient()
        
        # Initialize synchronizers
        subnet_synchronizer = SubnetSynchronizer(meraki_client, netbox_client)
        ip_synchronizer = IPSynchronizer(meraki_client, netbox_client)
        
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

            # Sync VLANs and subnets
            vlans_synced = subnet_synchronizer.sync_network(args.network, network_name)
            print(f"VLANs synced: {vlans_synced}")

            # Sync IP addresses if requested
            if args.sync_ips:
                ip_results = ip_synchronizer.sync_network_ips(
                    args.network, network_name,
                    sync_clients=args.sync_clients,
                    sync_reservations=args.sync_reservations
                )
                print(f"DHCP reservations synced: {ip_results['dhcp_reservations']}")
                print(f"Client IPs synced: {ip_results['client_ips']}")

            print(f"Network synchronization complete!")
            
        elif args.org:
            # Sync an entire organization
            print(f"Synchronizing organization {args.org}...")

            # Sync VLANs and subnets
            vlans_synced = subnet_synchronizer.sync_organization(args.org)
            print(f"VLANs synced: {vlans_synced}")

            # Sync IP addresses if requested
            if args.sync_ips:
                ip_results = ip_synchronizer.sync_organization_ips(
                    args.org,
                    sync_clients=args.sync_clients,
                    sync_reservations=args.sync_reservations
                )
                print(f"DHCP reservations synced: {ip_results['dhcp_reservations']}")
                print(f"Client IPs synced: {ip_results['client_ips']}")

            print(f"Organization synchronization complete!")
            
        else:
            # No specific org or network, sync all organizations
            print("Synchronizing all organizations...")
            total_vlans = 0
            total_dhcp_reservations = 0
            total_client_ips = 0

            orgs = meraki_client.get_organizations()
            for org in orgs:
                print(f"Synchronizing organization {org['name']}...")

                # Sync VLANs and subnets
                vlans_synced = subnet_synchronizer.sync_organization(org["id"])
                total_vlans += vlans_synced
                print(f"  VLANs synced: {vlans_synced}")

                # Sync IP addresses if requested
                if args.sync_ips:
                    ip_results = ip_synchronizer.sync_organization_ips(
                        org["id"],
                        sync_clients=args.sync_clients,
                        sync_reservations=args.sync_reservations
                    )
                    total_dhcp_reservations += ip_results['dhcp_reservations']
                    total_client_ips += ip_results['client_ips']
                    print(f"  DHCP reservations synced: {ip_results['dhcp_reservations']}")
                    print(f"  Client IPs synced: {ip_results['client_ips']}")

            print(f"\nAll organizations synchronized!")
            print(f"Total VLANs synced: {total_vlans}")
            if args.sync_ips:
                print(f"Total DHCP reservations synced: {total_dhcp_reservations}")
                print(f"Total client IPs synced: {total_client_ips}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())