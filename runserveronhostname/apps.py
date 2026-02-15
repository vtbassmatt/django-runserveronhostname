from importlib import import_module

from django.apps import AppConfig
import django.core.management

from runserveronhostname.management.commands._runserver import PartialRunserverCommand


def patched_load_command_class(app_name, name):
    """
    Adapted from `django.core.management.load_command_class`.

    Given a command name and an application name, return the Command
    class instance. Allow all errors raised by the import process
    (ImportError, AttributeError) to propagate.
    """
    module = import_module("%s.management.commands.%s" % (app_name, name))
    if name != 'runserver':
        return module.Command()

    Command = type('Command', (PartialRunserverCommand, module.Command), dict())
    return Command()


class RunserveronhostnameConfig(AppConfig):
    name = 'runserveronhostname'

    def ready(self):
        
        django.core.management.load_command_class = patched_load_command_class
        return super().ready()
