from __future__ import annotations
from PySide6.QtWidgets import QTabWidget
from .base import Page
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class StylePage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.i18n=i18n; self.tabs=QTabWidget(); self.layout_root.addWidget(self.tabs,1)
        self.wardrobe=GenericCrudPage(db,i18n,'page.style','Prendas y preferencias.','Wardrobe and preferences.','wardrobe',['name','category','color','season','occasion','brand','favorite'],[F('name','Prenda','Item',required=True),F('category','Categoría','Category'),F('color','Color','Color'),F('season','Estación','Season'),F('occasion','Ocasión','Occasion','combo',('Trabajo','Casual','Fiesta','Cena','Viaje','Gym','Invierno','Verano')),F('brand','Marca','Brand'),F('photo','Foto','Photo'),F('notes','Notas','Notes','multiline'),F('favorite','Favorito','Favorite','bool')],'id DESC')
        self.outfits=GenericCrudPage(db,i18n,'page.style','Outfits y planificación por evento.','Outfits and event planning.','outfits',['name','occasion','wear_date','favorite'],[F('name','Nombre','Name',required=True),F('item_ids','IDs de prendas','Item IDs'),F('occasion','Ocasión','Occasion'),F('wear_date','Fecha: ¿qué usé hoy?','Date: what did I wear today?','date'),F('photo','Foto','Photo'),F('favorite','Favorito','Favorite','bool'),F('notes','Notas','Notes','multiline')],'wear_date DESC')
        self.wardrobe.header.hide(); self.outfits.header.hide(); self.wardrobe.layout_root.setContentsMargins(12,12,12,12); self.outfits.layout_root.setContentsMargins(12,12,12,12); self.tabs.addTab(self.wardrobe,''); self.tabs.addTab(self.outfits,''); self.retranslate()
    def retranslate(self):
        self.title_label.setText(self.i18n.t('page.style')); self.subtitle_label.setText('Armario, outfits y planificación de estilo.' if self.i18n.language=='es' else 'Wardrobe, outfits and style planning.'); self.tabs.setTabText(0,'Prendas' if self.i18n.language=='es' else 'Wardrobe'); self.tabs.setTabText(1,'Outfits'); self.wardrobe.retranslate(); self.outfits.retranslate()
    def refresh(self): self.wardrobe.refresh(); self.outfits.refresh()
    def add_record(self): self.wardrobe.add_record()
