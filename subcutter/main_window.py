"""Main window of the subtitle cutter application."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QSplitter,
    QToolBar,
)

from subcutter.widgets.input_panel import InputPanel
from subcutter.widgets.subtitle_display import SubtitleDisplay
from subcutter.widgets.video_player import VideoPlayer


class MainWindow(QMainWindow):
    """Top-level window with a two-panel split layout."""
    singleton = None
    show_as_inline_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        if MainWindow.singleton is not None:
            raise RuntimeError()
        MainWindow.singleton = self

        self._show_as_inline = False

        self.setWindowTitle("Subtitle Cutter")
        self.resize(1200, 800)

        self._build_actions()
        self._build_menubar()
        self._build_toolbar()
        self._build_ui()

    #### Properties

    def show_as_inline(self):
        return self._show_as_inline

    def set_show_as_inline(self, value):
        if self._show_as_inline != value:
            self._show_as_inline = value
            self.show_as_inline_changed.emit(value)

    #### UI

    def _build_actions(self):
        self.new_action = QAction(QIcon.fromTheme("document-new"), "&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setToolTip("New project")

        self.open_action = QAction(QIcon.fromTheme("document-open"), "&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setToolTip("Open a video or subtitle file")
        self.open_action.triggered.connect(self._open_file)

        self.save_action = QAction(QIcon.fromTheme("document-save"), "&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setToolTip("Save project")

        self.quit_action = QAction(QIcon.fromTheme("application-exit"), "&Quit", self)
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.setToolTip("Quit application")
        self.quit_action.triggered.connect(self.close)

        self.undo_action = QAction(QIcon.fromTheme("edit-undo"), "&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setToolTip("Undo")

        self.redo_action = QAction(QIcon.fromTheme("edit-redo"), "&Redo", self)
        self.redo_action.setShortcut("Ctrl+Shift+Z")
        self.redo_action.setToolTip("Redo")

        self.ignore_fragment_action = QAction(
            QIcon.fromTheme("format-text-strikethrough"), "Ignore Fragment", self
        )
        self.ignore_fragment_action.setCheckable(True)
        self.ignore_fragment_action.setToolTip("Mark the selected fragment as ignored")

        self.inline_action = QAction(
            QIcon.fromTheme("format-justify-fill"), "Inline Subtitles", self
        )
        self.inline_action.setCheckable(True)
        self.inline_action.setToolTip("Display subtitle fragments inline with wrapping")
        self.inline_action.toggled.connect(self.set_show_as_inline)

    def _build_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

    def _build_toolbar(self):
        toolbar = QToolBar("Main toolbar", self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)

        toolbar.addSeparator()

        toolbar.addAction(self.ignore_fragment_action)
        toolbar.addAction(self.inline_action)

    def _build_ui(self):
        # ── Left panel ────────────────────────────────────────────
        self.subtitle_display = SubtitleDisplay()

        # ── Right panel ───────────────────────────────────────────
        self.video_player = VideoPlayer()
        self.input_panel = InputPanel()

        # Connect file loading to trigger subtitle parsing
        self.input_panel.subtitle_input.textChanged.connect(self._load_subtitles)

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

    #### Actions

    def _open_file(self):
        """Open a file dialog for video or subtitle files."""
        path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Video files (*.mp4 *.avi *.mkv *.mov *.webm);;Subtitle files (*.srt *.ass *.ssa *.vtt);;All files (*)",
        )
        if not path:
            return

        if path.lower().endswith((".srt", ".ass", ".ssa", ".vtt")):
            self.input_panel.subtitle_input.setText(path)
        else:
            self.input_panel.video_input.setText(path)

    def _load_subtitles(self, path):
        if path and path.endswith(".srt"):
            self.subtitle_display.load_subtitles(path)

