"""Rich-text subtitle display with highlightable fragments."""

import json

from datetime import timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QWidget
import srt

from subcutter.widgets.flow_layout import FlowLayout
from subcutter.widgets.subtitle_fragment import SubtitleFragment


class SubtitleDisplay(QScrollArea):
    """Scrollable container for subtitle fragments."""
    selected = Signal(object)

    def __init__(self, parent=None):
        from subcutter.main_window import MainWindow

        super().__init__(parent)
        self._fragments = []
        self._current_subtitles = []
        self._anchor_index = None
        self._playing_fragment = None

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)

        self._container = QWidget()
        self._layout = None
        self.setWidget(self._container)

        MainWindow.singleton.show_as_inline_changed.connect(self._on_show_as_inline_changed)
        self._on_show_as_inline_changed()

    def load_subtitles(self, path):
        """Parse the srt file and load fragments."""
        with open(path, encoding="utf-8") as f:
            self._current_subtitles = list(srt.parse(f))

        self._refresh_fragments()

    #### Fragments

    def _refresh_fragments(self):
        """Create fragment widgets from current subtitles."""
        for frag in self._fragments:
            try:
                self._layout.removeWidget(frag)
            except Exception:
                pass
            frag.deleteLater()

        self._fragments.clear()
        self._anchor_index = None
        self._playing_fragment = None

        from subcutter.main_window import MainWindow
        show_as_inline = MainWindow.singleton.show_as_inline

        old_layout = self._layout
        if show_as_inline:
            self._layout = FlowLayout()
            self._layout.setContentsMargins(4, 4, 4, 4)
        else:
            self._layout = QVBoxLayout()
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)
        for sub in self._current_subtitles:
            frag = SubtitleFragment(sub)
            frag.show_as_inline = show_as_inline
            frag.clicked.connect(self._on_fragment_clicked)
            self._fragments.append(frag)
            self._layout.addWidget(frag)
        if not show_as_inline:
            self._layout.addStretch()

        if old_layout is not None:
            QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)

    def _on_show_as_inline_changed(self, show_as_inline=False):
        """Move fragments to a new layout without recreating them."""
        old_layout = self._layout
        if show_as_inline:
            self._layout = FlowLayout()
            self._layout.setContentsMargins(4, 4, 4, 4)
        else:
            self._layout = QVBoxLayout()
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)

        for frag in self._fragments:
            frag.show_as_inline = show_as_inline
            self._layout.addWidget(frag)
        if not show_as_inline:
            self._layout.addStretch()

        if old_layout is not None:
            QWidget().setLayout(old_layout)
        self._container.setLayout(self._layout)

    def _on_fragment_clicked(self, subtitle):
        """Handle fragment click, supporting shift-click range selection."""
        idx = next(
            (i for i, s in enumerate(self._current_subtitles) if s is subtitle),
            None,
        )
        if idx is None:
            return

        modifiers = QApplication.keyboardModifiers()

        if modifiers & Qt.ShiftModifier and self._anchor_index is not None:
            start = min(self._anchor_index, idx)
            end = max(self._anchor_index, idx)
            for i, frag in enumerate(self._fragments):
                frag.selected = start <= i <= end
            self.selected.emit(self._fragments[start])
        else:
            for frag in self._fragments:
                frag.selected = False
            self._fragments[idx].selected = True
            self._anchor_index = idx
            self.selected.emit(self._fragments[idx])

    ### Playing fragment

    @property
    def playing_fragment(self):
        return self._playing_fragment

    @playing_fragment.setter
    def playing_fragment(self, fragment):
        old = self._playing_fragment
        if old is not None and fragment is not None and old[0] == fragment[0]:
            return
        if old is not None:
            old[1].playing = False
        self._playing_fragment = fragment
        if fragment is not None:
            fragment[1].playing = True

    def update_playing_position(self, position_ms):
        pos = timedelta(milliseconds=position_ms)

        # peek neighbours of current playing fragment first
        if self._playing_fragment is not None:
            i = self._playing_fragment[0]
            for di in (0, -1, 1):
                j = i + di
                if 0 <= j < len(self._current_subtitles):
                    sub = self._current_subtitles[j]
                    if sub.start <= pos <= sub.end:
                        self.playing_fragment = (j, self._fragments[j])
                        return

        # binary search
        lo, hi = 0, len(self._current_subtitles) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            sub = self._current_subtitles[mid]
            if pos < sub.start:
                hi = mid - 1
            elif pos > sub.end:
                lo = mid + 1
            else:
                self.playing_fragment = (mid, self._fragments[mid])
                return

        self.playing_fragment = None

    #### Saving/loading

    def save(self):
        """Serialize subtitle display state (subtitles + ignored states) to a JSON string."""
        return json.dumps({
            "subtitles": [
                {
                    "index": sub.index,
                    "start": srt.timedelta_to_srt_timestamp(sub.start),
                    "end": srt.timedelta_to_srt_timestamp(sub.end),
                    "content": sub.content,
                    "proprietary": sub.proprietary,
                    "ignored": self._fragments[i].ignored if i < len(self._fragments) else False,
                }
                for i, sub in enumerate(self._current_subtitles)
            ]
        })

    def load(self, json_str):
        """Restore subtitle display state (subtitles + ignored states) from a JSON string."""
        data = json.loads(json_str)
        subs = data.get("subtitles", [])
        self._current_subtitles = [
            srt.Subtitle(
                index=s.get("index"),
                start=srt.srt_timestamp_to_timedelta(s["start"]),
                end=srt.srt_timestamp_to_timedelta(s["end"]),
                content=s["content"],
                proprietary=s.get("proprietary", ""),
            )
            for s in subs
        ]
        self._refresh_fragments()
        for i, s in enumerate(subs):
            if i < len(self._fragments) and s.get("ignored", False):
                self._fragments[i].ignored = True

