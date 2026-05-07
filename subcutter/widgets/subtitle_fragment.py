"""Container for subtitle fragments."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SubtitleFragment(QFrame):
    """A single selectable subtitle entry."""
    clicked = Signal(object)

    def __init__(self, subtitle, parent=None, show_as_inline=False):
        super().__init__(parent)
        self.subtitle = subtitle
        self._show_as_inline = show_as_inline
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)

        self._info_label = QLabel(
            f"{subtitle.index} | {subtitle.start} --> {subtitle.end}"
        )
        self._content_label = QLabel(subtitle.content.replace('\n', ' '))

        self._layout.addWidget(self._info_label)
        self._layout.addWidget(self._content_label)
        self._layout.addStretch()

        self._apply_inline_style()

    def _apply_inline_style(self):
        """Apply styling based on inline mode."""
        if self._show_as_inline:
            self.setStyleSheet(
                "SubtitleFragment {"
                "  background-color: #e8e8e8;"
                "  border: 1px solid #bbb;"
                "  border-radius: 4px;"
                "  padding: 2px 6px;"
                "}"
                "SubtitleFragment:hover {"
                "  background-color: #d0d0d0;"
                "}"
            )
            self._info_label.setVisible(False)
            self._layout.setContentsMargins(4, 2, 4, 2)
        else:
            self.setStyleSheet("")
            self._info_label.setVisible(True)
            self._layout.setContentsMargins(5, 5, 5, 5)

    def set_show_as_inline(self, show_as_inline):
        """Switch between full-block and inline chip display."""
        if show_as_inline == self._show_as_inline:
            return
        self._show_as_inline = show_as_inline
        self._apply_inline_style()

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: #add8e6;")
        self.clicked.emit(self.subtitle)
        super().mousePressEvent(event)
