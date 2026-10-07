from __future__ import annotations

from .design_system import REQUIRED_THEME_TOKENS

# Every theme defines the same semantic surface colours.  This prevents Qt's
# native palette from leaking white/grey panels into a dark theme.
THEMES = {
    "Pink Crystal": {
        "bg1":"#1C0B2B", "bg2":"#32104D", "sidebar":"#11071D", "surface":"#251135",
        "surface_alt":"#2D1641", "card":"#35194B", "border":"#644978", "accent":"#F35BCB",
        "accent_hover":"#FF83DC", "accent2":"#A574E8", "text":"#FFF4FF", "muted":"#D9BEE5",
        "disabled":"#A68BAF", "danger":"#FF7290", "success":"#72DAB2", "dialog":"#21122F",
        "field":"#2A1838", "paper":"#FFF0F8", "ink":"#4A164D", "selection_text":"#170A22",
    },
    "Rose Night": {
        "bg1":"#190812", "bg2":"#4A132E", "sidebar":"#10060B", "surface":"#28111C",
        "surface_alt":"#321724", "card":"#401E2D", "border":"#79465B", "accent":"#FF5AAA",
        "accent_hover":"#FF84BF", "accent2":"#FFC0DF", "text":"#FFF8FC", "muted":"#E8C9D9",
        "disabled":"#B892A4", "danger":"#FF7188", "success":"#77D9B0", "dialog":"#27121D",
        "field":"#351D2A", "paper":"#FFF2F7", "ink":"#52143A", "selection_text":"#210A15",
    },
    "Violet Dream": {
        "bg1":"#151027", "bg2":"#423064", "sidebar":"#0F0A1B", "surface":"#241C36",
        "surface_alt":"#2C2342", "card":"#372A50", "border":"#695A82", "accent":"#BD7CFF",
        "accent_hover":"#CEA0FF", "accent2":"#F69BFF", "text":"#FFFFFF", "muted":"#DED5F2",
        "disabled":"#A99EBB", "danger":"#FF7AA8", "success":"#75D8B4", "dialog":"#261D3E",
        "field":"#332B48", "paper":"#FDF2FF", "ink":"#4A2864", "selection_text":"#1C112A",
    },
    "Blush": {
        "bg1":"#381925", "bg2":"#6B354E", "sidebar":"#251019", "surface":"#432332",
        "surface_alt":"#4D2A39", "card":"#573043", "border":"#8A6172", "accent":"#FF8FB8",
        "accent_hover":"#FFA8C8", "accent2":"#FFD2E4", "text":"#FFF9FB", "muted":"#F1D8E0",
        "disabled":"#C09EAA", "danger":"#FF708F", "success":"#79D6B2", "dialog":"#321A24",
        "field":"#4E2F3C", "paper":"#FFF7FA", "ink":"#5A263A", "selection_text":"#2A101B",
    },
    "Cherry Night": {
        "bg1":"#17070D", "bg2":"#48101D", "sidebar":"#0D0408", "surface":"#261017",
        "surface_alt":"#30141D", "card":"#3B1924", "border":"#713947", "accent":"#FF4770",
        "accent_hover":"#FF6D8D", "accent2":"#FF9FB6", "text":"#FFF7F9", "muted":"#E5C2CB",
        "disabled":"#AA858E", "danger":"#FF516F", "success":"#70D7AF", "dialog":"#281017",
        "field":"#351A23", "paper":"#FFF3F6", "ink":"#58182A", "selection_text":"#21080F",
    },
    "Lavender": {
        "bg1":"#241B36", "bg2":"#5B4A79", "sidebar":"#171121", "surface":"#302841",
        "surface_alt":"#3A3150", "card":"#44395C", "border":"#776A8D", "accent":"#D3A5FF",
        "accent_hover":"#E1C0FF", "accent2":"#F1D8FF", "text":"#FFFFFF", "muted":"#E7DDF0",
        "disabled":"#B2A6BE", "danger":"#FF82AA", "success":"#7AD9B4", "dialog":"#302841",
        "field":"#3D344E", "paper":"#FBF6FF", "ink":"#4D3568", "selection_text":"#23172F",
    },
    "Soft Pink": {
        "bg1":"#3A1B32", "bg2":"#73365A", "sidebar":"#261020", "surface":"#45243A",
        "surface_alt":"#512B45", "card":"#5C344F", "border":"#8C607C", "accent":"#FF8DD3",
        "accent_hover":"#FFA9DF", "accent2":"#FFD2F0", "text":"#FFF9FE", "muted":"#F0D8E9",
        "disabled":"#BDA0B4", "danger":"#FF759E", "success":"#7AD7B5", "dialog":"#321A2B",
        "field":"#503448", "paper":"#FFF6FC", "ink":"#5A2248", "selection_text":"#2A1021",
    },
    "Midnight Rose": {
        "bg1":"#090711", "bg2":"#26112D", "sidebar":"#06040B", "surface":"#17101D",
        "surface_alt":"#211528", "card":"#2A1932", "border":"#533E5B", "accent":"#F95DCE",
        "accent_hover":"#FF84DC", "accent2":"#AA88FF", "text":"#FDF8FF", "muted":"#C8B8D1",
        "disabled":"#8D7B96", "danger":"#FF667D", "success":"#72D7AF", "dialog":"#17101D",
        "field":"#241B2A", "paper":"#FFF2F8", "ink":"#45163F", "selection_text":"#100815",
    },
}


def validate_themes() -> bool:
    return all(REQUIRED_THEME_TOKENS.issubset(theme) for theme in THEMES.values())


def stylesheet(theme_name: str, font_size: int = 10) -> str:
    c = THEMES.get(theme_name, THEMES["Pink Crystal"])
    # QSS intentionally scopes surfaces and viewports instead of setting a solid
    # background on every QWidget.  This avoids white native viewports while
    # preserving transparent child widgets inside cards.
    return f"""
    * {{ outline: none; }}
    QWidget {{ color:{c['text']}; font-family:'Segoe UI'; font-size:{font_size}pt; }}
    QMainWindow, QWidget#Root {{
        background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c['bg1']},stop:1 {c['bg2']});
    }}
    QWidget#AppContent, QWidget#PageRoot, QWidget#ScrollViewport,
    QWidget#SettingsPageViewport, QWidget#SidebarViewport {{ background: transparent; }}

    QFrame#Sidebar {{ background:{c['sidebar']}; border-right:1px solid {c['border']}; }}
    QLabel#Brand {{ color:{c['text']}; font-size:20pt; font-weight:800; letter-spacing:2px; }}
    QLabel#SidebarSubtitle {{ color:{c['muted']}; font-size:9pt; }}
    QLabel#NavGroup {{ color:{c['accent2']}; font-size:8.5pt; font-weight:700; padding:12px 10px 4px 10px; }}
    QPushButton#NavGroupButton {{
        min-height:26px; text-align:left; border:none; border-radius:7px; padding:8px 9px 3px 9px;
        background:transparent; color:{c['accent2']}; font-size:8.5pt; font-weight:700;
    }}
    QPushButton#NavGroupButton:hover {{ background:{c['surface']}; color:{c['text']}; }}
    QPushButton#NavGroupButton:checked {{ color:{c['accent2']}; }}
    QPushButton#Nav {{
        min-height:34px; text-align:left; border:none; border-radius:9px; padding:6px 11px;
        background:transparent; color:{c['muted']};
    }}
    QPushButton#Nav:hover {{ background:{c['surface_alt']}; color:{c['text']}; }}
    QPushButton#Nav:checked {{ background:{c['card']}; color:{c['text']}; border-left:3px solid {c['accent']}; font-weight:650; }}

    QFrame#Topbar {{ background:{c['surface']}; border-bottom:1px solid {c['border']}; }}
    QLineEdit#GlobalSearch {{ background:{c['field']}; border:1px solid {c['border']}; border-radius:12px; padding:8px 12px; }}
    QPushButton#IconButton {{ min-width:38px; max-width:38px; min-height:38px; max-height:38px; border-radius:12px; padding:0px; }}

    QLabel#Title {{ color:{c['text']}; font-size:22pt; font-weight:750; }}
    QLabel#Subtitle, QLabel#Muted {{ color:{c['muted']}; }}
    QLabel#SectionTitle {{ color:{c['text']}; font-size:15pt; font-weight:700; }}
    QLabel#CardTitle {{ color:{c['text']}; font-size:11.5pt; font-weight:700; }}
    QLabel#Metric {{ color:{c['accent2']}; font-size:20pt; font-weight:750; }}

    QFrame#Card, QFrame#SectionCard, QFrame#MetricCard, QGroupBox {{
        background:{c['card']}; border:1px solid {c['border']}; border-radius:14px;
    }}
    QGroupBox {{ margin-top:12px; padding:18px 14px 14px 14px; font-weight:650; }}
    QGroupBox::title {{ subcontrol-origin:margin; left:14px; padding:0 7px; color:{c['text']}; background:{c['card']}; }}
    QFrame#ActionBar {{ background:{c['surface']}; border:1px solid {c['border']}; border-radius:12px; }}

    QPushButton {{
        min-height:36px; background:{c['surface_alt']}; color:{c['text']}; border:1px solid {c['border']};
        border-radius:10px; padding:0 13px;
    }}
    QPushButton:hover {{ background:{c['card']}; border-color:{c['accent']}; }}
    QPushButton:pressed {{ background:{c['surface']}; }}
    QPushButton:disabled {{ color:{c['disabled']}; background:{c['surface']}; border-color:{c['border']}; }}
    QPushButton#Primary, QPushButton[variant="primary"] {{ background:{c['accent']}; color:{c['selection_text']}; border:none; font-weight:700; }}
    QPushButton#Primary:hover, QPushButton[variant="primary"]:hover {{ background:{c['accent_hover']}; }}
    QPushButton#Danger, QPushButton[variant="danger"] {{ border-color:{c['danger']}; color:{c['danger']}; }}
    QPushButton[variant="ghost"] {{ background:transparent; border-color:transparent; }}

    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    QSpinBox, QDoubleSpinBox {{
        min-height:36px; background:{c['field']}; color:{c['text']}; border:1px solid {c['border']};
        border-radius:9px; padding:0 10px; selection-background-color:{c['accent']}; selection-color:{c['selection_text']};
    }}
    QTextEdit, QPlainTextEdit {{ padding:9px 10px; }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus,
    QTimeEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{ border:1px solid {c['accent']}; }}
    QComboBox::drop-down {{ width:30px; border:none; }}
    QComboBox QAbstractItemView, QListView {{
        background:{c['dialog']}; color:{c['text']}; border:1px solid {c['border']};
        selection-background-color:{c['accent']}; selection-color:{c['selection_text']}; padding:4px;
    }}
    QCheckBox {{ spacing:8px; }}
    QCheckBox::indicator {{ width:17px; height:17px; border-radius:5px; border:1px solid {c['border']}; background:{c['field']}; }}
    QCheckBox::indicator:checked {{ background:{c['accent']}; border-color:{c['accent']}; }}

    QTabWidget::pane {{ border:1px solid {c['border']}; border-radius:12px; background:{c['surface']}; top:-1px; }}
    QTabBar::tab {{
        min-height:32px; background:{c['surface_alt']}; color:{c['muted']}; border:1px solid {c['border']};
        border-bottom:none; border-top-left-radius:9px; border-top-right-radius:9px; padding:4px 13px; margin-right:4px;
    }}
    QTabBar::tab:hover {{ color:{c['text']}; border-color:{c['accent2']}; }}
    QTabBar::tab:selected {{ background:{c['card']}; color:{c['text']}; border-color:{c['accent']}; font-weight:700; }}

    QListWidget#SettingsNav {{ background:{c['surface']}; border:1px solid {c['border']}; border-radius:12px; padding:6px; }}
    QListWidget#SettingsNav::item {{ min-height:36px; border-radius:8px; padding:4px 9px; color:{c['muted']}; }}
    QListWidget#SettingsNav::item:hover {{ background:{c['surface_alt']}; color:{c['text']}; }}
    QListWidget#SettingsNav::item:selected {{ background:{c['card']}; color:{c['text']}; border-left:3px solid {c['accent']}; }}

    QTableWidget, QTableView, QTreeWidget, QListWidget {{
        background:{c['surface']}; alternate-background-color:{c['surface_alt']}; color:{c['text']};
        border:1px solid {c['border']}; border-radius:10px; selection-background-color:{c['accent']};
        selection-color:{c['selection_text']}; gridline-color:{c['border']};
    }}
    QTableWidget::item, QTableView::item, QTreeWidget::item, QListWidget::item {{ padding:6px; }}
    QHeaderView::section {{ background:{c['surface_alt']}; color:{c['text']}; padding:8px; border:none; border-right:1px solid {c['border']}; font-weight:700; }}
    QTableCornerButton::section {{ background:{c['surface_alt']}; border:none; }}

    QScrollArea, QAbstractScrollArea {{ border:none; background:transparent; }}
    QScrollArea > QWidget > QWidget, QAbstractScrollArea QWidget#qt_scrollarea_viewport {{ background:transparent; }}
    QScrollBar:vertical {{ background:transparent; width:11px; margin:2px; }}
    QScrollBar::handle:vertical {{ background:{c['border']}; border-radius:5px; min-height:30px; }}
    QScrollBar::handle:vertical:hover {{ background:{c['accent2']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
    QScrollBar:horizontal {{ background:transparent; height:11px; margin:2px; }}
    QScrollBar::handle:horizontal {{ background:{c['border']}; border-radius:5px; min-width:30px; }}
    QScrollBar::handle:horizontal:hover {{ background:{c['accent2']}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}

    QProgressBar {{ border:1px solid {c['border']}; border-radius:9px; background:{c['surface']}; text-align:center; min-height:20px; }}
    QProgressBar::chunk {{ border-radius:8px; background:{c['accent']}; }}

    QCalendarWidget QWidget {{ background:{c['surface']}; color:{c['text']}; }}
    QCalendarWidget QToolButton {{ color:{c['text']}; background:{c['surface_alt']}; border:none; border-radius:8px; margin:3px; }}
    QCalendarWidget QAbstractItemView {{ background:{c['surface']}; color:{c['text']}; selection-background-color:{c['accent']}; selection-color:{c['selection_text']}; }}

    QDialog, QMessageBox, QWizard, QWizardPage, QMenu {{ background:{c['dialog']}; color:{c['text']}; }}
    QMenu {{ border:1px solid {c['border']}; padding:5px; }}
    QMenu::item {{ padding:7px 22px 7px 12px; border-radius:7px; }}
    QMenu::item:selected {{ background:{c['accent']}; color:{c['selection_text']}; }}
    QToolTip {{ background:{c['dialog']}; color:{c['text']}; border:1px solid {c['accent']}; padding:5px; }}

    QPlainTextEdit#DiaryPaper {{
        background:{c['paper']}; color:{c['ink']}; border:2px solid {c['accent']}; border-radius:12px;
        padding:18px; font-family:'Segoe Print','Ink Free','Gabriola',cursive; font-size:14pt;
    }}
    """
