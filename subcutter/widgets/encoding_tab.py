"""Tab container for encoding and timings information."""

from PySide6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget


class EncodingTab(QTabWidget):
    """Tab container for encoding info, currently with a Timings tab."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Timings tab ───────────────────────────────────────
        timings_widget = QWidget()
        timings_layout = QVBoxLayout(timings_widget)
        self.timings_text = QPlainTextEdit()
        self.timings_text.setPlaceholderText("Timings input…")
        timings_layout.addWidget(self.timings_text)

        self.addTab(timings_widget, "Timings")
