import pytest
from unittest.mock import patch, MagicMock
import os

from meraki_netbox.src.clients.meraki_client import MerakiClient


class TestMerakiClient:
    def test_init_with_params(self):
        # We'll implement MerakiClient later, so this test will fail initially
        client = MerakiClient(api_key="test_api_key_123")
        assert client.api_key == "test_api_key_123"

    def test_init_from_env(self):
        """Test client initialization with environment variables."""
        with patch.dict(os.environ, {
            "MERAKI_API_KEY": "test_api_key_123"
        }):
            client = MerakiClient()
            assert client.api_key == "test_api_key_123"
        pass

    def test_init_missing_params(self):
        """Test client initialization with missing parameters."""
        with patch.dict(os.environ, clear=True): # Clear environment variables
            with pytest.raises(ValueError):
                MerakiClient()  # Should raise ValueError when no params provided

    @patch('meraki.DashboardAPI')
    def test_init_meraki_client(self, mock_dashboard):
        """Test getting organizations"""
        # Setup Mock
        mock_instance = MagicMock()
        mock_dashboard.return_value = mock_instance
        mock_instance.organizations.getOrganizations.return_value = [
            {"id": "1", "name": "Org 1"},
            {"id": "2", "name": "Org 2"}
        ]

        # Test the method
        client = MerakiClient(api_key="test_api_key_123")
        orgs = client.get_organizations()

        # Verify Results
        assert len(orgs) >= 1
        assert orgs[0]["id"] == "1"
        assert orgs[0]["name"] == "Org 1"
