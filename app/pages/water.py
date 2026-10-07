from __future__ import annotations
from datetime import date,timedelta
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout,QHBoxLayout,QLabel,QProgressBar,QPushButton,QTableWidget,QTableWidgetItem
from .base import Page

class WaterPage(Page):
    changed=Signal()
    def __init__(self,db,i18n):
        super().__init__(); self.db=db; self.i18n=i18n
        self.total=QLabel(); self.total.setObjectName('Metric'); self.progress=QProgressBar(); self.layout_root.addWidget(self.total); self.layout_root.addWidget(self.progress)
        row=QHBoxLayout(); self.buttons=[]
        for amount in (150,250,350,500): b=QPushButton(f'+ {amount} ml'); b.clicked.connect(lambda _=False,a=amount:self.add(a)); row.addWidget(b); self.buttons.append(b)
        row.addStretch(); self.layout_root.addLayout(row)
        self.week_label=QLabel(); self.layout_root.addWidget(self.week_label); self.week_grid=QGridLayout(); self.week_bars=[]
        for i in range(7):
            lab=QLabel(); bar=QProgressBar(); bar.setTextVisible(True); self.week_grid.addWidget(lab,0,i); self.week_grid.addWidget(bar,1,i); self.week_bars.append((lab,bar))
        self.layout_root.addLayout(self.week_grid)
        self.table=QTableWidget(0,2); self.layout_root.addWidget(self.table,1); self.retranslate(); self.refresh()
    def retranslate(self): self.title_label.setText(self.i18n.t('page.water')); self.subtitle_label.setText('Registro local de hidratación con objetivo, historial y semana.' if self.i18n.language=='es' else 'Local hydration log with goal, history and week view.'); self.table.setHorizontalHeaderLabels(['ml','Fecha'] if self.i18n.language=='es' else ['ml','Date']); self.week_label.setText('Últimos 7 días' if self.i18n.language=='es' else 'Last 7 days')
    def add(self,amount): self.db.execute('INSERT INTO water(amount_ml,recorded_at) VALUES(?,?)',(amount,self.db.now())); self.db.audit('ADD_WATER','water',None,str(amount)); self.refresh(); self.changed.emit()
    def refresh(self):
        today=date.today(); today_s=today.isoformat(); total=int(self.db.one('SELECT COALESCE(SUM(amount_ml),0) FROM water WHERE substr(recorded_at,1,10)=?',(today_s,))[0]); goal=max(1,int(self.db.setting('water_goal','2000') or 2000)); self.total.setText(f'{total} / {goal} ml'); self.progress.setRange(0,goal); self.progress.setValue(min(total,goal))
        for i,(lab,bar) in enumerate(self.week_bars):
            d=today-timedelta(days=6-i); amount=int(self.db.one('SELECT COALESCE(SUM(amount_ml),0) FROM water WHERE substr(recorded_at,1,10)=?',(d.isoformat(),))[0]); lab.setText(d.strftime('%a')); bar.setRange(0,goal); bar.setValue(min(amount,goal)); bar.setFormat(f'{amount}')
        rows=self.db.all('SELECT amount_ml,recorded_at FROM water ORDER BY id DESC LIMIT 40'); self.table.setRowCount(len(rows))
        for r,row in enumerate(rows): self.table.setItem(r,0,QTableWidgetItem(str(row[0]))); self.table.setItem(r,1,QTableWidgetItem(str(row[1])))
