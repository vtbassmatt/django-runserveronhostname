from django.conf import settings
from django.core.management.base import BaseCommand


class PartialRunserverCommand(BaseCommand):
    def handle(self, *args, **options):
        if not options["addrport"]:
            try:
                run_on = settings.RUNSERVER_ON
                options["addrport"] = run_on
            except AttributeError:
                pass
        return super().handle(*args, **options)
