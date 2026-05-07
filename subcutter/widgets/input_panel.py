"""Container for input fields: video path and subtitle path."""

from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget


class InputPanel(QWidget):
    """Container for input fields: video path and subtitle path."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Input video
        layout.addWidget(QLabel("Input video:"))
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Path to video file…")
        layout.addWidget(self.video_input)

        # Subtitle file
        layout.addWidget(QLabel("Subtitle file (.srt):"))
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("Path to .srt file…")
        layout.addWidget(self.subtitle_input)

        layout.addStretch()
