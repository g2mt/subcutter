"""Encodes subtitle timings into ffmpeg concat format."""

import os

from PySide6.QtCore import QObject, QProcess, Signal


class Encoder(QObject):
    """Generates ffmpeg concat timings from unignored subtitle fragments."""

    timings_updated = Signal(str)
    output_changed = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._timings = ""
        self._media_path = None
        self._output = ""
        self._output_path = ""
        self._process = None

    #### Properties

    @property
    def output(self):
        return self._output

    @property
    def output_path(self):
        return self._output_path

    #### Events

    def _on_output(self):
        data = self._process.readAllStandardOutput().data().decode()
        self._output += data
        self.output_changed.emit(self._output)

    #### Actions

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

    def render(self, output_path):
        """Render the concatenated video using ffmpeg in the background."""
        if not self._timings or not self._media_path:
            raise RuntimeError("No timings to render; preprocess first.")

        self._output_path = output_path
        self._output = ""
        self.output_changed.emit(self._output)

        from subcutter.main_window import MainWindow
        list_path = os.path.join(MainWindow.singleton._tmpdir, "concat_list.txt")
        with open(list_path, "w") as f:
            f.write(self._timings)

        if self._process is not None:
            self._process.kill()
            self._process.waitForFinished()

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_output)
        self._process.finished.connect(lambda *_: self.finished.emit())
        self._process.start("ffmpeg", ["-f", "concat", "-safe", "0", "-i", list_path, output_path])
