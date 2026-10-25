import re
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def normalize_relative_path(raw: str) -> str:
    path = PurePosixPath(raw.strip().replace("\\", "/"))
    if str(path) in ("", "."):
        raise ValueError("Enter the path to the song, relative to the music folder.")
    if path.is_absolute() or _WINDOWS_DRIVE.match(str(path)):
        raise ValueError("Use a path relative to the music folder (no drive letter or leading slash).")
    if ".." in path.parts:
        raise ValueError("The path can't contain '..'.")
    return path.as_posix()


class Song(models.Model):
    file_path = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=200, help_text="Native language display title")
    search_title = models.CharField(max_length=200, blank=True, help_text="English searchable title.")
    artist = models.CharField(max_length=200, blank=True, help_text="Can be left blank if unknown.")
    source_media = models.CharField(max_length=200, blank=True, help_text="Can be left blank if unknown or does not exist.")
    aliases = models.TextField(blank=True, help_text="Other names someone might search for, one per line")

    class Meta:
        ordering = ["artist", "title"]

    def __str__(self):
        if self.search_title:
            return f"{self.artist} - {self.search_title}"
        else:
            return f"{self.artist} - {self.title}" if self.artist else self.title

    def clean(self):
        super().clean()
        try:
            self.file_path = normalize_relative_path(self.file_path)
        except ValueError as exc:
            raise ValidationError({"file_path": str(exc)})

    def absolute_path(self) -> Path | None:
        if settings.MUSIC_DIR is None:
            return None
        return Path(settings.MUSIC_DIR) / self.file_path
