# tests/conftest.py

import pytest

# permite usar pytest.mark.asyncio sin decorar cada test
pytest_plugins = ["pytest_asyncio"]