from __future__ import annotations
from datetime import date,datetime,timedelta
from PySide6.QtCore import QTimer,Qt
from PySide6.QtGui import QAction,QIcon
from PySide6.QtWidgets import QApplication,QDialog,QFrame,QHBoxLayout,QLabel,QLineEdit,QListWidget,QMainWindow,QMenu,QMessageBox,QPushButton,QScrollArea,QStackedWidget,QSystemTrayIcon,QVBoxLayout,QWidget
from .database import Database
from .i18n import I18n
from .pages import BackupPage,CalendarPage,DashboardPage,DiaryPage,GenericCrudPage,SettingsPage,StatisticsPage,TrashPage,WaterPage
from .pages.finance import FinancePage
from .pages.stylehub import StylePage
from .pages.wellnesshub import WellnessPage
from .pages.filepages import LibraryPage,MultimediaPage
from .pages.lists import ListsPage
from .pages.habits import HabitsPage
from .pages.cycle import CyclePage
from .pages.mood import MoodPage
from .pages.catalog import catalog
from .paths import DISPLAY_NAME,SUBTITLE,VERSION,resource_path
from .styles import stylesheet
from .design_system import SIZING

NAV_GROUPS=[
 ('nav.home',[('dashboard','page.dashboard')]),
 ('nav.organization',[('calendar','page.calendar'),('tasks','page.tasks'),('alarms','page.alarms'),('habits','page.habits'),('lists','page.lists')]),
 ('nav.personal',[('diary','page.diary'),('writing','page.writing'),('people','page.people'),('goals','page.goals')]),
 ('nav.wellness',[('wellness','page.wellness'),('cycle','page.cycle'),('water','page.water'),('sleep','page.sleep'),('mood','page.mood'),('selfcare','page.selfcare')]),
 ('nav.style',[('beauty','page.beauty'),('style','page.style')]),
 ('nav.life',[('finance','page.finance'),('travel','page.travel'),('library','page.library'),('multimedia','page.multimedia')]),
 ('nav.system',[('statistics','page.statistics'),('backup','page.backup'),('trash','page.trash'),('settings','page.settings')]),
]
OPTIONAL_MAP={'cycle':'module_cycle','sleep':'module_sleep','mood':'module_mood','beauty':'module_beauty','style':'module_style','multimedia':'module_multimedia'}

class MainWindow(QMainWindow):
    def __init__(self,db:Database,i18n:I18n):
        super().__init__(); self.db=db; self.i18n=i18n; self._allow_quit=False; self.pages={}; self.nav_buttons={}; self.group_labels={}; self.group_items={}
        self.setMinimumSize(1024,640); self.resize(1366,768); self.setWindowIcon(QIcon(str(resource_path('assets/AuraAgenda.ico'))))
        root=QWidget(); root.setObjectName('Root'); self.setCentralWidget(root); outer=QHBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        sidebar=QFrame(); sidebar.setObjectName('Sidebar'); sidebar.setFixedWidth(SIZING['sidebar_width']); sl=QVBoxLayout(sidebar); sl.setContentsMargins(14,16,12,12); sl.setSpacing(4)
        self.brand=QLabel('AURA\nAGENDA'); self.brand.setObjectName('Brand'); self.sub=QLabel(SUBTITLE); self.sub.setObjectName('SidebarSubtitle'); sl.addWidget(self.brand); sl.addWidget(self.sub)
        nav_scroll=QScrollArea(); nav_scroll.setObjectName('SidebarScroll'); nav_scroll.setWidgetResizable(True); nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); nav_host=QWidget(); nav_host.setObjectName('SidebarViewport'); self.nav_layout=QVBoxLayout(nav_host); self.nav_layout.setContentsMargins(0,10,0,0); self.nav_layout.setSpacing(3); nav_scroll.setWidget(nav_host); sl.addWidget(nav_scroll,1)
        self.version_label=QLabel(); self.version_label.setObjectName('SidebarSubtitle'); sl.addWidget(self.version_label); outer.addWidget(sidebar)
        right=QWidget(); right.setObjectName('AppContent'); rv=QVBoxLayout(right); rv.setContentsMargins(0,0,0,0); rv.setSpacing(0); top=QFrame(); top.setObjectName('Topbar'); top.setFixedHeight(SIZING['topbar_height']); th=QHBoxLayout(top); th.setContentsMargins(18,9,18,9); th.setSpacing(10); self.global_search=QLineEdit(); self.global_search.setObjectName('GlobalSearch'); self.global_search.setMaximumWidth(760); self.global_search.returnPressed.connect(self.search_global); self.notify_btn=QPushButton('🔔'); self.notify_btn.setObjectName('IconButton'); self.notify_btn.setAccessibleName('Notifications'); self.notify_btn.clicked.connect(self.show_notifications); th.addWidget(self.global_search,1); th.addStretch(0); th.addWidget(self.notify_btn); rv.addWidget(top); self.stack=QStackedWidget(); self.stack.setObjectName('ContentStack'); rv.addWidget(self.stack,1); outer.addWidget(right,1)
        self._build_pages(); self._build_nav(); self.settings.theme_changed.connect(self.apply_theme); self.settings.language_changed.connect(self.retranslate_all); self.settings.settings_changed.connect(self.apply_module_visibility); self.dashboard.quick_action.connect(self.quick_action)
        for p in self.pages.values():
            if hasattr(p,'changed'): p.changed.connect(self.refresh_summary)
        self.setup_tray(); self.alarm_timer=QTimer(self); self.alarm_timer.timeout.connect(self.check_alarms); self.alarm_timer.start(30000); self.retranslate_all(self.i18n.language); self.apply_theme(self.db.setting('theme','Pink Crystal')); self.apply_module_visibility(); self.go('dashboard'); QTimer.singleShot(1000,self.check_alarms)

    def _build_pages(self):
        self.dashboard=DashboardPage(self.db,self.i18n); self.pages['dashboard']=self.dashboard; self.pages['calendar']=CalendarPage(self.db,self.i18n); self.pages['diary']=DiaryPage(self.db,self.i18n); self.pages['water']=WaterPage(self.db,self.i18n)
        self.pages['wellness']=WellnessPage(self.db,self.i18n); self.pages['style']=StylePage(self.db,self.i18n); self.pages['finance']=FinancePage(self.db,self.i18n); self.pages['library']=LibraryPage(self.db,self.i18n); self.pages['multimedia']=MultimediaPage(self.db,self.i18n); self.pages['lists']=ListsPage(self.db,self.i18n); self.pages['habits']=HabitsPage(self.db,self.i18n); self.pages['cycle']=CyclePage(self.db,self.i18n); self.pages['mood']=MoodPage(self.db,self.i18n)
        for key,spec in catalog().items():
            if key in self.pages: continue
            page_key,es,en,table,cols,fields,order=spec; self.pages[key]=GenericCrudPage(self.db,self.i18n,page_key,es,en,table,cols,fields,order)
        self.pages['statistics']=StatisticsPage(self.db,self.i18n); self.pages['backup']=BackupPage(self.db,self.i18n); self.pages['trash']=TrashPage(self.db,self.i18n); self.settings=SettingsPage(self.db,self.i18n); self.pages['settings']=self.settings
        for key,p in self.pages.items(): p.setProperty('page_id',key); self.stack.addWidget(p)

    def _build_nav(self):
        while self.nav_layout.count():
            item=self.nav_layout.takeAt(0); w=item.widget();
            if w: w.deleteLater()
        self.nav_buttons={}; self.group_labels={}; self.group_items={}
        for group,items in NAV_GROUPS:
            lab=QPushButton(); lab.setObjectName('NavGroupButton'); lab.setCheckable(True); lab.setChecked(True); lab.setProperty('expanded',True); lab.clicked.connect(lambda checked,g=group:self._toggle_group(g,checked)); self.nav_layout.addWidget(lab); self.group_labels[group]=lab; self.group_items[group]=[]
            for page_id,label_key in items:
                b=QPushButton(); b.setObjectName('Nav'); b.setCheckable(True); b.clicked.connect(lambda _=False,pid=page_id:self.go(pid)); self.nav_layout.addWidget(b); self.nav_buttons[page_id]=(b,label_key); self.group_items[group].append(page_id)
        self.nav_layout.addStretch()

    def _toggle_group(self, group, expanded):
        button=self.group_labels.get(group)
        if button is not None:
            button.setProperty('expanded',bool(expanded)); button.setText(('▾ ' if expanded else '▸ ')+self.i18n.t(group)); button.style().unpolish(button); button.style().polish(button)
        for pid in self.group_items.get(group,[]):
            nav=self.nav_buttons.get(pid)
            if not nav: continue
            visible=bool(expanded)
            optional=OPTIONAL_MAP.get(pid)
            if optional: visible=visible and self.db.setting(optional,'1')=='1'
            nav[0].setVisible(visible)

    def retranslate_all(self,language=None):
        if language: self.i18n.set_language(language)
        self.setWindowTitle(f'{DISPLAY_NAME} — {self.i18n.t("app.subtitle")}'); self.sub.setText(self.i18n.t('app.subtitle')); self.global_search.setPlaceholderText(self.i18n.t('ui.search_everything')); self.notify_btn.setToolTip(self.i18n.t('ui.notifications')); self.notify_btn.setAccessibleName(self.i18n.t('ui.notifications')); self.version_label.setText(f'Version {VERSION}\nLocal-first · Offline')
        for k,lab in self.group_labels.items(): lab.setText(('▾ ' if lab.isChecked() else '▸ ')+self.i18n.t(k))
        for pid,(b,key) in self.nav_buttons.items(): b.setText(self.i18n.t(key))
        for p in self.pages.values():
            if hasattr(p,'retranslate'): p.retranslate()
        self.refresh_tray_texts()

    def apply_module_visibility(self):
        for group,items in NAV_GROUPS:
            expanded=self.group_labels.get(group).isChecked() if group in self.group_labels else True
            for pid,_ in items:
                if pid not in self.nav_buttons: continue
                optional=OPTIONAL_MAP.get(pid)
                enabled=True if optional is None else self.db.setting(optional,'1')=='1'
                self.nav_buttons[pid][0].setVisible(expanded and enabled)
        self.refresh_summary()

    def go(self,page_id:str):
        page=self.pages.get(page_id)
        if page is None:return
        self.stack.setCurrentWidget(page)
        for pid,(b,_) in self.nav_buttons.items(): b.setChecked(pid==page_id)
        if hasattr(page,'refresh'): page.refresh()

    def quick_action(self,page_id):
        self.go(page_id)
        p=self.pages.get(page_id)
        if page_id=='water': p.add(250)
        elif hasattr(p,'add_record'): p.add_record()

    def refresh_summary(self):
        for pid in ('dashboard','statistics','water'):
            p=self.pages.get(pid)
            if p and hasattr(p,'refresh'): p.refresh()

    def apply_theme(self,name):
        app=QApplication.instance(); size=int(self.db.setting('font_size','10') or 10)
        if app: app.setStyleSheet(stylesheet(name,size))

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray_menu = QMenu()
        self.tray_show = QAction(self)
        self.tray_quit = QAction(self)
        self.tray_show.triggered.connect(self.show_normal)
        self.tray_quit.triggered.connect(self.quit_app)
        self.tray_menu.addAction(self.tray_show)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.tray_quit)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(
            lambda reason: self.show_normal() if reason == QSystemTrayIcon.DoubleClick else None
        )
        self.tray.show()
        self.refresh_tray_texts()

    def refresh_tray_texts(self):
        if not hasattr(self, "tray"):
            return
        self.tray_show.setText(self.i18n.t("tray.open"))
        self.tray_quit.setText(self.i18n.t("tray.exit"))
        self.tray.setToolTip(f'{DISPLAY_NAME} — {self.i18n.t("app.subtitle")}')

    def _show_unlocked(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def show_normal(self):
        controller = getattr(self, "_auto_lock_controller", None)
        if controller is not None:
            controller.request_show()
            return
        self._show_unlocked()

    def _notification_is_private(self) -> bool:
        controller = getattr(self, "_auto_lock_controller", None)
        if controller is not None and controller.locked:
            return True
        return self.db.setting("notification_privacy", "show_content") == "hide_sensitive"

    def show_tray_notification(self, title: str, body: str, sensitive: bool = True, timeout: int = 8000):
        if sensitive and self._notification_is_private():
            title = DISPLAY_NAME
            body = self.i18n.t("security.private_notification")
        self.tray.showMessage(title, body, QSystemTrayIcon.Information, timeout)

    def quit_app(self):
        self._allow_quit = True
        self.tray.hide()
        QApplication.quit()
    def closeEvent(self,event):
        if self._allow_quit or self.db.setting('minimize_to_tray','1')!='1': event.accept(); return
        event.ignore(); self.hide(); self.tray.showMessage(DISPLAY_NAME,self.i18n.t('tray.running'),QSystemTrayIcon.Information,2500)

    def check_alarms(self):
        from .timeutil import now_in_timezone
        now=now_in_timezone(self.db.setting('timezone','')); d=now.strftime('%Y-%m-%d'); t=now.strftime('%H:%M')
        rows=self.db.all("SELECT * FROM alarms WHERE deleted=0 AND enabled IN ('Yes','Sí') AND completed IN ('No','') AND alarm_date=? AND alarm_time=?",(d,t))
        for r in rows:
            if str(r['last_triggered'] or '').startswith(now.strftime('%Y-%m-%dT%H:%M')): continue
            self.show_tray_notification(str(r['name']), str(r['message'] or self.i18n.t('tray.running')), True, 8000)
            box=QMessageBox(self); box.setWindowTitle(str(r['name'])); box.setText(str(r['message'] or r['name'])); snooze=box.addButton(self.i18n.t('alarm.snooze_10'),QMessageBox.ActionRole); done=box.addButton(self.i18n.t('alarm.completed'),QMessageBox.AcceptRole); box.addButton(self.i18n.t('common.close'),QMessageBox.RejectRole); box.exec()
            clicked=box.clickedButton()
            if clicked==snooze:
                later=now+timedelta(minutes=10); self.db.execute('UPDATE alarms SET alarm_date=?,alarm_time=?,last_triggered=?,updated_at=? WHERE id=?',(later.strftime('%Y-%m-%d'),later.strftime('%H:%M'),self.db.now(),self.db.now(),r['id'])); continue
            if clicked==done:
                self.db.execute("UPDATE alarms SET completed='Yes',last_triggered=?,updated_at=? WHERE id=?",(self.db.now(),self.db.now(),r['id'])); continue
            rule=str(r['repeat_rule'] or 'once'); new_date=d; completed='No'; current=date.fromisoformat(d)
            if rule=='daily': new_date=(current+timedelta(days=1)).isoformat()
            elif rule=='weekly': new_date=(current+timedelta(days=7)).isoformat()
            elif rule=='monthly':
                month=current.month+1; year=current.year+(month>12); month=1 if month>12 else month
                import calendar as _cal; day=min(current.day,_cal.monthrange(year,month)[1]); new_date=date(year,month,day).isoformat()
            else: completed='Yes'
            self.db.execute('UPDATE alarms SET last_triggered=?,alarm_date=?,completed=?,updated_at=? WHERE id=?',(self.db.now(),new_date,completed,self.db.now(),r['id']))
        # Event reminders use the same local timezone but do not require a separate alarm record.
        events=self.db.all("SELECT * FROM agenda WHERE deleted=0 AND event_date=? AND reminder_minutes>0",(d,))
        for e in events:
            try:
                start=datetime.strptime(f"{e['event_date']} {e['start_time'] or '00:00'}",'%Y-%m-%d %H:%M'); current_naive=now.replace(tzinfo=None); trigger=start-timedelta(minutes=int(e['reminder_minutes'] or 0))
            except Exception:
                continue
            marker=str(e['last_reminded'] or '') if 'last_reminded' in e.keys() else ''
            if trigger <= current_naive < start and not marker.startswith(d):
                self.show_tray_notification(str(e['title']), str(e['description'] or e['location'] or self.i18n.t('page.calendar')), True, 8000); self.db.execute('UPDATE agenda SET last_reminded=?,updated_at=? WHERE id=?',(self.db.now(),self.db.now(),e['id']))

    def search_global(self):
        term=self.global_search.text().strip()
        if not term:return
        sources=[('agenda','title','calendar'),('tasks','title','tasks'),('diary','title','diary'),('people','name','people'),('goals','title','goals'),('lists','name','lists'),('library','title','library'),('multimedia','title','multimedia'),('beauty_products','name','beauty'),('wardrobe','name','style')]
        results=[]
        for table,col,pid in sources:
            try:
                for r in self.db.all(f'SELECT id,{col} AS label FROM {table} WHERE deleted=0 AND {col} LIKE ? LIMIT 8',(f'%{term}%',)): results.append((pid,table,r['id'],r['label']))
            except Exception: pass
        dlg=QDialog(self); dlg.setWindowTitle(self.i18n.t('common.search')); lay=QVBoxLayout(dlg); lst=QListWidget(); lay.addWidget(lst); mapping=[]
        for pid,table,rid,label in results: lst.addItem(f'{self.i18n.t("page."+pid)} · {label}'); mapping.append(pid)
        lst.itemDoubleClicked.connect(lambda item:(self.go(mapping[lst.row(item)]),dlg.accept())); dlg.resize(600,420); dlg.exec()

    def show_notifications(self):
        today=date.today().isoformat(); msgs=[]
        if self.db.setting('notify_tasks','1')=='1':
            overdue=self.db.all("SELECT title,due_date FROM tasks WHERE deleted=0 AND due_date<>'' AND due_date<? AND status NOT IN ('done','Finished') ORDER BY due_date LIMIT 8",(today,)); msgs += [f'⚠ {r["title"]} · {r["due_date"]}' for r in overdue]
        if self.db.setting('notify_events','1')=='1':
            upcoming=self.db.all('SELECT title,event_date,start_time FROM agenda WHERE deleted=0 AND event_date>=? ORDER BY event_date,start_time LIMIT 8',(today,)); msgs += [f'📅 {r["title"]} · {r["event_date"]} {r["start_time"] or ""}' for r in upcoming]
        if self.db.setting('notify_birthdays','1')=='1':
            mmdd=date.today().strftime('%m-%d'); people=self.db.all("SELECT name,birthday FROM people WHERE deleted=0 AND birthday<>'' ORDER BY birthday LIMIT 50")
            for r in people:
                if str(r['birthday'])[-5:]>=mmdd: msgs.append(f'🎂 {r["name"]} · {r["birthday"]}')
        if self.db.setting('notify_payments','1')=='1':
            payments=self.db.all("SELECT name,next_payment,amount,currency FROM subscriptions WHERE deleted=0 AND active=1 AND next_payment>=? ORDER BY next_payment LIMIT 5",(today,)); msgs += [f'💳 {r["name"]} · {r["next_payment"]} · {r["amount"]} {r["currency"] or ""}' for r in payments]
        if self.db.setting('notify_health','1')=='1':
            health=self.db.all("SELECT title,event_date FROM health_items WHERE deleted=0 AND event_date>=? ORDER BY event_date LIMIT 5",(today,)); msgs += [f'⚕ {r["title"]} · {r["event_date"]}' for r in health]
        QMessageBox.information(self,self.i18n.t('ui.notifications'),'\n'.join(msgs[:24]) if msgs else self.i18n.t('empty.records'))
