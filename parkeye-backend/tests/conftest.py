"""Shared test fixtures. Fixes Windows ProactorEventLoop + asyncpg issues."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session to avoid
    'Event loop is closed' errors with asyncpg on Windows."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
