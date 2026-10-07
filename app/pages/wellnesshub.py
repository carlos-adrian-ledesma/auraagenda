from __future__ import annotations
from PySide6.QtWidgets import QLabel,QTabWidget
from .base import Page
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class WellnessPage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.i18n=i18n; self.notice=QLabel(); self.notice.setWordWrap(True); self.layout_root.addWidget(self.notice); self.tabs=QTabWidget(); self.layout_root.addWidget(self.tabs,1)
        self.symptoms=GenericCrudPage(db,i18n,'page.wellness','Síntomas opcionales.','Optional symptoms.','wellness_logs',['log_date','pain','energy','mood','sleep','stress'],[F('log_date','Fecha','Date','date',required=True),F('pain','Dolor 0-10','Pain 0-10','int'),F('energy','Energía 0-10','Energy 0-10','int'),F('mood','Humor 0-10','Mood 0-10','int'),F('sleep','Sueño 0-10','Sleep 0-10','int'),F('stress','Estrés 0-10','Stress 0-10','int'),F('appetite','Apetito 0-10','Appetite 0-10','int'),F('skin','Piel','Skin'),F('migraine','Migraña 0-10','Migraine 0-10','int'),F('bloating','Hinchazón 0-10','Bloating 0-10','int'),F('custom_symptoms','Otros','Other'),F('notes','Notas','Notes','multiline')],'log_date DESC')
        self.health=GenericCrudPage(db,i18n,'page.wellness','Citas y recordatorios de salud.','Health appointments and reminders.','health_items',['item_type','title','event_date','provider','medication'],[F('item_type','Tipo','Type','combo',('Cita médica','Ginecología','Odontología','Dermatología','Control','Medicación','Estudio','Nota')),F('title','Título','Title',required=True),F('event_date','Fecha','Date','date'),F('reminder_at','Recordatorio','Reminder'),F('provider','Profesional o lugar','Provider or place'),F('medication','Medicación','Medication'),F('notes','Notas','Notes','multiline')],'event_date DESC')
        self.symptoms.header.hide(); self.health.header.hide(); self.symptoms.layout_root.setContentsMargins(12,12,12,12); self.health.layout_root.setContentsMargins(12,12,12,12); self.tabs.addTab(self.symptoms,''); self.tabs.addTab(self.health,''); self.retranslate()
    def retranslate(self):
        self.title_label.setText(self.i18n.t('page.wellness')); self.subtitle_label.setText('Centro opcional de bienestar y organización de salud.' if self.i18n.language=='es' else 'Optional wellness and health organization center.'); self.notice.setText('⚕ '+self.i18n.t('health.disclaimer')); self.tabs.setTabText(0,'Síntomas y bienestar' if self.i18n.language=='es' else 'Symptoms and wellness'); self.tabs.setTabText(1,'Salud' if self.i18n.language=='es' else 'Health'); self.symptoms.retranslate(); self.health.retranslate()
    def refresh(self): self.symptoms.refresh(); self.health.refresh()
    def add_record(self): self.symptoms.add_record()
