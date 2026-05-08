"""Container for subtitle fragments."""



from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
import srt


class SubtitleFragment(QFrame):
    """A single selectable subtitle entry."""
    clicked = Signal(object)

    def __init__(self, subtitle: srt.Subtitle, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.subtitle = subtitle
        self._selected = False
        self._show_as_inline = False
        self._ignored = False
        self._playing = False

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
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, selected: bool) -> None:
        """Set the selection state of this fragment."""
        if self._selected == selected:
            return
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def show_as_inline(self) -> bool:
        return self._show_as_inline

    @show_as_inline.setter
    def show_as_inline(self, show_as_inline: bool) -> None:
        if self._show_as_inline == show_as_inline:
            return
        self._show_as_inline = show_as_inline
        self._update_show_as_inline()

    def _update_show_as_inline(self) -> None:
        if self._show_as_inline:
            self._layout.setContentsMargins(4, 2, 4, 2)
            self._info_label.hide()
        else:
            self._layout.setContentsMargins(5, 5, 5, 5)
            self._info_label.show()
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def playing(self) -> bool:
        return self._playing

    @playing.setter
    def playing(self, playing: bool) -> None:
        if self._playing == playing:
            return
        self._playing = playing
        self.setProperty("playing", playing)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def ignored(self) -> bool:
        return self._ignored

    @ignored.setter
    def ignored(self, value: bool) -> None:
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit(self.subtitle)
        super().mousePressEvent(event)
