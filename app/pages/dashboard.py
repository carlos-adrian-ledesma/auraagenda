from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .base import Page


class MetricCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("MetricCard")
        self.setMinimumHeight(108)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 13, 16, 13)
        lay.setSpacing(4)
        self.caption = QLabel()
        self.caption.setObjectName("Muted")
        self.value = QLabel("0")
        self.value.setObjectName("Metric")
        self.detail = QLabel()
        self.detail.setObjectName("Muted")
        self.detail.setWordWrap(True)
        lay.addWidget(self.caption)
        lay.addWidget(self.value)
        lay.addWidget(self.detail)
        lay.addStretch(1)


class DashboardPage(Page):
    quick_action = Signal(str)

    def __init__(self, db, i18n):
        super().__init__()
        self.db = db
        self.i18n = i18n

        hero = QFrame()
        hero.setObjectName("SectionCard")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(18, 15, 18, 15)
        hero_layout.setSpacing(12)
        welcome_col = QVBoxLayout()
        welcome_col.setSpacing(3)
        self.welcome = QLabel()
        self.welcome.setObjectName("SectionTitle")
        self.clock = QLabel()
        self.clock.setObjectName("Muted")
        welcome_col.addWidget(self.welcome)
        welcome_col.addWidget(self.clock)
        hero_layout.addLayout(welcome_col, 1)
        self.layout_root.addWidget(hero)

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 1)
        self.cards = {}
        keys = ["events", "tasks", "overdue", "water", "balance", "habits", "sleep", "mood", "birthdays"]
        for i, key in enumerate(keys):
            card = MetricCard()
            self.cards[key] = card
            self.grid.addWidget(card, i // 3, i % 3)
        self.layout_root.addLayout(self.grid)

        quick_frame = QFrame()
        quick_frame.setObjectName("SectionCard")
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setContentsMargins(16, 13, 16, 16)
        quick_layout.setSpacing(10)
        self.quick_label = QLabel()
        self.quick_label.setObjectName("CardTitle")
        quick_layout.addWidget(self.quick_label)
        q = QGridLayout()
        q.setHorizontalSpacing(9)
        q.setVerticalSpacing(9)
        self.quick_buttons = {}
        items = [
            ("calendar", "＋"), ("tasks", "✓"), ("diary", "✒"), ("finance", "$"),
            ("water", "◉"), ("people", "♡"), ("habits", "★"),
        ]
        for i, (key, _icon) in enumerate(items):
            button = QPushButton()
            button.clicked.connect(lambda _=False, k=key: self.quick_action.emit(k))
            q.addWidget(button, i // 4, i % 4)
            self.quick_buttons[key] = button
        for col in range(4):
            q.setColumnStretch(col, 1)
        quick_layout.addLayout(q)
        self.layout_root.addWidget(quick_frame)
        self.layout_root.addStretch(1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)
        self.retranslate()
        self.refresh()

    def retranslate(self):
        self.title_label.setText(self.i18n.t("page.dashboard"))
        self.subtitle_label.setText(
            "Tu centro personal de organización" if self.i18n.language == "es"
            else "Your personal organization center"
        )
        self.quick_label.setText(self.i18n.t("dashboard.quick"))
        names = {
            "calendar": "+ " + self.i18n.t("page.calendar"),
            "tasks": "+ " + self.i18n.t("page.tasks"),
            "diary": "+ " + self.i18n.t("page.diary"),
            "finance": "+ " + self.i18n.t("page.finance"),
            "water": "+ " + self.i18n.t("page.water"),
            "people": "+ " + self.i18n.t("page.people"),
            "habits": "+ " + self.i18n.t("page.habits"),
        }
        for key, button in self.quick_buttons.items():
            button.setText(names[key])
        for key, card in self.cards.items():
            card.caption.setText(self.i18n.t("dashboard." + key))

    def refresh(self):
        today = date.today().isoformat()
        month = today[:7]
        name = self.db.setting("user_name", "Tu nombre") or (
            "Tu nombre" if self.i18n.language == "es" else "Your name"
        )
        phrase = self.db.setting("welcome_phrase", "")
        from ..timeutil import now_in_timezone
        now = now_in_timezone(self.db.setting("timezone", ""))
        self.welcome.setText(self.i18n.t("dashboard.welcome", name=name) + (f" · {phrase}" if phrase else ""))
        self.clock.setText(now.strftime("%A %d/%m/%Y · %H:%M"))

        def count(sql, params=()):
            row = self.db.one(sql, params)
            return int(row[0]) if row else 0

        events = count("SELECT COUNT(*) FROM agenda WHERE deleted=0 AND event_date=?", (today,))
        tasks = count("SELECT COUNT(*) FROM tasks WHERE deleted=0 AND status NOT IN ('done','Done','Finished','Completada')")
        overdue = count(
            "SELECT COUNT(*) FROM tasks WHERE deleted=0 AND due_date<>'' AND due_date<? "
            "AND status NOT IN ('done','Done','Finished','Completada')", (today,)
        )
        water = self.db.one(
            "SELECT COALESCE(SUM(amount_ml),0) FROM water WHERE substr(recorded_at,1,10)=?", (today,)
        )[0]
        goal = max(1, int(self.db.setting("water_goal", "2000") or 2000))
        fin = self.db.one(
            "SELECT COALESCE(SUM(CASE WHEN lower(txn_type) IN ('income','ingreso') THEN amount ELSE -amount END),0) "
            "FROM finance WHERE deleted=0 AND substr(txn_date,1,7)=?", (month,)
        )[0]
        habits = count("SELECT COUNT(*) FROM habits WHERE deleted=0 AND active=1")
        sleep = self.db.one(
            "SELECT AVG(hours) FROM sleep_logs WHERE deleted=0 AND sleep_date>=?",
            ((date.today() - timedelta(days=6)).isoformat(),),
        )
        sleep_value = float(sleep[0] or 0)
        mood = self.db.one("SELECT emotion FROM mood_logs WHERE deleted=0 ORDER BY recorded_at DESC LIMIT 1")
        mood_value = str(mood[0]) if mood else "—"
        birthdays = count("SELECT COUNT(*) FROM people WHERE deleted=0 AND birthday IS NOT NULL AND birthday<>''")
        values = {
            "events": str(events), "tasks": str(tasks), "overdue": str(overdue),
            "water": f"{int(water)} / {goal} ml",
            "balance": f"{float(fin):,.2f} {(self.db.setting('currency','') or '—')}",
            "habits": str(habits), "sleep": f"{sleep_value:.1f} h", "mood": mood_value,
            "birthdays": str(birthdays),
        }
        for key, value in values.items():
            self.cards[key].value.setText(value)
            self.cards[key].detail.setText("" if value not in {"0", "0.0 h"} else self.i18n.t("empty.records"))
