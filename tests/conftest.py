"""
Pytest configuration and fixtures for runserveronhostname tests.
"""
import pytest
from unittest.mock import MagicMock, Mock
from django.conf import settings
from django.test import override_settings


@pytest.fixture
def mock_command():
    """Create a mock Django command instance."""
    command = MagicMock()
    command.handle = MagicMock(return_value=None)
    return command


@pytest.fixture
def mock_settings_with_runserver_on():
    """Configure settings with RUNSERVER_ON set."""
    with override_settings(RUNSERVER_ON='testproject.localhost:8000'):
        yield


@pytest.fixture
def mock_settings_without_runserver_on():
    """Configure settings without RUNSERVER_ON."""
    with override_settings():
        # Delete RUNSERVER_ON if it exists
        if hasattr(settings, 'RUNSERVER_ON'):
            delattr(settings, 'RUNSERVER_ON')
        yield


@pytest.fixture
def sample_options():
    """Sample options dictionary for runserver command."""
    return {
        'addrport': '',
        'use_reloader': True,
        'use_threading': True,
        'verbosity': 1,
    }


@pytest.fixture
def sample_options_with_addrport():
    """Sample options dictionary with addrport already specified."""
    return {
        'addrport': '0.0.0.0:8080',
        'use_reloader': True,
        'use_threading': True,
        'verbosity': 1,
    }

