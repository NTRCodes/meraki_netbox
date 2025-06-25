"""
IP Address Synchronization Module

This module handles synchronizing IP addresses from Meraki to NetBox.
It syncs both dynamic client IP addresses and static DHCP reservations.
"""

import ipaddress
import re
from typing import Dict, List, Optional


class IPSynchronizer:
    """Synchronizes Meraki IP addresses to NetBox IP addresses."""
    
    def __init__(self, meraki_client, netbox_client):
        """Initialize the IP synchronizer.
        
        Args:
            meraki_client: Initialized MerakiClient instance
            netbox_client: Initialized NetBoxClient instance
        """
        self.meraki = meraki_client
        self.netbox = netbox_client

    def _sanitize_dns_name(self, name: str) -> Optional[str]:
        """Sanitize a name to be valid for DNS in NetBox.

        Args:
            name (str): The original name

        Returns:
            str: Sanitized DNS name or None if invalid
        """
        if not name or name.lower() in ['unknown device', 'none', 'unknown']:
            return None

        # Replace invalid characters with hyphens and remove multiple consecutive hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9\-\.\*_]', '-', name)
        sanitized = re.sub(r'-+', '-', sanitized)  # Replace multiple hyphens with single
        sanitized = sanitized.strip('-')  # Remove leading/trailing hyphens

        # Ensure it's not empty after sanitization
        if not sanitized:
            return None

        return sanitized
    
    def _get_subnet_for_ip(self, ip_address: str, vlans: List[Dict]) -> Optional[str]:
        """Find which VLAN subnet an IP address belongs to.
        
        Args:
            ip_address (str): The IP address to check
            vlans (list): List of VLAN dictionaries with subnet information
            
        Returns:
            str: The subnet in CIDR notation, or None if not found
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            for vlan in vlans:
                if 'subnet' in vlan:
                    try:
                        network = ipaddress.ip_network(vlan['subnet'], strict=False)
                        if ip in network:
                            return vlan['subnet']
                    except (ipaddress.AddressValueError, ValueError):
                        continue
        except (ipaddress.AddressValueError, ValueError):
            pass
        return None
    
    def _create_ip_with_subnet(self, ip_address: str, subnet: str, description: str, dns_name: str = None):
        """Create an IP address in NetBox with proper subnet mask.
        
        Args:
            ip_address (str): The IP address
            subnet (str): The subnet in CIDR notation
            description (str): Description for the IP address
            dns_name (str, optional): DNS name for the IP address
        """
        try:
            # Extract the subnet mask from the subnet
            network = ipaddress.ip_network(subnet, strict=False)
            ip_with_mask = f"{ip_address}/{network.prefixlen}"
            
            self.netbox.create_or_update_ip_address(
                ip_address=ip_with_mask,
                description=description,
                dns_name=dns_name,
                status="active"
            )
        except Exception as e:
            print(f"    Error creating IP {ip_address}: {e}")
    
    def sync_dhcp_reservations(self, network_id: str, network_name: str, vlans: List[Dict]) -> int:
        """Synchronize DHCP reservations (fixed IP assignments) to NetBox.
        
        Args:
            network_id (str): Meraki network ID
            network_name (str): Meraki network name
            vlans (list): List of VLAN dictionaries
            
        Returns:
            int: Number of DHCP reservations synced
        """
        reservations_synced = 0
        
        for vlan in vlans:
            if 'id' not in vlan or 'subnet' not in vlan:
                continue
                
            try:
                # Get DHCP reservations for this VLAN
                reservations = self.meraki.get_dhcp_reservations(network_id, vlan['id'])
                
                for mac_address, assignment in reservations.items():
                    ip_address = assignment.get('ip')
                    name = assignment.get('name', 'Unknown Device')
                    
                    if ip_address:
                        description = f"DHCP Reservation - {name}\nNetwork: {network_name}\nVLAN: {vlan['name']} ({vlan['id']})\nMAC: {mac_address}"
                        dns_name = self._sanitize_dns_name(name)
                        
                        self._create_ip_with_subnet(
                            ip_address=ip_address,
                            subnet=vlan['subnet'],
                            description=description,
                            dns_name=dns_name
                        )
                        reservations_synced += 1
                        
            except Exception as e:
                print(f"    Error syncing DHCP reservations for VLAN {vlan['id']}: {e}")
        
        return reservations_synced
    
    def sync_client_ips(self, network_id: str, network_name: str, vlans: List[Dict], limit: int = 50) -> int:
        """Synchronize active client IP addresses to NetBox.
        
        Args:
            network_id (str): Meraki network ID
            network_name (str): Meraki network name
            vlans (list): List of VLAN dictionaries
            limit (int): Maximum number of clients to sync (default: 50)
            
        Returns:
            int: Number of client IPs synced
        """
        try:
            # Get network clients
            clients = self.meraki.get_network_clients(network_id)
            clients_synced = 0
            
            # Limit the number of clients to avoid overwhelming NetBox
            clients = clients[:limit]
            
            for client in clients:
                ip_address = client.get('ip')
                mac_address = client.get('mac')
                description_name = client.get('description', 'Unknown Device')
                
                if ip_address and mac_address:
                    # Find which subnet this IP belongs to
                    subnet = self._get_subnet_for_ip(ip_address, vlans)
                    
                    if subnet:
                        description = f"Active Client - {description_name}\nNetwork: {network_name}\nMAC: {mac_address}"
                        dns_name = self._sanitize_dns_name(description_name)
                        
                        self._create_ip_with_subnet(
                            ip_address=ip_address,
                            subnet=subnet,
                            description=description,
                            dns_name=dns_name
                        )
                        clients_synced += 1
                    else:
                        print(f"    Warning: Could not find subnet for IP {ip_address}")
            
            return clients_synced
            
        except Exception as e:
            print(f"    Error syncing client IPs: {e}")
            return 0
    
    def sync_network_ips(self, network_id: str, network_name: str, sync_clients: bool = True, sync_reservations: bool = True) -> Dict[str, int]:
        """Synchronize all IP addresses in a network to NetBox.
        
        Args:
            network_id (str): Meraki network ID
            network_name (str): Meraki network name
            sync_clients (bool): Whether to sync active client IPs
            sync_reservations (bool): Whether to sync DHCP reservations
            
        Returns:
            dict: Dictionary with counts of synced items
        """
        try:
            # Get VLANs for subnet information
            vlans = self.meraki.get_vlans(network_id)
            
            results = {
                'dhcp_reservations': 0,
                'client_ips': 0
            }
            
            if sync_reservations:
                results['dhcp_reservations'] = self.sync_dhcp_reservations(network_id, network_name, vlans)
            
            if sync_clients:
                results['client_ips'] = self.sync_client_ips(network_id, network_name, vlans)
            
            return results
            
        except Exception as e:
            print(f"    Error syncing network IPs: {e}")
            return {'dhcp_reservations': 0, 'client_ips': 0}
    
    def sync_organization_ips(self, org_id: str, sync_clients: bool = True, sync_reservations: bool = True) -> Dict[str, int]:
        """Synchronize all IP addresses in an organization to NetBox.
        
        Args:
            org_id (str): Meraki organization ID
            sync_clients (bool): Whether to sync active client IPs
            sync_reservations (bool): Whether to sync DHCP reservations
            
        Returns:
            dict: Dictionary with total counts of synced items
        """
        # Get all networks for this organization
        networks = self.meraki.get_networks(org_id)
        
        total_results = {
            'dhcp_reservations': 0,
            'client_ips': 0
        }
        
        for network in networks:
            network_id = network["id"]
            network_name = network["name"]
            
            print(f"    Syncing IPs for network: {network_name}")
            results = self.sync_network_ips(network_id, network_name, sync_clients, sync_reservations)
            
            total_results['dhcp_reservations'] += results['dhcp_reservations']
            total_results['client_ips'] += results['client_ips']
        
        return total_results
