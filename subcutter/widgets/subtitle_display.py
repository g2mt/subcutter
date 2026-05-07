"""Rich-text subtitle display with highlightable fragments."""

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
import srt

from subcutter.widgets.flow_layout import FlowLayout
from subcutter.widgets.subtitle_fragment import SubtitleFragment


class SubtitleDisplay(QScrollArea):
    """Scrollable container for subtitle fragments."""

    def __init__(self, parent=None):
        from subcutter.main_window import MainWindow

        super().__init__(parent)
        self._fragments = []
        self._current_subtitles = []

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)

        self._container = QWidget()
        self._layout = None
        self.setWidget(self._container)

        MainWindow.singleton.show_as_inline_changed.connect(self._on_show_as_inline_changed)
        self._on_show_as_inline_changed()

    def load_subtitles(self, path):
        """Parse the srt file and load fragments."""
        with open(path, encoding="utf-8") as f:
            self._current_subtitles = list(srt.parse(f))

        self._refresh_fragments()

    #### Fragments

    def _refresh_fragments(self):
        from subcutter.main_window import MainWindow
        self._on_show_as_inline_changed(MainWindow.singleton.show_as_inline())

    def _on_show_as_inline_changed(self, show_as_inline=False):
        """Create fragment widgets from current subtitles."""
        for frag in self._fragments:
            self._layout.removeWidget(frag)
            frag.deleteLater()

        self._fragments.clear()

        old_layout = self._layout
        if show_as_inline:
            self._layout = FlowLayout()
            self._layout.setContentsMargins(4, 4, 4, 4)
        else:
            self._layout = QVBoxLayout()
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)
        for sub in self._current_subtitles:
            frag = SubtitleFragment(sub, show_as_inline=show_as_inline)
            self._fragments.append(frag)
            self._layout.addWidget(frag)
        if not show_as_inline:
            self._layout.addStretch()

        if old_layout is not None:
            QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)
