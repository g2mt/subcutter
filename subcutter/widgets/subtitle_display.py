"""Rich-text subtitle display with highlightable fragments."""

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
import srt

from subcutter.widgets.subtitle_fragment import SubtitleFragment


class SubtitleDisplay(QScrollArea):
    """Scrollable container for subtitle fragments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()
        self.setWidget(self._container)

    def load_subtitles(self, path):
        """Parse the srt file and load fragments."""
        with open(path, encoding="utf-8") as f:
            subtitles = list(srt.parse(f))

        # Clear existing
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for sub in subtitles:
            fragment = SubtitleFragment(sub)
            self._layout.insertWidget(self._layout.count() - 1, fragment)
