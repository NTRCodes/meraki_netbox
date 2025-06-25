class SubnetSynchronizer:
    """Synchronizes Meraki subnets to NetBox prefixes."""
    
    def __init__(self, meraki_client, netbox_client):
        """Initialize the synchronizer.
        
        Args:
            meraki_client: Initialized MerakiClient instance
            netbox_client: Initialized NetBoxClient instance
        """
        self.meraki = meraki_client
        self.netbox = netbox_client
    
    def sync_vlan(self, vlan_data, network_name):
        """Synchronize a single VLAN to NetBox.

        Args:
            vlan_data (dict): VLAN data from Meraki API
            network_name (str): Name of the network this VLAN belongs to
        """
        # Skip if no subnet is defined
        if "subnet" not in vlan_data:
            return

        vlan_id = vlan_data["id"]
        vlan_name = vlan_data["name"]
        subnet = vlan_data["subnet"]

        # Create description with Meraki metadata
        description = f"Meraki VLAN {vlan_id} - {vlan_name}\nNetwork: {network_name}"
        if "applianceIp" in vlan_data:
            description += f"\nGateway: {vlan_data['applianceIp']}"

        # Create or update the prefix in NetBox (this will also create the VLAN if needed)
        self.netbox.create_or_update_prefix(
            prefix=subnet,
            description=description,
            vlan_id=int(vlan_id),
            vlan_name=vlan_name
        )

    def sync_network(self, network_id, network_name):
        """Synchronize all VLANs in a network to NetBox.

        Args:
            network_id (str): Meraki network ID
            network_name (str): Meraki network name
        """
        try:
            # Get all VLANs for this network
            vlans = self.meraki.get_vlans(network_id)

            # Sync each VLAN
            vlans_synced = 0
            for vlan in vlans:
                try:
                    self.sync_vlan(vlan, network_name)
                    vlans_synced += 1
                except Exception as vlan_error:
                    print(f"    Error syncing VLAN {vlan.get('id', 'unknown')} in network {network_name}: {vlan_error}")

            return vlans_synced
        except Exception as e:
            error_msg = str(e)
            # Check for common error patterns and provide more helpful messages
            if "VLANs are not enabled" in error_msg:
                print(f"  Skipping network {network_name}: VLANs are not enabled")
            elif "This endpoint only supports MX networks" in error_msg:
                print(f"  Skipping network {network_name}: Not an MX network (VLANs not supported)")
            else:
                print(f"  Error syncing network {network_name}: {e}")
            return 0

    def sync_organization(self, org_id):
        """Synchronize all networks in an organization to NetBox.

        Args:
            org_id (str): Meraki organization ID
        """
        # Get all networks for this organization
        networks = self.meraki.get_networks(org_id)

        total_vlans = 0
        for network in networks:
            network_id = network["id"]
            network_name = network["name"]

            print(f"  Syncing network: {network_name}")
            vlans_synced = self.sync_network(network_id, network_name)
            total_vlans += vlans_synced

        return total_vlans
