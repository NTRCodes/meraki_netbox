import pytest
from meraki_netbox.src.clients.netbox_client import NetBoxClient
from unittest.mock import patch
import os

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
        with patch.dict(os.environ, clear=True):
            with pytest.raises(ValueError):
                NetBoxClient()