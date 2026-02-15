"""
Tests for patched_load_command_class function.
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from django.core.management.base import BaseCommand
from runserveronhostname.apps import patched_load_command_class
from runserveronhostname.management.commands._runserver import PartialRunserverCommand


@pytest.mark.django_db
class TestPatchedLoadCommandClass:
    """Test the patched_load_command_class function."""
    
    def test_returns_regular_command_for_non_runserver(self):
        """Test that non-runserver commands are loaded normally."""
        # Test with a built-in Django command
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            mock_command = MagicMock(spec=BaseCommand)
            mock_module.Command = MagicMock(return_value=mock_command)
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'migrate')
            
            # Verify the module was imported correctly
            mock_import.assert_called_once_with('django.core.management.commands.migrate')
            
            # Verify the command instance was created
            assert result == mock_command
            mock_module.Command.assert_called_once()
    
    def test_returns_patched_command_for_runserver(self):
        """Test that runserver command is patched with PartialRunserverCommand."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            # Create a mock Command class
            class MockRunserverCommand(BaseCommand):
                pass
            
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'runserver')
            
            # Verify the module was imported correctly
            mock_import.assert_called_once_with('django.core.management.commands.runserver')
            
            # Verify the returned command is an instance
            assert isinstance(result, BaseCommand)
            
            # Verify the result is an instance of a class that inherits from both
            # PartialRunserverCommand and the original Command
            assert isinstance(result, PartialRunserverCommand)
            assert isinstance(result, MockRunserverCommand)
    
    def test_runserver_command_has_correct_mro(self):
        """Test that the patched runserver command has the correct method resolution order."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            class MockRunserverCommand(BaseCommand):
                pass
            
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'runserver')
            
            # Check the MRO to ensure PartialRunserverCommand comes before the original
            mro = type(result).__mro__
            partial_index = mro.index(PartialRunserverCommand)
            original_index = mro.index(MockRunserverCommand)
            
            # PartialRunserverCommand should come before MockRunserverCommand in MRO
            assert partial_index < original_index
    
    def test_import_errors_propagate(self):
        """Test that ImportError is allowed to propagate."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            
            with pytest.raises(ImportError, match="Module not found"):
                patched_load_command_class('nonexistent', 'command')
    
    def test_attribute_errors_propagate(self):
        """Test that AttributeError is allowed to propagate."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            # Module exists but doesn't have Command attribute
            del mock_module.Command
            mock_import.return_value = mock_module
            
            with pytest.raises(AttributeError):
                patched_load_command_class('django.core', 'migrate')
    
    def test_module_import_path_format(self):
        """Test that module paths are formatted correctly."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            mock_module.Command = MagicMock(return_value=MagicMock())
            mock_import.return_value = mock_module
            
            # Test various app and command names
            test_cases = [
                ('myapp', 'mycommand', 'myapp.management.commands.mycommand'),
                ('django.core', 'migrate', 'django.core.management.commands.migrate'),
                ('my.nested.app', 'custom', 'my.nested.app.management.commands.custom'),
            ]
            
            for app_name, cmd_name, expected_path in test_cases:
                mock_import.reset_mock()
                patched_load_command_class(app_name, cmd_name)
                mock_import.assert_called_once_with(expected_path)
    
    def test_runserver_command_type_name(self):
        """Test that the dynamically created runserver command has the correct type name."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            class MockRunserverCommand(BaseCommand):
                pass
            
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.core', 'runserver')
            
            # The type name should be 'Command'
            assert type(result).__name__ == 'Command'
    
    def test_handles_staticfiles_runserver(self):
        """Test that django.contrib.staticfiles runserver is also patched."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            class MockStaticfilesRunserverCommand(BaseCommand):
                pass
            
            mock_module.Command = MockStaticfilesRunserverCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('django.contrib.staticfiles', 'runserver')
            
            # Verify it's patched correctly
            assert isinstance(result, PartialRunserverCommand)
            assert isinstance(result, MockStaticfilesRunserverCommand)
    
    def test_handles_daphne_runserver(self):
        """Test that third-party runserver implementations (like daphne) are also patched."""
        with patch('runserveronhostname.apps.import_module') as mock_import:
            mock_module = MagicMock()
            
            class MockDaphneRunserverCommand(BaseCommand):
                pass
            
            mock_module.Command = MockDaphneRunserverCommand
            mock_import.return_value = mock_module
            
            result = patched_load_command_class('daphne', 'runserver')
            
            # Verify it's patched correctly
            assert isinstance(result, PartialRunserverCommand)
            assert isinstance(result, MockDaphneRunserverCommand)
