from __future__ import annotations
from datetime import date,timedelta
from collections import Counter
from PySide6.QtWidgets import QLabel
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class MoodPage(GenericCrudPage):
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.mood','Emociones, intensidad, etiquetas y estadísticas semanales/mensuales.','Emotions, intensity, tags and weekly/monthly statistics.','mood_logs',['recorded_at','emotion','intensity','tags'],[F('emotion','Emoción','Emotion',required=True),F('intensity','Intensidad 1-10','Intensity 1-10','int'),F('recorded_at','Fecha/hora ISO','ISO date/time',required=True),F('note','Nota','Note','multiline'),F('tags','Etiquetas','Tags')],'recorded_at DESC')
        self.summary=QLabel(); self.summary.setWordWrap(True); self.layout_root.insertWidget(3,self.summary); self.refresh()
    def refresh(self):
        super().refresh()
        if not hasattr(self,'summary'):return
        since=(date.today()-timedelta(days=29)).isoformat(); rows=self.db.all("SELECT emotion,intensity,recorded_at FROM mood_logs WHERE deleted=0 AND substr(recorded_at,1,10)>=?",(since,)); c=Counter(str(r['emotion']) for r in rows if r['emotion']); avg=(sum(float(r['intensity'] or 0) for r in rows)/len(rows)) if rows else 0; top=c.most_common(1)[0][0] if c else '—'; self.summary.setText((f'30 días · emoción predominante: {top} · intensidad promedio: {avg:.1f}' if self.i18n.language=='es' else f'30 days · predominant emotion: {top} · average intensity: {avg:.1f}'))
