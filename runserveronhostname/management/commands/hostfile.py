from pathlib import Path
import platform

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from runserveronhostname.hostfile_parser import Hostfile


class Command(BaseCommand):
    help = "Analyze your system hostfile to see if this project's RUNSERVER_ON hostname is mentioned."

    def add_arguments(self, parser):    # pragma: no cover - we don't need to test Django itself
        parser.add_argument(
            "--write",
            action="store_true",
            help="Print a hostfile with this project added",
        )
        parser.add_argument(
            "--status",
            action="store_true",
            help="Exit with 0 status if this project is already included, 1 if not",
        )
        parser.add_argument(
            "--file",
            action="store",
            help="Exit with 0 status if this project is already included, 1 if not",
        )

    def handle(self, *args, **options):
        try:
            runserver_on = settings.RUNSERVER_ON
        except AttributeError:
            self.stdout.write("RUNSERVER_ON not found in settings.")
            return
        
        target_hostname, _ = runserver_on.split(':', maxsplit=1)

        system = platform.system()
        if options['file']:
            hostfile = Path(options['file'])
        elif system in ('Darwin', 'Linux'):
            hostfile = Path('/etc/hosts')
        elif system in ('Windows',):
            raise CommandError("Windows has a known hostfile but we haven't dealt with it yet", returncode=2)
        else:
            raise CommandError(f'No implementation for {system}', returncode=2)

        with open(hostfile) as f:
            hosts = Hostfile(f)

        write_hostfile = options['write']

        if write_hostfile:
            self.stdout.write(str(hosts))
            if target_hostname not in hosts:
                self.stdout.write(f"127.0.0.1\t{target_hostname}")
        else:
            if target_hostname in hosts:
                self.stdout.write(f"{target_hostname} is already in {hostfile}.")
            else:
                err_msg = f"{target_hostname} not found in {hostfile}."
                if options['status']:
                    raise CommandError(err_msg, returncode=1)
                self.stderr.write(err_msg)
