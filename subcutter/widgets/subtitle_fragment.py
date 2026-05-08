"""Container for subtitle fragments."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SubtitleFragment(QFrame):
    """A single selectable subtitle entry."""
    clicked = Signal(object)

    def __init__(self, subtitle, parent=None):
        super().__init__(parent)

        self.subtitle = subtitle
        self._selected = False
        self._show_as_inline = False
        self._ignored = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)

        self._info_label = QLabel(
            f"{subtitle.index} | {subtitle.start} --> {subtitle.end}"
        )
        self._layout.addWidget(self._info_label)

        self._content_label = QLabel(subtitle.content.replace('\n', ' '))
        self._layout.addWidget(self._content_label)
        self._layout.addStretch()

        self._update_show_as_inline()

    #### Properties

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        """Set the selection state of this fragment."""
        if self._selected == selected:
            return
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def show_as_inline(self):
        return self._show_as_inline

    @show_as_inline.setter
    def show_as_inline(self, show_as_inline):
        if self._show_as_inline == show_as_inline:
            return
        self._show_as_inline = show_as_inline
        self._update_show_as_inline()

    def _update_show_as_inline(self):
        if self._show_as_inline:
            self._layout.setContentsMargins(4, 2, 4, 2)
            self._info_label.hide()
        else:
            self._layout.setContentsMargins(5, 5, 5, 5)
            self._info_label.show()
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def ignored(self):
        return self._ignored

    @ignored.setter
    def ignored(self, value):
        if self._ignored == value:
            return
        self._ignored = value
        if value:
            self._content_label.setStyleSheet("text-decoration: line-through;")
        else:
            self._content_label.setStyleSheet("")
        self.setProperty("ignored", value)
        self.style().unpolish(self)
        self.style().polish(self)

    #### Events

    def mousePressEvent(self, event):
        self.clicked.emit(self.subtitle)
        super().mousePressEvent(event)
