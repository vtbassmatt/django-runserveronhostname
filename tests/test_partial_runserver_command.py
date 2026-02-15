"""
Tests for PartialRunserverCommand class.
"""
import pytest
from django.test import override_settings
from django.core.management.base import BaseCommand
from runserveronhostname.management.commands._runserver import PartialRunserverCommand


@pytest.mark.django_db
class TestPartialRunserverCommand:
    """Test the PartialRunserverCommand mixin class."""
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_uses_runserver_on_when_addrport_empty(self):
        """Test that RUNSERVER_ON is used when addrport is empty."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return 'parent_result'
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        result = command.handle(addrport='')
        
        assert captured['options']['addrport'] == 'testproject.localhost:8000'
        assert result == 'parent_result'
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_preserves_addrport_when_provided(self):
        """Test that existing addrport is preserved even when RUNSERVER_ON is set."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport='0.0.0.0:8080')
        
        assert captured['options']['addrport'] == '0.0.0.0:8080'
    
    def test_handle_without_runserver_on_setting(self):
        """Test that command works when RUNSERVER_ON is not set or is None."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport='foo')
        
        assert captured['options']['addrport'] == 'foo'
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_with_none_addrport(self):
        """Test handling when addrport is None instead of empty string."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport=None)
        
        # None is falsy, so it should be replaced
        assert captured['options']['addrport'] == 'testproject.localhost:8000'
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_with_false_addrport(self):
        """Test handling when addrport is False."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport=False)
        
        # False is falsy, so it should be replaced
        assert captured['options']['addrport'] == 'testproject.localhost:8000'
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_with_zero_addrport(self):
        """Test handling when addrport is 0 (falsy integer)."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport=0)
        
        # 0 is falsy, so it should be replaced
        assert captured['options']['addrport'] == 'testproject.localhost:8000'
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_passes_all_arguments(self):
        """Test that all arguments are passed to parent handle method."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['args'] = args
                captured['options'] = dict(options)
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        args = ('arg1', 'arg2')
        command.handle(*args, addrport='', use_reloader=True, verbosity=2)
        
        assert captured['args'] == args
        assert captured['options']['addrport'] == 'testproject.localhost:8000'
        assert captured['options']['use_reloader'] == True
        assert captured['options']['verbosity'] == 2
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_returns_parent_return_value(self):
        """Test that the return value from parent handle is preserved."""
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                return 'test_return_value'
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        result = command.handle(addrport='')
        
        assert result == 'test_return_value'
    
    def test_handle_with_various_runserver_on_formats(self):
        """Test different formats for RUNSERVER_ON setting."""
        
        test_cases = [
            'localhost:8000',
            '0.0.0.0:8080',
            'myproject.local:3000',
            '192.168.1.100:8000',
            '[::1]:8000',  # IPv6
        ]
        
        for runserver_value in test_cases:
            with override_settings(RUNSERVER_ON=runserver_value):
                captured = {}
                
                class MockParent(BaseCommand):
                    def handle(self, *args, **options):
                        captured['addrport'] = options.get('addrport')
                        return None
                
                class TestCommand(PartialRunserverCommand, MockParent):
                    pass
                
                command = TestCommand()
                command.handle(addrport='')
                
                assert captured['addrport'] == runserver_value, \
                    f"Failed for {runserver_value}"
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_handle_with_whitespace_addrport(self):
        """Test handling when addrport contains only whitespace."""
        
        captured = {}
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                captured['addrport'] = options.get('addrport')
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        command.handle(addrport='   ')
        
        # Whitespace string is truthy in Python, so it should NOT be replaced
        assert captured['addrport'] == '   '
    
    def test_handle_raises_key_error_for_missing_addrport_key(self):
        """Test that handle raises KeyError if addrport is missing from options."""
        
        class MockParent(BaseCommand):
            def handle(self, *args, **options):
                return None
        
        class TestCommand(PartialRunserverCommand, MockParent):
            pass
        
        command = TestCommand()
        
        with pytest.raises(KeyError):
            command.handle()  # No addrport key
