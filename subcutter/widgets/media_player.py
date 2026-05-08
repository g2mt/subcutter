"""Video playback widget using QMediaPlayer."""

from typing import Optional

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from subcutter.extensions import MEDIA_EXTENSIONS


class MediaPlayer(QWidget):
    """Video playback widget using QMediaPlayer."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
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

        self._player.positionChanged.connect(self._update_slider)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._seek_slider.sliderMoved.connect(self._seek)
        self._seek_slider.sliderPressed.connect(self._prepare_seek)
        self._seek_slider.sliderReleased.connect(self._end_seek)

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

    def _on_duration_changed(self, duration: int) -> None:
        self._seek_slider.setRange(0, duration)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        if state == QMediaPlayer.PlayingState:
            self._play_button.setIcon(QIcon.fromTheme("media-playback-pause"))
            self._play_button.setToolTip("Pause")
        else:
            self._play_button.setIcon(QIcon.fromTheme("media-playback-start"))
            self._play_button.setToolTip("Play")

    #### Drag & Drop

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                path = urls[0].toLocalFile()
                if Path(path).suffix.lower() in MEDIA_EXTENSIONS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        path = event.mimeData().urls()[0].toLocalFile()
        self.load_file(path)
        event.acceptProposedAction()

    #### Actions

    def load_file(self, path: str | Path) -> None:
        """Load a media file for playback."""
        self._player.setSource(QUrl.fromLocalFile(str(path)))

    def _update_slider(self, position: int) -> None:
        if not self._seek_slider.isSliderDown():
            self._seek_slider.setValue(position)

    def _seek(self, position: int) -> None:
        self._player.setPosition(position)

    def _prepare_seek(self) -> None:
        self._was_playing = self._player.playbackState() == QMediaPlayer.PlayingState
        self._player.pause()

    def _end_seek(self) -> None:
        if self._was_playing:
            self._player.play()

    def _toggle_play(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()
