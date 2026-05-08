"""Tab container for encoding and timings information."""



from PySide6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget


class EncodingTab(QTabWidget):
    """Tab container for encoding info, currently with a Timings tab."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # ── Timings tab ───────────────────────────────────────
        timings_widget = QWidget()
        timings_layout = QVBoxLayout(timings_widget)
        self.timings_text = QPlainTextEdit()
        self.timings_text.setPlaceholderText("Timings input…")
        timings_layout.addWidget(self.timings_text)

        self.addTab(timings_widget, "Timings")

        # ── Output tab ──────────────────────────────────────────
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        self.addTab(output_widget, "Output")
