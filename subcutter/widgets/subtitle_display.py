"""Rich-text subtitle display with highlightable fragments."""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit


class SubtitleDisplay(QTextEdit):
    """Rich-text subtitle display with highlightable fragments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("monospace", 10))
        self.setPlaceholderText("No subtitle file loaded.")
