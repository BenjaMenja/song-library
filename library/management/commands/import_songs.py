from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from library.models import Song

class Command(BaseCommand):
    help = "Add a Song entry for each audio file in MUSIC_DIR that isn't in the database yet."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show what would be added without changing the database.")

    def handle(self, *args, dry_run, **options):
        if settings.MUSIC_DIR is None:
            raise CommandError("MUSIC_DIR is not set. Add it to .env first.")
        music_dir = Path(settings.MUSIC_DIR)
        if not music_dir.is_dir():
            raise CommandError(f"MUSIC_DIR does not exist or isn't a folder: {music_dir}")

        on_disk = {
            p.relative_to(music_dir).as_posix(): p.stem
            for p in music_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in settings.AUDIO_EXTENSIONS
        }
        in_db = set(Song.objects.values_list("file_path", flat=True))

        new_paths = sorted(set(on_disk) - in_db)
        missing = sorted(in_db - set(on_disk))

        if not dry_run:
            Song.objects.bulk_create([Song(file_path=path, title=on_disk[path]) for path in new_paths], batch_size=500)
            print(f"Added {len(new_paths)} songs.")
        else:
            print(f"Non dry run adds {len(new_paths)} songs.")

        if dry_run:
            for path in new_paths[:20]:
                print(f"  + {path}")
            if len(new_paths) > 20:
                print(f"  ... and {len(new_paths) - 20} more.")
        if missing:
            print(self.style.WARNING(
                f"{len(missing)} database entries point to files that no longer exist:"))
            for path in missing[:20]:
                print(f"  - {path}")
            if len(missing) > 20:
                print(f"  ... and {len(missing) - 20} more.")
