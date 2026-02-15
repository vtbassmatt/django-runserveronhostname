"""
Integration tests for runserveronhostname package.

These tests verify the entire flow from patch application to command execution.
"""
import pytest
from unittest.mock import MagicMock, patch
from django.test import override_settings
from django.core.management.base import BaseCommand
from runserveronhostname.apps import patched_load_command_class
from runserveronhostname.management.commands._runserver import PartialRunserverCommand


class TestIntegration:
    """Integration tests for the complete package functionality."""
    
    @override_settings(RUNSERVER_ON='integration.localhost:9000')
    def test_end_to_end_runserver_with_setting(self):
        """Test end-to-end flow when RUNSERVER_ON is configured."""
        
        with patch('runserveronhostname.apps.import_module') as mock_import:
            captured = {}
            
            class MockRunserverCommand(BaseCommand):
                def handle(self, *args, **options):
                    captured['addrport'] = options.get('addrport')
                    return None
            
            mock_module = MagicMock()
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            command = patched_load_command_class('django.core', 'runserver')
            command.handle(addrport='')
            
            # Verify the setting was used
            assert captured['addrport'] == 'integration.localhost:9000'
    
    def test_end_to_end_runserver_without_setting(self):
        """Test end-to-end flow when RUNSERVER_ON is not set."""
        
        with patch('runserveronhostname.apps.import_module') as mock_import:
            captured = {}
            
            class MockRunserverCommand(BaseCommand):
                def handle(self, *args, **options):
                    captured['addrport'] = options.get('addrport')
                    return None
            
            mock_module = MagicMock()
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            command = patched_load_command_class('django.core', 'runserver')
            command.handle(addrport='foo')
            
            assert captured['addrport'] == 'foo'
    
    @override_settings(RUNSERVER_ON='default.localhost:8000')
    def test_end_to_end_with_user_override(self):
        """Test that user can override RUNSERVER_ON by passing addrport."""
        
        with patch('runserveronhostname.apps.import_module') as mock_import:
            captured = {}
            
            class MockRunserverCommand(BaseCommand):
                def handle(self, *args, **options):
                    captured['addrport'] = options.get('addrport')
                    return None
            
            mock_module = MagicMock()
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            command = patched_load_command_class('django.core', 'runserver')
            # User provides explicit addrport, should not use RUNSERVER_ON
            command.handle(addrport='override.localhost:9999')
            
            # Verify the user override was respected
            assert captured['addrport'] == 'override.localhost:9999'
    
    def test_non_runserver_commands_unaffected(self):
        """Test that non-runserver commands are not affected by the patch."""
        
        with patch('runserveronhostname.apps.import_module') as mock_import:
            
            class MockMigrateCommand(BaseCommand):
                pass
            
            mock_module = MagicMock()
            original_command = MockMigrateCommand()
            mock_module.Command = MagicMock(return_value=original_command)
            mock_import.return_value = mock_module
            
            command = patched_load_command_class('django.core', 'migrate')
            
            # Verify it's the original command
            assert command == original_command
            
            # Verify it's NOT an instance of PartialRunserverCommand
            assert not isinstance(command, PartialRunserverCommand)
    
    @override_settings(RUNSERVER_ON='multi.localhost:8000')
    def test_multiple_runserver_invocations(self):
        """Test that multiple runserver invocations work correctly."""
        
        with patch('runserveronhostname.apps.import_module') as mock_import:
            invocations = []
            
            class MockRunserverCommand(BaseCommand):
                def handle(self, *args, **options):
                    invocations.append(options.get('addrport'))
                    return None
            
            mock_module = MagicMock()
            mock_module.Command = MockRunserverCommand
            mock_import.return_value = mock_module
            
            # First invocation
            command1 = patched_load_command_class('django.core', 'runserver')
            command1.handle(addrport='')
            
            # Second invocation
            command2 = patched_load_command_class('django.core', 'runserver')
            command2.handle(addrport='')
            
            # Both should use the setting
            assert len(invocations) == 2
            assert all(addr == 'multi.localhost:8000' for addr in invocations)
    
    @override_settings(RUNSERVER_ON='impl.localhost:8000')
    def test_different_runserver_implementations(self):
        """Test that different runserver implementations (staticfiles, daphne) are handled."""
        
        implementations = [
            ('django.core', 'runserver'),
            ('django.contrib.staticfiles', 'runserver'),
            ('daphne', 'runserver'),
        ]
        
        for app_name, cmd_name in implementations:
            with patch('runserveronhostname.apps.import_module') as mock_import:
                captured = {}
                
                class MockRunserverCmd(BaseCommand):
                    def handle(self, *args, **options):
                        captured['addrport'] = options.get('addrport')
                        return None
                
                mock_module = MagicMock()
                mock_module.Command = MockRunserverCmd
                mock_import.return_value = mock_module
                
                command = patched_load_command_class(app_name, cmd_name)
                command.handle(addrport='')
                
                assert captured['addrport'] == 'impl.localhost:8000', \
                    f"Failed for {app_name}.{cmd_name}"

