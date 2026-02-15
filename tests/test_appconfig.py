"""
Tests for RunserveronhostnameConfig AppConfig class.
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from importlib import import_module
import django.core.management
from runserveronhostname.apps import patched_load_command_class


class TestPatchedLoadCommandClass:
    """Tests for the patched_load_command_class function that's used by AppConfig."""
    
    def test_returns_regular_command_for_non_runserver(self):
        """Test that non-runserver commands are loaded normally."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            mock_command = MagicMock()
            mock_module.Command = MagicMock(return_value=mock_command)
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'migrate')
            
            mock_import.assert_called_once_with('django.core.management.commands.migrate')
            assert result == mock_command
    
    def test_runserver_command_gets_patched(self):
        """Test that runserver command class gets patched with PartialRunserverCommand."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            from django.core.management.base import BaseCommand
            
            class DummyCommand(BaseCommand):
                pass
            
            mock_module.Command = DummyCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'runserver')
            
            mock_import.assert_called_once_with('django.core.management.commands.runserver')
            
            # Verify result is instance and has both base classes in MRO
            assert isinstance(result, BaseCommand)
            from runserveronhostname.management.commands._runserver import PartialRunserverCommand
            assert isinstance(result, PartialRunserverCommand)
    
    def test_module_import_path_construction(self):
        """Test that module paths are constructed correctly."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.Command = MagicMock(return_value=MagicMock())
            mock_import.return_value = mock_module
            
            patched_load_command_class('myapp', 'mycommand')
            
            assert mock_import.call_args[0][0] == 'myapp.management.commands.mycommand'
    
    def test_import_errors_propagate(self):
        """Test that ImportError propagates."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            
            with pytest.raises(ImportError):
                patched_load_command_class('nonexistent', 'command')
    
    def test_attribute_errors_propagate(self):
        """Test that AttributeError propagates."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock(spec=[])  # No Command attribute
            mock_import.return_value = mock_module
            
            with pytest.raises(AttributeError):
                patched_load_command_class('django.core', 'migrate')


class TestAppConfigReady:
    """Tests for AppConfig.ready() method functionality."""
    
    def test_ready_patches_django_function(self):
        """Test that calling ready() patches django.core.management.load_command_class."""
        original_func = django.core.management.load_command_class
        
        try:
            from runserveronhostname.apps import RunserveronhostnameConfig
            
            # Use a proper module object
            app_module = import_module('runserveronhostname')
            config = RunserveronhostnameConfig('runserveronhostname', app_module)
            config.ready()
            
            # Verify the patch was applied
            assert django.core.management.load_command_class == patched_load_command_class
            
        finally:
            # Restore original
            django.core.management.load_command_class = original_func
    
    def test_ready_calls_super(self):
        """Test that ready() calls parent ready()."""
        from runserveronhostname.apps import RunserveronhostnameConfig
        
        app_module = import_module('runserveronhostname')
        config = RunserveronhostnameConfig('runserveronhostname', app_module)
        
        # Mock the parent's ready method
        with patch.object(RunserveronhostnameConfig.__bases__[0], 'ready', return_value='parent_result') as mock_ready:
            result = config.ready()
            
            mock_ready.assert_called_once()
            assert result == 'parent_result'


