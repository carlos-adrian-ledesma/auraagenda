from __future__ import annotations
from datetime import date,timedelta
from PySide6.QtWidgets import QHBoxLayout,QLabel,QPushButton
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class HabitsPage(GenericCrudPage):
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.habits','Hábitos recurrentes con rachas y progreso semanal/mensual.','Recurring habits with streaks and weekly/monthly progress.','habits',['name','frequency','days','target','unit','active'],[F('name','Nombre','Name',required=True),F('frequency','Frecuencia','Frequency','combo',('daily','weekly','custom'),default='daily'),F('days','Días','Days'),F('target','Objetivo','Target','double',default='1'),F('unit','Unidad','Unit'),F('color','Color','Color'),F('icon','Icono','Icon'),F('active','Activo','Active','bool',default='1')],'id DESC')
        row=QHBoxLayout(); self.mark_btn=QPushButton(); self.stats=QLabel(); self.stats.setWordWrap(True); row.addWidget(self.mark_btn); row.addWidget(self.stats,1); self.layout_root.addLayout(row); self.mark_btn.clicked.connect(self.mark_today); self.table_widget.itemSelectionChanged.connect(self.refresh_stats); self.retranslate()
    def retranslate(self): super().retranslate(); self.mark_btn.setText('✓ Hoy' if self.i18n.language=='es' else '✓ Today') if hasattr(self,'mark_btn') else None; self.refresh_stats() if hasattr(self,'stats') else None
    def refresh(self): super().refresh(); self.refresh_stats()
    def mark_today(self):
        hid=self.selected_id()
        if not hid:return
        today=date.today().isoformat(); self.db.execute('INSERT INTO habit_logs(habit_id,log_date,value,note,created_at) VALUES(?,?,?,?,?) ON CONFLICT(habit_id,log_date) DO UPDATE SET value=excluded.value',(hid,today,1,'',self.db.now())); self.refresh_stats(); self.changed.emit()
    def refresh_stats(self):
        if not hasattr(self,'stats'):return
        hid=self.selected_id()
        if not hid:self.stats.setText('');return
        rows={r['log_date'] for r in self.db.all('SELECT log_date FROM habit_logs WHERE habit_id=? AND value>0 ORDER BY log_date',(hid,))}; today=date.today(); streak=0; d=today
        while d.isoformat() in rows:streak+=1;d-=timedelta(days=1)
        best=0;cur=0;prev=None
        for ds in sorted(rows):
            dt=date.fromisoformat(ds);cur=cur+1 if prev and dt-prev==timedelta(days=1) else 1;best=max(best,cur);prev=dt
        week=sum(1 for i in range(7) if (today-timedelta(days=i)).isoformat() in rows);month=sum(1 for ds in rows if ds.startswith(today.strftime('%Y-%m')))
        self.stats.setText(f'Racha: {streak} · Mejor: {best} · Semana: {week/7*100:.0f}% · Mes: {month}/{today.day}' if self.i18n.language=='es' else f'Streak: {streak} · Best: {best} · Week: {week/7*100:.0f}% · Month: {month}/{today.day}')
