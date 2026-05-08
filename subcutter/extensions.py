"""File extension constants for media and subtitle files."""

from typing import Optional
from pathlib import Path

MEDIA_EXTENSIONS = (
    ".3gp",
    ".aac",
    ".ac3",
    ".aiff",
    ".alac",
    ".ape",
    ".avi",
    ".divx",
    ".dts",
    ".flac",
    ".flv",
    ".m4a",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".mts",
    ".m2ts",
    ".ogg",
    ".ogv",
    ".opus",
    ".ts",
    ".wav",
    ".webm",
    ".wma",
    ".wmv",
)

SUBTITLE_EXTENSIONS = (".srt",)


def find_companion(path: str, extensions: tuple[str, ...]) -> Optional[str]:
    """Return the first existing file with the same stem but given extensions."""
    p = Path(path)
    for ext in extensions:
        candidate = p.with_suffix(ext)
        if candidate.exists():
            return str(candidate)
    return None
