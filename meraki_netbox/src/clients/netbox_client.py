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