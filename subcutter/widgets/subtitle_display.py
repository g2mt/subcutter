"""Rich-text subtitle display with highlightable fragments."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QWidget
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
        self._anchor_index = None

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
            try:
                self._layout.removeWidget(frag)
            except Exception:
                pass
            frag.deleteLater()

        self._fragments.clear()
        self._anchor_index = None

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
            frag.clicked.connect(self._on_fragment_clicked)
            self._fragments.append(frag)
            self._layout.addWidget(frag)
        if not show_as_inline:
            self._layout.addStretch()

        if old_layout is not None:
            QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)

    def _on_fragment_clicked(self, subtitle):
        """Handle fragment click, supporting shift-click range selection."""
        idx = next(
            (i for i, s in enumerate(self._current_subtitles) if s is subtitle),
            None,
        )
        if idx is None:
            return

        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.ShiftModifier and self._anchor_index is not None:
            start = min(self._anchor_index, idx)
            end = max(self._anchor_index, idx)
            for i, frag in enumerate(self._fragments):
                frag.selected = start <= i <= end
        else:
            for frag in self._fragments:
                frag.selected = False
            self._fragments[idx].selected = True
            self._anchor_index = idx
