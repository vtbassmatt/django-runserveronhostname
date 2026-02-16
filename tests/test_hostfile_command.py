"""
Tests for hostfile command.
"""
from django.test import override_settings
from django.core.management import CommandError
import pytest
from runserveronhostname.management.commands.hostfile import Command


CMD_DEFAULTS = {
    'write': False,
    'status': False,
    'file': None,
}

class TestHostfileCommand:
    """Test the hostfile command."""
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_command_runs(self):
        """Test that the hostfile command runs at all."""
        
        command = Command()
        result = command.handle(**CMD_DEFAULTS)

        assert result == None
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_negative_status(self):
        """Test that we raise when requesting status."""
        
        command = Command()
        options = CMD_DEFAULTS.copy()
        options.update(status=True)
        with pytest.raises(CommandError):
            command.handle(**options)
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_command_runs(self, tmp_path):
        """Test that we can read a hostfile already containing this project."""
        
        d = tmp_path / "etc"
        d.mkdir()
        p = d / "hosts"
        p.write_text("127.0.0.1	testproject.localhost\n", encoding="utf-8")

        command = Command()
        options = CMD_DEFAULTS.copy()
        options.update(file=str(p))
        result = command.handle(**options)

        assert result == None

    def test_command_runs_without_setting(self):
        """Test behavior without a RUNSERVER_ON setting."""
        
        command = Command()
        result = command.handle(**CMD_DEFAULTS)

        assert result == None
    
    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_prints_file(self, capsys, tmp_path):
        """Check we write a file back when the host was already in the file."""
        
        d = tmp_path / "etc"
        d.mkdir()
        p = d / "hosts"
        p.write_text("127.0.0.1	localhost\n127.0.0.1	testproject.localhost\n", encoding="utf-8")

        command = Command()
        options = CMD_DEFAULTS.copy()
        options.update(write=True, file=str(p))
        command.handle(**options)

        captured = capsys.readouterr()
        assert 'testproject.localhost' in captured.out

    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_prints_file_with_addition(self, capsys, tmp_path):
        """Check we write a file with a new line if the old one wasn't found."""

        d = tmp_path / "etc"
        d.mkdir()
        p = d / "hosts"
        p.write_text("127.0.0.1	localhost\n", encoding="utf-8")

        command = Command()
        options = CMD_DEFAULTS.copy()
        options.update(write=True, file=str(p))
        command.handle(**options)

        captured = capsys.readouterr()
        assert 'testproject.localhost' in captured.out

    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_command_with_file(self, tmp_path):
        """Parse a particular file."""

        d = tmp_path / "etc"
        d.mkdir()
        p = d / "hosts"
        p.write_text("127.0.0.1	localhost\n255.255.255.255	broadcasthost\n", encoding="utf-8")
        
        command = Command()
        options = CMD_DEFAULTS.copy()
        options.update(file=str(p))
        result = command.handle(**options)

        assert result == None

    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_coverage_unix(self, monkeypatch):
        """Complete coverage: Unix branch."""
        
        def mock_isdarwin():
            return 'Darwin'
        
        import platform
        real_platform = platform.system()

        monkeypatch.setattr(platform, "system", mock_isdarwin)

        command = Command()
        if real_platform in ('Darwin', 'Linux'):
            # /etc/hosts exists on these platforms, so assert we're fine
            result = command.handle(**CMD_DEFAULTS)
            assert result == None
        else:
            with pytest.raises(CommandError):
                command.handle(**CMD_DEFAULTS)

    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_coverage_windows(self, monkeypatch):
        """Complete coverage: Windows branch."""
        
        def mock_iswindows():
            return 'Windows'
        
        import platform
        monkeypatch.setattr(platform, "system", mock_iswindows)

        command = Command()
        with pytest.raises(CommandError):
            command.handle(**CMD_DEFAULTS)

    @override_settings(RUNSERVER_ON='testproject.localhost:8000')
    def test_coverage_other(self, monkeypatch):
        """Complete coverage: other branch."""
        
        def mock_isnonstop():
            return 'Nonstop'
        
        import platform
        monkeypatch.setattr(platform, "system", mock_isnonstop)

        command = Command()
        with pytest.raises(CommandError):
            command.handle(**CMD_DEFAULTS)
