"""Container for input fields: video path and subtitle path."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LineEditWithFile(QWidget):
    """A QLineEdit with a browse button that opens a file dialog."""

    textChanged = Signal(str)

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        layout.addWidget(self.line_edit, stretch=1)

        self.browse_button = QPushButton()
        self.browse_button.setIcon(QIcon.fromTheme("document-open"))
        self.browse_button.setToolTip("Browse for file…")
        layout.addWidget(self.browse_button)

        self.browse_button.clicked.connect(self._browse)
        self.line_edit.textChanged.connect(self.textChanged.emit)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self.line_edit.setText(path)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)




class InputPanel(QWidget):
    """Container for input fields: video path and subtitle path."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Input media
        layout.addWidget(QLabel("Input media:"))
        self.media_input = LineEditWithFile(placeholder="Path to media file…")
        layout.addWidget(self.media_input)

        # Subtitle file
        layout.addWidget(QLabel("Subtitle file:"))
        self.subtitle_input = LineEditWithFile(placeholder="Path to .srt file…")
        layout.addWidget(self.subtitle_input)

        # Output file
        layout.addWidget(QLabel("Output file:"))
        self.output_input = LineEditWithFile(placeholder="Path to output video…")
        layout.addWidget(self.output_input)

        layout.addStretch()
