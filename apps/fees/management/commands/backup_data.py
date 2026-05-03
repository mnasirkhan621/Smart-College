from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.fees.models import BackupLog


class Command(BaseCommand):
    help = "Create a JSON backup of SCMS application data."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", default="backups", help="Directory where the backup file will be written.")

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        if not output_dir.is_absolute():
            output_dir = settings.BASE_DIR / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        output_path = output_dir / f"scms-backup-{timestamp}.json"
        with output_path.open("w", encoding="utf-8") as handle:
            call_command(
                "dumpdata",
                exclude=["contenttypes", "auth.permission", "admin.logentry", "sessions.session"],
                indent=2,
                stdout=handle,
            )

        BackupLog.objects.create(file_path=str(output_path), status="CREATED")
        self.stdout.write(self.style.SUCCESS(f"Backup created: {output_path}"))
