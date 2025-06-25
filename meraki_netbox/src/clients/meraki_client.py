import os
import meraki

class MerakiClient:
    """Client for interacting with Meraki API."""

    def __init__(self, api_key=None):
        """Initialize the Meraki client.

        Args:
            api_key (str): Meraki API key

        Raises:
            ValueError: If the API key is not provided and not in environment variables.
        """
        # Try to get API key from parameters or environment variables
        self.api_key = api_key or os.getenv("MERAKI_API_KEY")
        if not self.api_key:
            raise ValueError("Meraki API key not provided")

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Initialize the Meraki Dashboard API with custom log path
        self.dashboard = meraki.DashboardAPI(api_key=self.api_key, log_path=logs_dir)

    def get_organizations(self):
        """Get all organizations the API key has access to."""
        return self.dashboard.organizations.getOrganizations()

    def get_networks(self, organization_id):
        """Get all networks for a specific organization.

        Args:
            organization_id (str): The Meraki organization ID

        Returns:
            list: List of network dictionaries
        """
        return self.dashboard.organizations.getOrganizationNetworks(organization_id)

    def get_vlans(self, network_id):
        """Get all VLANs for a specific network.

        Args:
            network_id (str): The Meraki network ID

        Returns:
            list: List of VLAN dictionaries
        """
        return self.dashboard.appliance.getNetworkApplianceVlans(network_id)

    def get_network_clients(self, network_id):
        """Get all clients (devices with IP addresses) for a specific network.

        Args:
            network_id (str): The Meraki network ID

        Returns:
            list: List of client dictionaries with IP addresses
        """
        return self.dashboard.networks.getNetworkClients(network_id)

    def get_vlan_details(self, network_id, vlan_id):
        """Get detailed information about a specific VLAN, including DHCP reservations.

        Args:
            network_id (str): The Meraki network ID
            vlan_id (str): The VLAN ID

        Returns:
            dict: VLAN details including fixedIpAssignments (DHCP reservations)
        """
        return self.dashboard.appliance.getNetworkApplianceVlan(network_id, vlan_id)

    def get_dhcp_reservations(self, network_id, vlan_id):
        """Get DHCP reservations (fixed IP assignments) for a specific VLAN.

        Args:
            network_id (str): The Meraki network ID
            vlan_id (str): The VLAN ID

        Returns:
            dict: Dictionary of MAC addresses to IP assignment details
        """
        vlan_details = self.get_vlan_details(network_id, vlan_id)
        return vlan_details.get('fixedIpAssignments', {})
