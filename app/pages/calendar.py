from __future__ import annotations
from datetime import date,timedelta
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCalendarWidget,QHBoxLayout,QPushButton,QTableWidgetItem
from .generic import GenericCrudPage
from ..widgets import FieldSpec

CAL_FIELDS=[
 FieldSpec('title','Título','Title',required=True),FieldSpec('event_date','Fecha','Date','date',required=True),FieldSpec('start_time','Hora de inicio','Start time','time',default='09:00'),FieldSpec('end_time','Hora final','End time','time',default='10:00'),
 FieldSpec('all_day','Todo el día','All day','bool'),FieldSpec('category','Categoría','Category','combo',('Personal','Trabajo','Salud','Belleza','Familia','Social','Estudios','Viajes','Compras','Trámites','Otros'),default='Personal'),FieldSpec('color','Color','Color'),FieldSpec('priority','Prioridad','Priority','combo',('Low','Normal','High','Urgent'),default='Normal'),FieldSpec('location','Lugar','Location'),FieldSpec('description','Descripción','Description','multiline'),FieldSpec('reminder_minutes','Recordatorio (min)','Reminder (min)','int'),FieldSpec('repeat_rule','Repetición','Repeat','combo',('once','daily','weekly','monthly','yearly','custom'),default='once'),FieldSpec('repeat_detail','Detalle de repetición','Repeat detail'),FieldSpec('status','Estado','Status','combo',('pending','in_progress','done','rescheduled','cancelled'),default='pending')]

class CalendarPage(GenericCrudPage):
    def __init__(self,db,i18n):
        self.mode='month'; super().__init__(db,i18n,'page.calendar','Vista Día, Semana, Mes y Lista para eventos, citas y recordatorios.','Day, Week, Month and List views for events, appointments and reminders.','agenda',['event_date','start_time','title','category','location','repeat_rule','status'],CAL_FIELDS,'event_date ASC,start_time ASC')
        modes=QHBoxLayout(); self.mode_buttons={}
        for mode,key in [('day','calendar.day'),('week','calendar.week'),('month','calendar.month'),('list','calendar.list')]:
            b=QPushButton(); b.setCheckable(True); b.clicked.connect(lambda _=False,m=mode:self.set_mode(m)); modes.addWidget(b); self.mode_buttons[mode]=(b,key)
        modes.addStretch(); self.layout_root.insertLayout(3,modes)
        self.calendar=QCalendarWidget(); self.calendar.selectionChanged.connect(self.refresh); self.layout_root.insertWidget(4,self.calendar); self.set_mode('month'); self.retranslate()
    def retranslate(self):
        super().retranslate()
        if hasattr(self,'mode_buttons'):
            for m,(b,k) in self.mode_buttons.items(): b.setText(self.i18n.t(k))
    def set_mode(self,mode):
        self.mode=mode
        if hasattr(self,'calendar'): self.calendar.setVisible(mode!='list')
        if hasattr(self,'mode_buttons'):
            for m,(b,_) in self.mode_buttons.items(): b.setChecked(m==mode)
        self.refresh()
    def refresh(self):
        if not hasattr(self,'table_widget'): return
        selected=self.calendar.selectedDate().toPython() if hasattr(self,'calendar') else date.today(); params=[]; clauses=['deleted=0']
        if self.mode=='day': clauses.append('event_date=?'); params.append(selected.isoformat())
        elif self.mode=='week':
            start=selected-timedelta(days=selected.weekday()); end=start+timedelta(days=6); clauses.append('event_date BETWEEN ? AND ?'); params.extend([start.isoformat(),end.isoformat()])
        elif self.mode=='month': clauses.append('substr(event_date,1,7)=?'); params.append(selected.strftime('%Y-%m'))
        term=self.search.text().strip() if hasattr(self,'search') else ''
        if term: clauses.append('(title LIKE ? OR category LIKE ? OR location LIKE ? OR description LIKE ?)'); params.extend([f'%{term}%']*4)
        rows=self.db.all('SELECT * FROM agenda WHERE '+' AND '.join(clauses)+' ORDER BY event_date,start_time',params)
        self.table_widget.setColumnCount(len(self.columns)+1); self.table_widget.setHorizontalHeaderLabels(['ID']+[self.field_label(c) for c in self.columns]); self.table_widget.setRowCount(len(rows))
        for r,row in enumerate(rows):
            self.table_widget.setItem(r,0,QTableWidgetItem(str(row['id'])))
            for c,name in enumerate(self.columns,1):
                val=row[name] if row[name] is not None else ''
                if name in {'category','repeat_rule','status'}: val=self.i18n.choice(str(val))
                self.table_widget.setItem(r,c,QTableWidgetItem(str(val)))
        self.table_widget.resizeColumnsToContents()
