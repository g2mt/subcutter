"""Video playback widget using QMediaPlayer."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class MediaPlayer(QWidget):
    """Video playback widget using QMediaPlayer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._video_widget = QVideoWidget(self)
        self._player.setVideoOutput(self._video_widget)

        self._play_button = QPushButton()
        self._play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self._play_button.setIconSize(QSize(16, 16))
        self._play_button.setFixedSize(32, 28)
        self._play_button.setFlat(True)
        self._play_button.clicked.connect(self._toggle_play)

        self._seek_slider = QSlider(Qt.Horizontal)
        self._seek_slider.setRange(0, 0)

        self._player.positionChanged.connect(self._seek_slider.setValue)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._seek_slider.sliderMoved.connect(self._player.setPosition)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self._play_button)
        controls_layout.addWidget(self._seek_slider, stretch=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._video_widget, stretch=1)
        layout.addLayout(controls_layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    #### Events

    def _on_duration_changed(self, duration):
        self._seek_slider.setRange(0, duration)

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self._play_button.setIcon(QIcon.fromTheme("media-playback-pause"))
            self._play_button.setToolTip("Pause")
        else:
            self._play_button.setIcon(QIcon.fromTheme("media-playback-start"))
            self._play_button.setToolTip("Play")

    #### Actions

    def load_file(self, path):
        """Load a media file for playback."""
        self._player.setSource(path)

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()
