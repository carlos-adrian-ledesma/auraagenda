from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Page(QWidget):
    """Common page shell with a stable header and consistent spacing."""

    def __init__(self, title: str = "", subtitle: str = ""):
        super().__init__()
        self.setObjectName("PageRoot")
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(24, 20, 24, 22)
        self.layout_root.setSpacing(14)

        self.header = QFrame(self)
        self.header.setObjectName("PageHeader")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 2)
        header_layout.setSpacing(3)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("Title")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("Subtitle")
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        self.layout_root.addWidget(self.header)

    def refresh(self):
        pass

    def retranslate(self):
        pass
