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

        # Try to get network clients (devices with IP addresses)
        try:
            print("\n=== Network Clients ===")
            clients = client.dashboard.networks.getNetworkClients(network['id'])
            for client_device in clients[:5]:  # Show first 5 clients
                ip = client_device.get('ip', 'N/A')
                mac = client_device.get('mac', 'N/A')
                description = client_device.get('description', 'Unknown Device')
                print(f"Client: {description} (IP: {ip}, MAC: {mac})")
        except Exception as e:
            print(f"Could not get network clients: {e}")

        # Try to get DHCP reservations (fixed IP assignments)
        try:
            print("\n=== DHCP Reservations ===")
            for vlan in vlans:
                if 'id' in vlan:
                    # Try to get VLAN details which may include DHCP reservations
                    vlan_details = client.dashboard.appliance.getNetworkApplianceVlan(
                        network['id'], vlan['id']
                    )
                    reservations = vlan_details.get('fixedIpAssignments', {})
                    if reservations:
                        for mac, assignment in reservations.items():
                            ip = assignment.get('ip', 'N/A')
                            name = assignment.get('name', 'Unknown')
                            print(f"Reservation: {name} (IP: {ip}, MAC: {mac}, VLAN: {vlan['id']})")
                    else:
                        print(f"No DHCP reservations found for VLAN {vlan['id']}")
        except Exception as e:
            print(f"Could not get DHCP reservations: {e}")

        print("=" * 50)