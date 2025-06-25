import os
import pynetbox

class NetBoxClient:
    """Client for interacting with NetBox API."""

    def __init__(self, url=None, token=None):
        """Initialize the NetBox client.

        Args:
            url (str): NetBox API URL
            token (str): NetBox API token

        Raises:
            ValueError: If URL or token is not provided and not in environment variables.
        """
        # Try to get URL from parameters or environment variables
        self.url = url or os.getenv("NETBOX_URL")
        if not self.url:
            raise ValueError("NetBox URL not provided")

        # Try to get token from parameters or environment variables
        self.token = token or os.getenv("NETBOX_TOKEN")
        if not self.token:
            raise ValueError("NetBox token not provided")

        # Initialize the NetBox API client
        self.api = pynetbox.api(self.url, token=self.token)

    def create_or_update_vlan(self, vlan_id, name, description=None):
        """Create a VLAN in NetBox or update it if it already exists.

        Args:
            vlan_id (int): The VLAN ID
            name (str): The VLAN name
            description (str, optional): Description for the VLAN

        Returns:
            dict: The created or updated VLAN object
        """
        # Check if the VLAN already exists
        existing_vlans = list(self.api.ipam.vlans.filter(vid=vlan_id))

        if existing_vlans:
            # Update the existing VLAN
            existing_vlan = existing_vlans[0]
            existing_vlan.name = name
            if description:
                existing_vlan.description = description
            existing_vlan.save()
            return existing_vlan
        else:
            # Create a new VLAN
            vlan_data = {
                "vid": vlan_id,
                "name": name,
            }

            if description:
                vlan_data["description"] = description

            return self.api.ipam.vlans.create(vlan_data)

    def create_or_update_prefix(self, prefix, description=None, vlan_id=None, vlan_name=None):
        """Create a prefix in NetBox or update it if it already exists.

        Args:
            prefix (str): The network prefix in CIDR notation (e.g., "192.168.10.0/24")
            description (str, optional): Description for the prefix
            vlan_id (int, optional): ID of the associated VLAN
            vlan_name (str, optional): Name of the associated VLAN

        Returns:
            dict: The created or updated prefix object
        """
        vlan_object = None

        # If VLAN ID is provided, ensure the VLAN exists in NetBox
        if vlan_id is not None:
            if not vlan_name:
                vlan_name = f"VLAN {vlan_id}"

            # Create or update the VLAN first
            vlan_object = self.create_or_update_vlan(
                vlan_id=vlan_id,
                name=vlan_name,
                description=f"Meraki VLAN {vlan_id}"
            )

        # Check if the prefix already exists
        existing_prefixes = list(self.api.ipam.prefixes.filter(prefix=prefix))

        if existing_prefixes:
            # Update the existing prefix
            existing_prefix = existing_prefixes[0]
            if description:
                existing_prefix.description = description
            if vlan_object is not None:
                existing_prefix.vlan = vlan_object.id
            existing_prefix.save()
            return existing_prefix
        else:
            # Create a new prefix
            prefix_data = {
                "prefix": prefix,
            }

            if description:
                prefix_data["description"] = description

            if vlan_object is not None:
                prefix_data["vlan"] = vlan_object.id

            return self.api.ipam.prefixes.create(prefix_data)

    def create_or_update_ip_address(self, ip_address, description=None, dns_name=None, status="active"):
        """Create an IP address in NetBox or update it if it already exists.

        Args:
            ip_address (str): The IP address in CIDR notation (e.g., "192.168.10.100/24")
            description (str, optional): Description for the IP address
            dns_name (str, optional): DNS name for the IP address
            status (str, optional): Status of the IP address (default: "active")

        Returns:
            dict: The created or updated IP address object
        """
        # Check if the IP address already exists
        existing_ips = list(self.api.ipam.ip_addresses.filter(address=ip_address))

        if existing_ips:
            # Update the existing IP address
            existing_ip = existing_ips[0]
            if description:
                existing_ip.description = description
            if dns_name:
                existing_ip.dns_name = dns_name
            existing_ip.status = status
            existing_ip.save()
            return existing_ip
        else:
            # Create a new IP address
            ip_data = {
                "address": ip_address,
                "status": status,
            }

            if description:
                ip_data["description"] = description

            if dns_name:
                ip_data["dns_name"] = dns_name

            return self.api.ipam.ip_addresses.create(ip_data)
