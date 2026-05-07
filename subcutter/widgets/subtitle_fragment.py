"""Container for subtitle fragments."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SubtitleFragment(QFrame):
    """A single selectable subtitle entry."""
    clicked = Signal(object)

    def __init__(self, subtitle, show_as_inline=False, parent=None):
        super().__init__(parent)
        self.subtitle = subtitle
        self._show_as_inline = show_as_inline
        self._selected = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        self._layout = QHBoxLayout(self)

        if show_as_inline:
            self._layout.setContentsMargins(4, 2, 4, 2)
        else:
            self._layout.setContentsMargins(5, 5, 5, 5)
            self._info_label = QLabel(
                f"{subtitle.index} | {subtitle.start} --> {subtitle.end}"
            )
            self._layout.addWidget(self._info_label)

        self._content_label = QLabel(subtitle.content.replace('\n', ' '))
        self._layout.addWidget(self._content_label)
        self._layout.addStretch()

    #### State

    def set_selected(self, selected):
        """Set the selection state of this fragment."""
        if self._selected == selected:
            return
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    #### Events

    def mousePressEvent(self, event):
        self.clicked.emit(self.subtitle)
        super().mousePressEvent(event)
