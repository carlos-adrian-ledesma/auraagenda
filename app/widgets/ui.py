from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
)


class SectionCard(QFrame):
    """Reusable premium card with an optional title and subtitle."""

    def __init__(self, title: str = "", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SectionCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout_card = QVBoxLayout(self)
        self.layout_card.setContentsMargins(18, 16, 18, 18)
        self.layout_card.setSpacing(12)
        self.header = QWidget(self)
        self.header.setObjectName("ScrollViewport")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(3)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("Muted")
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        self.layout_card.addWidget(self.header)
        self.header.setVisible(bool(title or subtitle))

    def set_header(self, title: str, subtitle: str = ""):
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)
        self.header.setVisible(bool(title or subtitle))

    def add_layout(self, layout):
        self.layout_card.addLayout(layout)

    def add_widget(self, widget, stretch: int = 0, alignment=Qt.Alignment()):
        self.layout_card.addWidget(widget, stretch, alignment)


class ScrollPage(QWidget):
    """A transparent scroll host used inside settings and long dialogs."""

    def __init__(self, parent=None, max_content_width: int = 900):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.viewport = QWidget()
        self.viewport.setObjectName("SettingsPageViewport")
        self.content = QWidget(self.viewport)
        self.content.setObjectName("ScrollViewport")
        self.content.setMaximumWidth(max_content_width)
        self.layout_content = QVBoxLayout(self.content)
        self.layout_content.setContentsMargins(14, 12, 20, 20)
        self.layout_content.setSpacing(16)
        viewport_layout = QHBoxLayout(self.viewport)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.addWidget(self.content, 0, Qt.AlignTop)
        viewport_layout.addStretch(1)
        self.scroll.setWidget(self.viewport)
        root.addWidget(self.scroll)

    def add_widget(self, widget):
        self.layout_content.addWidget(widget)

    def add_stretch(self):
        self.layout_content.addStretch(1)
