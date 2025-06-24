# Project Structure Explanation

## Core Structure
- `src/` - Contains all source code (using a src layout is a Python best practice)
  - `clients/` - API client code for external services (Meraki, NetBox)
  - `models/` - Data models/schemas for objects we're synchronizing
  - `sync/` - Business logic for synchronization between systems
  - `utils/` - Helper utilities (config loading, logging, etc.)

## Testing Structure
- `tests/` - Mirrors the src directory structure
  - Test files named with `test_` prefix to be auto-discovered by pytest

## Configuration Files
- `.env.example` - Template for environment variables (never commit actual .env)
- `requirements.txt` - Project dependencies
- `setup.py` - Makes the package installable/importable
- `README.md` - Project documentation

## Benefits of this structure
1. Clear separation of concerns
2. Easy to navigate and understand
3. Follows Python packaging best practices
4. Supports test discovery
5. Scales well as project grows