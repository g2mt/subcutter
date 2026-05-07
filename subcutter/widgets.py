"""Custom widgets for the subtitle cutter application."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SubtitleDisplay(QTextEdit):
    """Rich-text subtitle display with highlightable fragments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("monospace", 10))
        self.setPlaceholderText("No subtitle file loaded.")


class VideoPlayer(QWidget):
    """Video playback widget using QMediaPlayer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._video_widget = QVideoWidget(self)

        self._player.setVideoOutput(self._video_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._video_widget)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def player(self):
        return self._player


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
