"""Encodes subtitle timings into ffmpeg concat format."""

import subprocess
import os
import tempfile

from PySide6.QtCore import QObject, Signal


class Encoder(QObject):
    """Generates ffmpeg concat timings from unignored subtitle fragments."""

    timings_updated = Signal(str)

    def __init__(self):
        super().__init__()
        self._timings = ""
        self._media_path = None

    def preprocess(self, fragments, media_path):
        """Generate concat-format timings for all non-ignored fragments."""
        if media_path:
            self._media_path = media_path
        else:
            media_path = "/dev/null"
            self._media_path = None

        self._timings = ""
        for frag in fragments:
            if frag.ignored:
                continue
            sub = frag.subtitle
            start_sec = sub.start.total_seconds()
            end_sec = sub.end.total_seconds()
            self._timings += f"file {media_path}\n"
            self._timings += f"inpoint {start_sec}\n"
            self._timings += f"outpoint {end_sec}\n"

        self.timings_updated.emit(self._timings)

    def render(self, output_file):
        """Render the concatenated video using ffmpeg."""
        if not self._timings or not self._media_path:
            raise RuntimeError("No timings to render; preprocess first.")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(self._timings)
            list_path = f.name

        try:
            result = subprocess.run(
                ["ffmpeg", "-f", "concat", "-i", list_path, output_file],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"ffmpeg failed (exit {result.returncode}): {result.stderr.strip()}"
                )
        finally:
            os.unlink(list_path)

