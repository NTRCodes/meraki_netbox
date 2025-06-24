# Meraki to NetBox Labs Integration

A tool to synchronize Cisco Meraki network data with NetBox Labs, focusing on subnets, VLANs, and IP addresses.

## Features

- Synchronize Meraki subnets to NetBox prefixes
- Map Meraki VLANs to NetBox VLAN objects
- Import Meraki IP address assignments to NetBox IP addresses

## Getting Started

### Prerequisites

- Python 3.8+
- Meraki API credentials
- NetBox Labs API token

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/meraki-netbox-integration.git
cd meraki-netbox-integration

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API credentials:

```
MERAKI_API_KEY=your_meraki_api_key
NETBOX_URL=https://your-netbox-instance.com
NETBOX_TOKEN=your_netbox_token
```

## Usage

```bash
python sync_networks.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.