"""Main window of the subtitle cutter application."""



import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QToolBar,
    QWidget,
)

from subcutter.widgets.input_panel import InputPanel
from subcutter.widgets.subtitle_display import SubtitleDisplay
from subcutter.widgets.media_player import MediaPlayer
from subcutter.widgets.encoding_tab import EncodingTab
from subcutter.actions.action_history import ActionHistory
from subcutter.actions.ignore_fragment_action import IgnoreFragmentAction
from subcutter.encoder import Encoder
from subcutter.extensions import MEDIA_EXTENSIONS, SUBTITLE_EXTENSIONS, find_companion
from subcutter.widgets.subtitle_fragment import SubtitleFragment


class MainWindow(QMainWindow):
    """Top-level window with a two-panel split layout."""
    singleton = None
    show_as_inline_changed = Signal(bool)
    edited = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        if MainWindow.singleton is not None:
            raise RuntimeError()
        MainWindow.singleton = self

        self._show_as_inline = False
        self._tmpdir = tempfile.mkdtemp(prefix="subcutter_")
        self.destroyed.connect(lambda: shutil.rmtree(self._tmpdir, ignore_errors=True))
        self.encoder = Encoder()
        self.encoder.state_changed.connect(self._on_encoder_state_changed)

        self._action_history = ActionHistory(self)

        app_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self._state_path = app_dir / "subcutter" / "state.json"

        self.setWindowTitle("Subtitle Cutter")
        self.resize(1200, 800)

        self._build_actions()
        self._build_menubar()
        self._build_toolbar()
        self._build_ui()

        self._action_history.can_undo_changed.connect(self.undo_action.setEnabled)
        self._action_history.can_redo_changed.connect(self.redo_action.setEnabled)
        self._action_history.action_performed.connect(self.edited.emit)

        self.setProperty("show_as_inline", False)
        self.setStyleSheet(
        """
            MainWindow[show_as_inline=true] SubtitleFragment {
              background-color: #e8e8e8;
              border: 1px solid #bbb;
              border-radius: 4px;
              padding: 2px 6px;
            }
            MainWindow[show_as_inline=true] SubtitleFragment:hover {
              background-color: #d0d0d0;
            }
            SubtitleFragment[selected=true],
            MainWindow[show_as_inline=true] SubtitleFragment[selected=true] {
              background-color: #add8e6;
            }
            SubtitleFragment[playing=true],
            MainWindow[show_as_inline=true] SubtitleFragment[playing=true] {
              background-color: #fffacd !important;
            }
        """
        )
        self.load_file()

    #### Properties

    @property
    def show_as_inline(self) -> bool:
        return self._show_as_inline

    @show_as_inline.setter
    def show_as_inline(self, value: bool) -> None:
        if self._show_as_inline != value:
            self._show_as_inline = value
            self.setProperty("show_as_inline", value)
            self.style().unpolish(self)
            self.style().polish(self)
            self.show_as_inline_changed.emit(value)

    #### Saving/loading

    def save_file(self) -> None:
        """Serialize current state to state.json."""
        data = {
            "input_panel": json.loads(self.input_panel.save()),
            "subtitle_display": json.loads(self.subtitle_display.save()),
        }
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(data, indent=2))

    def load_file(self) -> None:
        """Deserialize state from state.json and restore widgets."""
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text())
        except (json.JSONDecodeError, OSError):
            return
        self.input_panel.load(json.dumps(data["input_panel"]))
        self.subtitle_display.load(json.dumps(data["subtitle_display"]))
        self._preprocess()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_file()
        super().closeEvent(event)

    #### UI

    def _build_actions(self) -> None:
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
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._action_history.undo)

        self.redo_action = QAction(QIcon.fromTheme("edit-redo"), "&Redo", self)
        self.redo_action.setShortcut("Ctrl+Shift+Z")
        self.redo_action.setToolTip("Redo")
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._action_history.redo)

        self.ignore_fragment_action = QAction(
            QIcon.fromTheme("format-text-strikethrough"), "Ignore Fragment", self
        )
        self.ignore_fragment_action.setCheckable(True)
        self.ignore_fragment_action.setToolTip("Mark the selected fragment as ignored")
        self.ignore_fragment_action.setShortcut("X")
        self.ignore_fragment_action.triggered.connect(self._toggle_ignore_selected)

        self.inline_action = QAction(
            QIcon.fromTheme("format-justify-fill"), "Inline Subtitles", self
        )
        self.inline_action.setCheckable(True)
        self.inline_action.setToolTip("Display subtitle fragments inline with wrapping")
        def on_inline_action_toggled(toggled):
            self.show_as_inline = toggled
        self.inline_action.toggled.connect(on_inline_action_toggled)

        self.render_action = QAction(
            QIcon.fromTheme("media-record"), "Render", self
        )
        self.render_action.setToolTip("Render the concatenated video")
        self.render_action.triggered.connect(self._render)

        self.stop_action = QAction(
            QIcon.fromTheme("media-playback-stop"), "Stop", self
        )
        self.stop_action.setToolTip("Stop rendering")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.encoder.stop)

    def _build_menubar(self) -> None:
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

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main toolbar", self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)

        toolbar.addSeparator()

        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addAction(self.render_action)
        toolbar.addAction(self.stop_action)

        toolbar.addSeparator()

        toolbar.addAction(self.ignore_fragment_action)
        toolbar.addAction(self.inline_action)


    def _build_ui(self) -> None:
        # ── Left panel ────────────────────────────────────────────
        self.subtitle_display = SubtitleDisplay()
        self.subtitle_display.selected.connect(self._on_selected_fragment_changed)

        # ── Right panel ───────────────────────────────────────────
        self.media_player = MediaPlayer()
        self.media_player._player.positionChanged.connect(self.subtitle_display.update_playing_position)

        self.input_panel = InputPanel()

        self.input_panel.subtitle_input.textChanged.connect(self._load_subtitles)
        self.input_panel.media_input.textChanged.connect(self._load_media)

        self.encoding_tab = EncodingTab()
        self.edited.connect(self._preprocess)
        self.encoder.timings_updated.connect(
            self.encoding_tab.timings_text.setPlainText
        )
        self.encoder.output_appended.connect(
            self.encoding_tab.output_text.appendPlainText
        )
        self.encoder.output_reset.connect(
            self.encoding_tab.output_text.clear
        )

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.media_player)
        right_splitter.addWidget(self.input_panel)
        right_splitter.addWidget(self.encoding_tab)
        right_splitter.setSizes([300, 200, 200])

        # ── Main splitter ─────────────────────────────────────────
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.subtitle_display)
        main_splitter.addWidget(right_splitter)

        # Default sizes: 80 % left, 20 % right
        main_splitter.setSizes([960, 240])
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(main_splitter)

    #### Events

    def _on_encoder_state_changed(self, running: bool) -> None:
        self.render_action.setEnabled(not running)
        self.stop_action.setEnabled(running)
        if not running and self.encoder.output_path:
            self.show_notify("Render Complete", f"Video rendered to {self.encoder.output_path}")

    def _on_selected_fragment_changed(self, fragment: SubtitleFragment | None) -> None:
        """Update Ignore Fragment action check state from the first selected fragment."""
        self.ignore_fragment_action.setChecked(
            fragment is not None and fragment.ignored
        )

    #### Notifications

    def show_notify(self, title: str, text: str) -> None:
        """Show a desktop notification (notify-send) or fall back to QMessageBox."""
        if shutil.which("notify-send"):
            subprocess.Popen(
                ["notify-send", title, text]
            )
        else:
            QMessageBox.information(self, title, text)

    #### Actions

    def _toggle_ignore_selected(self) -> None:
        """Toggle the ignored state of the currently selected fragment(s)."""
        selected = [f for f in self.subtitle_display._fragments if f._selected]
        if not selected:
            return
        self._action_history.do(IgnoreFragmentAction(selected))

    def _preprocess(self) -> None:
        self.encoder.preprocess(
            self.subtitle_display._fragments,
            self.input_panel.media_input.text(),
        )

    def _render(self) -> None:
        """Render the concatenated media file."""
        output_path = self.input_panel.output_input.text()
        if not output_path:
            output_path = str(Path(self._tmpdir, "render.mp4"))
        try:
            self.encoder.render(output_path)
        except RuntimeError as e:
            QMessageBox.critical(self, "Render Error", str(e))

    def _open_file(self) -> None:
        """Open a file dialog for media or subtitle files."""
        path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            f"Media files (*{' *'.join(e.lstrip('.') for e in MEDIA_EXTENSIONS)});;Subtitle files (*{' *'.join(e.lstrip('.') for e in SUBTITLE_EXTENSIONS)});;All files (*)",
        )
        if not path:
            return

        if path.lower().endswith(SUBTITLE_EXTENSIONS):
            self.input_panel.subtitle_input.setText(path)
            if not self.input_panel.media_input.text():
                companion = find_companion(
                    path, MEDIA_EXTENSIONS
                )
                if companion:
                    self.input_panel.media_input.setText(companion)
        else:
            self.input_panel.media_input.setText(path)
            if not self.input_panel.subtitle_input.text():
                companion = find_companion(
                    path, SUBTITLE_EXTENSIONS
                )
                if companion:
                    self.input_panel.subtitle_input.setText(companion)

    def _load_media(self, path: str) -> None:
        if path and Path(path).suffix.lower() in MEDIA_EXTENSIONS:
            self.media_player.load_file(path)

    def _load_subtitles(self, path: str) -> None:
        if path and path.endswith(".srt"):
            self.subtitle_display.load_subtitles(path)

