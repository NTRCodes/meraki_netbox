import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clients.netbox_client import NetBoxClient

class TestNetBoxClient:
    """Test suite for the NetBox API client."""

    def test_init_with_params(self):
        """Test client initialization with explicit parameters."""
        client = NetBoxClient(url="https://netbox.example.com", token="test_token_123")
        assert client.url == "https://netbox.example.com"
        assert client.token == "test_token_123"

    def test_init_from_env(self):
        """Test client initialization with environment variables."""
        with patch.dict(os.environ, {
            "NETBOX_URL": "https://netbox.example.com",
            "NETBOX_TOKEN": "test_token_123"
        }):
            client = NetBoxClient()
            assert client.url == "https://netbox.example.com"
            assert client.token == "test_token_123"

    def test_init_missing_params(self):
        """Test client initialization with missing parameters."""
        with patch.dict(os.environ, clear=True):  # Clear environment variables
            with pytest.raises(ValueError):
                NetBoxClient()  # Should raise ValueError when no params provided

            # Test with only URL
            with pytest.raises(ValueError):
                NetBoxClient(url="https://netbox.example.com")

            # Test with only token
            with pytest.raises(ValueError):
                NetBoxClient(token="test_token_123")

    @patch('pynetbox.api')
    def test_create_prefix(self, mock_api):
        """Test creating a prefix in NetBox."""
        # Setup mock
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_ipam = MagicMock()
        mock_instance.ipam = mock_ipam
        mock_prefixes = MagicMock()
        mock_ipam.prefixes = mock_prefixes
        mock_prefixes.create.return_value = {
            "id": 1,
            "prefix": "192.168.10.0/24",
            "description": "Test Prefix"
        }

        # Test the method
        client = NetBoxClient(url="https://netbox.example.com", token="test_token_123")
        prefix = client.create_prefix(
            prefix="192.168.10.0/24",
            description="Test Prefix",
            vlan_id=10
        )

        # Verify results
        assert prefix["id"] == 1
        assert prefix["prefix"] == "192.168.10.0/24"
        mock_prefixes.create.assert_called_once_with({
            "prefix": "192.168.10.0/24",
            "description": "Test Prefix",
            "vlan": 10
        })

    @patch('pynetbox.api')
    def test_create_or_update_prefix_new(self, mock_api):
        """Test creating a new prefix in NetBox."""
        # Setup mock for a new prefix
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_ipam = MagicMock()
        mock_instance.ipam = mock_ipam
        mock_prefixes = MagicMock()
        mock_ipam.prefixes = mock_prefixes

        # Mock filter to return empty list (prefix doesn't exist)
        mock_filter = MagicMock()
        mock_prefixes.filter.return_value = mock_filter
        mock_filter.return_value = []

        # Mock create to return a new prefix
        mock_prefixes.create.return_value = {
            "id": 1,
            "prefix": "192.168.10.0/24",
            "description": "Test Prefix"
        }

        # Test the method
        client = NetBoxClient(url="https://netbox.example.com", token="test_token_123")
        prefix = client.create_or_update_prefix(
            prefix="192.168.10.0/24",
            description="Test Prefix",
            vlan=10
        )

        # Verify results
        assert prefix["id"] == 1
        mock_prefixes.filter.assert_called_once_with(prefix="192.168.10.0/24")
        mock_prefixes.create.assert_called_once()

    @patch('pynetbox.api')
    def test_create_or_update_prefix_existing(self, mock_api):
        """Test updating an existing prefix in NetBox."""
        # Setup mock for an existing prefix
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_ipam = MagicMock()
        mock_instance.ipam = mock_ipam
        mock_prefixes = MagicMock()
        mock_ipam.prefixes = mock_prefixes

        # Mock filter to return an existing prefix
        mock_filter = MagicMock()
        mock_prefixes.filter.return_value = mock_filter
        existing_prefix = MagicMock()
        existing_prefix.id = 1
        existing_prefix.prefix = "192.168.10.0/24"
        existing_prefix.description = "Old Description"
        mock_filter.return_value = [existing_prefix]

        # Test the method
        client = NetBoxClient(url="https://netbox.example.com", token="test_token_123")
        prefix = client.create_or_update_prefix(
            prefix="192.168.10.0/24",
            description="Updated Description",
            vlan=10
        )

        # Verify results
        assert prefix.id == 1
        assert existing_prefix.description == "Updated Description"
        assert existing_prefix.vlan == 10
        existing_prefix.save.assert_called_once()
