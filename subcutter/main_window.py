"""Main window of the subtitle cutter application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QSplitter

from subcutter.widgets import InputPanel, SubtitleDisplay, VideoPlayer


class MainWindow(QMainWindow):
    """Top-level window with a two-panel split layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subtitle Cutter")
        self.resize(1200, 800)

        self._build_ui()

    def _build_ui(self):
        # ── Left panel ────────────────────────────────────────────
        self.subtitle_display = SubtitleDisplay()

        # ── Right panel ───────────────────────────────────────────
        self.video_player = VideoPlayer()
        self.input_panel = InputPanel()

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.video_player)
        right_splitter.addWidget(self.input_panel)

        # ── Main splitter ─────────────────────────────────────────
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.subtitle_display)
        main_splitter.addWidget(right_splitter)

        # Default sizes: 80 % left, 20 % right
        main_splitter.setSizes([960, 240])
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(main_splitter)
