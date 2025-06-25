import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clients.meraki_client import MerakiClient


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

    @patch('meraki.DashboardAPI')
    def test_get_networks(self, mock_dashboard):
        """Test getting networks for an organization."""
        # Setup mock
        mock_instance = MagicMock()
        mock_dashboard.return_value = mock_instance
        mock_instance.organizations.getOrganizationNetworks.return_value = [
            {"id": "N_123", "name": "Test Network", "productTypes": ["appliance"]}
        ]

        # Test the method
        client = MerakiClient(api_key="test_api_key")
        networks = client.get_networks("org_123")

        # Verify results
        assert len(networks) == 1
        assert networks[0]["id"] == "N_123"
        assert networks[0]["name"] == "Test Network"
        mock_instance.organizations.getOrganizationNetworks.assert_called_once_with("org_123")

    @patch('meraki.DashboardAPI')
    def test_get_vlans(self, mock_dashboard):
        """Test getting VLANs for a network."""
        # Setup mock
        mock_instance = MagicMock()
        mock_dashboard.return_value = mock_instance
        mock_instance.appliance.getNetworkApplianceVlans.return_value = [
            {
                "id": "10",
                "name": "Data VLAN",
                "subnet": "192.168.10.0/24",
                "applianceIp": "192.168.10.1"
            }
        ]

        # Test the method
        client = MerakiClient(api_key="test_api_key")
        vlans = client.get_vlans("N_123")

        # Verify results
        assert len(vlans) == 1
        assert vlans[0]["id"] == "10"
        assert vlans[0]["name"] == "Data VLAN"
        assert vlans[0]["subnet"] == "192.168.10.0/24"
        mock_instance.appliance.getNetworkApplianceVlans.assert_called_once_with("N_123")

    @patch('meraki.DashboardAPI')
    def test_get_vlans_no_appliance(self, mock_dashboard):
        """Test getting VLANs for a network without an appliance."""
        # Setup mock to raise an exception
        mock_instance = MagicMock()
        mock_dashboard.return_value = mock_instance
        mock_instance.appliance.getNetworkApplianceVlans.side_effect = meraki.APIError(
            "Network not found", "Network not found", "GET", 404
        )

        # Test the method
        client = MerakiClient(api_key="test_api_key")
        vlans = client.get_vlans("N_123")

        # Verify results
        assert vlans == []
        mock_instance.appliance.getNetworkApplianceVlans.assert_called_once_with("N_123")
