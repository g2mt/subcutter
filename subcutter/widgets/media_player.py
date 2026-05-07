"""Video playback widget using QMediaPlayer."""

from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class MediaPlayer(QWidget):
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
