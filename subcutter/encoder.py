"""Encodes subtitle timings into ffmpeg concat format."""

from PySide6.QtCore import QObject, Signal


class Encoder(QObject):
    """Generates ffmpeg concat timings from unignored subtitle fragments."""

    timings_updated = Signal(str)

    def preprocess(self, fragments, video_path):
        """Generate concat-format timings for all non-ignored fragments."""
        if not video_path:
            video_path = "/dev/null"

        lines = []
        for frag in fragments:
            if frag.ignored:
                continue
            sub = frag.subtitle
            start_sec = sub.start.total_seconds()
            end_sec = sub.end.total_seconds()
            lines.append(f"file {video_path}")
            lines.append(f"inpoint {start_sec}")
            lines.append(f"outpoint {end_sec}")

        self.timings_updated.emit("\n".join(lines))
