"""Rich-text subtitle display with highlightable fragments."""

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
import srt

from subcutter.widgets.flow_layout import FlowLayout
from subcutter.widgets.subtitle_fragment import SubtitleFragment


class SubtitleDisplay(QScrollArea):
    """Scrollable container for subtitle fragments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self._show_as_inline = False
        self._fragments = []
        self._current_subtitles = []

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()
        self.setWidget(self._container)

    def load_subtitles(self, path):
        """Parse the srt file and load fragments."""
        with open(path, encoding="utf-8") as f:
            self._current_subtitles = list(srt.parse(f))

        self._clear_fragments()
        self._create_fragments()

    def _clear_fragments(self):
        """Remove all fragment widgets."""
        for frag in self._fragments:
            self._layout.removeWidget(frag)
            frag.deleteLater()
        self._fragments.clear()

    def _create_fragments(self):
        """Create fragment widgets from current subtitles."""
        for sub in self._current_subtitles:
            frag = SubtitleFragment(
                sub, show_as_inline=self._show_as_inline
            )
            self._fragments.append(frag)

        if self._show_as_inline:
            self._switch_to_flow_layout()
        else:
            self._switch_to_vbox_layout()

    def _switch_to_vbox_layout(self):
        """Replace current layout with a QVBoxLayout."""
        old_layout = self._layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        for frag in self._fragments:
            self._layout.addWidget(frag)
        self._layout.addStretch()

        # Delete old layout (orphans its items)
        QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)

    def _switch_to_flow_layout(self):
        """Replace current layout with a FlowLayout."""
        old_layout = self._layout
        self._layout = FlowLayout()
        self._layout.setContentsMargins(4, 4, 4, 4)
        for frag in self._fragments:
            self._layout.addWidget(frag)

        QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)

    def set_show_as_inline(self, show_as_inline):
        """Toggle between block and inline layout."""
        if show_as_inline == self._show_as_inline:
            return
        self._show_as_inline = show_as_inline

        if self._fragments:
            for frag in self._fragments:
                frag.set_show_as_inline(show_as_inline)

            if show_as_inline:
                self._switch_to_flow_layout()
            else:
                self._switch_to_vbox_layout()
