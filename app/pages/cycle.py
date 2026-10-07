from __future__ import annotations
from datetime import date,timedelta
from PySide6.QtWidgets import QLabel
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class CyclePage(GenericCrudPage):
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.cycle','Registro opcional de ciclo. Las predicciones son estimaciones de organización personal.','Optional cycle log. Predictions are personal organization estimates.','cycle_records',['start_date','end_date','duration_days','intensity','symptoms'],[F('start_date','Inicio','Start','date',required=True),F('end_date','Final','End','date'),F('duration_days','Duración (días)','Duration (days)','int'),F('intensity','Intensidad','Intensity','combo',('Low','Medium','High')),F('symptoms','Síntomas','Symptoms','multiline'),F('notes','Notas','Notes','multiline')],'start_date DESC')
        self.estimate=QLabel(); self.estimate.setWordWrap(True); self.layout_root.insertWidget(3,self.estimate); self.refresh()
    def refresh(self):
        super().refresh()
        if not hasattr(self,'estimate'):return
        rows=self.db.all("SELECT start_date FROM cycle_records WHERE deleted=0 ORDER BY start_date DESC LIMIT 6")
        dates=[]
        for r in rows:
            try: dates.append(date.fromisoformat(r['start_date']))
            except Exception: pass
        if len(dates)>=2:
            diffs=[(dates[i]-dates[i+1]).days for i in range(len(dates)-1) if 15 <= (dates[i]-dates[i+1]).days <= 60]
            if diffs:
                avg=round(sum(diffs)/len(diffs)); nxt=dates[0]+timedelta(days=avg); prefix='Próxima fecha estimada' if self.i18n.language=='es' else 'Estimated next date'; self.estimate.setText(f'≈ {prefix}: {nxt.isoformat()} · {avg} días/days · '+self.i18n.t('health.disclaimer')); return
        self.estimate.setText(self.i18n.t('health.disclaimer'))
