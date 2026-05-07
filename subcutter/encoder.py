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
        self._video_path = None

    def preprocess(self, fragments, video_path):
        """Generate concat-format timings for all non-ignored fragments."""
        if video_path:
            self._video_path = video_path
        else:
            video_path = "/dev/null"
            self._video_path = None

        self._timings = ""
        for frag in fragments:
            if frag.ignored:
                continue
            sub = frag.subtitle
            start_sec = sub.start.total_seconds()
            end_sec = sub.end.total_seconds()
            self._timings += f"file {video_path}\n"
            self._timings += f"inpoint {start_sec}\n"
            self._timings += f"outpoint {end_sec}\n"

        self.timings_updated.emit(self._timings)

    def render(self, output_file):
        """Render the concatenated video using ffmpeg."""
        if not self._timings or not self._video_path:
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

