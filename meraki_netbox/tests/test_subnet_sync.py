import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sync.subnet_sync import SubnetSynchronizer

class TestSubnetSynchronizer:
    """Test suite for the subnet synchronizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_meraki = MagicMock()
        self.mock_netbox = MagicMock()
        self.synchronizer = SubnetSynchronizer(
            meraki_client=self.mock_meraki,
            netbox_client=self.mock_netbox
        )
    
    def test_sync_vlan(self):
        """Test synchronizing a single VLAN."""
        # Test data
        vlan_data = {
            "id": "10",
            "name": "Data VLAN",
            "subnet": "192.168.10.0/24",
            "applianceIp": "192.168.10.1"
        }
        network_name = "Test Network"
        
        # Call the method
        self.synchronizer.sync_vlan(vlan_data, network_name)
        
        # Verify the results
        self.mock_netbox.create_or_update_prefix.assert_called_once()
        call_args = self.mock_netbox.create_or_update_prefix.call_args[1]
        assert call_args["prefix"] == "192.168.10.0/24"
        assert "Meraki VLAN 10 - Data VLAN" in call_args["description"]
        assert "Network: Test Network" in call_args["description"]
        assert call_args["vlan"] == 10
    
    def test_sync_vlan_no_subnet(self):
        """Test synchronizing a VLAN without a subnet."""
        # Test data
        vlan_data = {
            "id": "10",
            "name": "Data VLAN",
            # No subnet defined
        }
        network_name = "Test Network"
        
        # Call the method
        self.synchronizer.sync_vlan(vlan_data, network_name)
        
        # Verify the results - should not call create_or_update_prefix
        self.mock_netbox.create_or_update_prefix.assert_not_called()