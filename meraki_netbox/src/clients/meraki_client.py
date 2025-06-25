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
