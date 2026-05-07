"""Container for subtitle fragments."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SubtitleFragment(QFrame):
    """A single selectable subtitle entry."""
    clicked = Signal(object)

    def __init__(self, subtitle, parent=None):
        super().__init__(parent)
        self.subtitle = subtitle
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        info = f"{subtitle.index} | {subtitle.start} --> {subtitle.end}"
        layout.addWidget(QLabel(info))
        layout.addWidget(QLabel(subtitle.content.replace('\n', ' ')))
        layout.addStretch()

    def mousePressEvent(self, event):
        self.setStyleSheet("background-color: #add8e6;")
        self.clicked.emit(self.subtitle)
        super().mousePressEvent(event)
