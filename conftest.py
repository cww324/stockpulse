"""
Pytest configuration for StockPulse.

This file is automatically loaded by pytest and configures:
- Python path to include project root
- Custom markers
- Shared fixtures
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require database)",
    )
