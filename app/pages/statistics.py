from __future__ import annotations
from datetime import date,timedelta
from PySide6.QtWidgets import QGridLayout,QLabel,QProgressBar
from .base import Page
from .dashboard import MetricCard
class StatisticsPage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.db=db; self.i18n=i18n; self.grid=QGridLayout(); self.cards={}
        for i,k in enumerate(['Tasks','Events','Water','Habits','Sleep','Mood','Finance','Diary','Wellness']): c=MetricCard(); c.caption.setText(k); self.cards[k]=c; self.grid.addWidget(c,i//3,i%3)
        self.layout_root.addLayout(self.grid); self.layout_root.addStretch(); self.retranslate(); self.refresh()
    def retranslate(self): self.title_label.setText(self.i18n.t('page.statistics')); self.subtitle_label.setText('Resumen de los últimos 30 días.' if self.i18n.language=='es' else 'Summary of the last 30 days.')
    def refresh(self):
        since=(date.today()-timedelta(days=29)).isoformat(); month=date.today().isoformat()[:7]
        q=lambda sql,p=(): self.db.one(sql,p)[0]
        vals={'Tasks':q("SELECT COUNT(*) FROM tasks WHERE deleted=0 AND status IN ('done','Finished','Completada')"),'Events':q('SELECT COUNT(*) FROM agenda WHERE deleted=0 AND event_date>=?',(since,)),'Water':q('SELECT COALESCE(SUM(amount_ml),0) FROM water WHERE substr(recorded_at,1,10)>=?',(since,)),'Habits':q('SELECT COUNT(*) FROM habit_logs WHERE log_date>=?',(since,)),'Sleep':round(float(q('SELECT COALESCE(AVG(hours),0) FROM sleep_logs WHERE deleted=0 AND sleep_date>=?',(since,))),1),'Mood':q('SELECT COUNT(*) FROM mood_logs WHERE deleted=0 AND substr(recorded_at,1,10)>=?',(since,)),'Finance':round(float(q("SELECT COALESCE(SUM(CASE WHEN lower(txn_type) IN ('income','ingreso') THEN amount ELSE -amount END),0) FROM finance WHERE deleted=0 AND substr(txn_date,1,7)=?",(month,))),2),'Diary':q('SELECT COUNT(*) FROM diary WHERE deleted=0 AND substr(created_at,1,10)>=?',(since,)),'Wellness':q('SELECT COUNT(*) FROM wellness_logs WHERE deleted=0 AND log_date>=?',(since,))}
        for k,v in vals.items(): self.cards[k].value.setText(str(v)); self.cards[k].detail.setText('' if v else self.i18n.t('empty.records'))
