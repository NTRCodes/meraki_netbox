#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

from src.clients.netbox_client import NetBoxClient

# Initialize the NetBox client
client = NetBoxClient()

# Test basic connectivity
print("=== NetBox Connection Test ===")
try:
    # Get NetBox version (simple API call to test connectivity)
    status = client.api.status()
    print(f"Connected to NetBox version: {status.get('version', 'Unknown')}")
    print(f"NetBox URL: {client.url}")
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Test prefix functionality
print("\n=== Prefixes Test ===")
try:
    # List some existing prefixes (convert to list first, then slice)
    all_prefixes = list(client.api.ipam.prefixes.all())
    prefixes = all_prefixes[:5] if all_prefixes else []

    if prefixes:
        print(f"Found {len(prefixes)} existing prefixes (out of {len(all_prefixes)} total):")
        for prefix in prefixes:
            print(f"  - {prefix.prefix} ({prefix.description or 'No description'})")
    else:
        print("No existing prefixes found.")
        
    # Test creating a test prefix
    print("\nCreating a test prefix...")
    test_prefix = "192.0.2.0/24"  # TEST-NET-1 from RFC 5737 (for testing)
    
    # Check if it already exists
    existing = list(client.api.ipam.prefixes.filter(prefix=test_prefix))
    if existing:
        print(f"Test prefix {test_prefix} already exists, skipping creation.")
    else:
        # Create the prefix
        new_prefix = client.create_or_update_prefix(
            prefix=test_prefix,
            description="Test prefix from Meraki-NetBox integration script"
        )
        print(f"Created test prefix: {test_prefix}")
        
except Exception as e:
    print(f"Prefix test failed: {e}")
    import traceback
    traceback.print_exc()  # Print the full traceback for debugging

print("\nNetBox exploration complete!")