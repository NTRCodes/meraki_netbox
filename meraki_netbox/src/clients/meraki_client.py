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
        self.dashboard = meraki.DashboardAPI(api_key=self.api_key)

    def get_organizations(self):
        """Get all organizations the API key has access to."""
        return self.dashboard.organizations.getOrganizations()