from __future__ import annotations
import shutil
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QHBoxLayout,QMessageBox,QPushButton
from .generic import GenericCrudPage
from ..widgets import FieldSpec
from ..paths import DATA_ROOT

FIELDS=[FieldSpec('title','Título','Title',required=True),FieldSpec('body','Texto','Text','multiline'),FieldSpec('category','Categoría','Category','combo',('Día de hoy','Gratitud','Reflexión','Objetivos','Carta','Sueños','Viaje','Momento especial'),default='Día de hoy'),FieldSpec('mood','Estado de ánimo','Mood'),FieldSpec('tags','Etiquetas','Tags'),FieldSpec('favorite','Favorito','Favorite','combo',('No','Yes'),default='No'),FieldSpec('privacy','Privacidad','Privacy','combo',('Normal','Private'),default='Normal'),FieldSpec('template','Plantilla','Template')]
class DiaryPage(GenericCrudPage):
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.diary','Diario personal con búsqueda, categorías, estados de ánimo y adjuntos.','Personal diary with search, categories, mood and attachments.','diary',['title','category','mood','favorite','updated_at'],FIELDS,'updated_at DESC')
        row=QHBoxLayout(); self.attach_btn=QPushButton(); self.open_btn=QPushButton(); self.export_btn=QPushButton(); row.addWidget(self.attach_btn); row.addWidget(self.open_btn); row.addWidget(self.export_btn); row.addStretch(); self.layout_root.insertLayout(3,row); self.attach_btn.clicked.connect(self.attach); self.open_btn.clicked.connect(self.show_attachments); self.export_btn.clicked.connect(self.export_txt); self.retranslate()
    def retranslate(self):
        super().retranslate()
        if hasattr(self,'attach_btn'):
            if self.i18n.language=='es': self.attach_btn.setText('📎 Adjuntar'); self.open_btn.setText('📂 Adjuntos'); self.export_btn.setText('⇩ Exportar TXT')
            else: self.attach_btn.setText('📎 Attach'); self.open_btn.setText('📂 Attachments'); self.export_btn.setText('⇩ Export TXT')
    def attach(self):
        rid=self.selected_id()
        if rid is None: QMessageBox.information(self,self.i18n.t('success.title'),'Selecciona una entrada.' if self.i18n.language=='es' else 'Select an entry.'); return
        files,_=QFileDialog.getOpenFileNames(self,'Adjuntar archivos' if self.i18n.language=='es' else 'Attach files')
        if not files:return
        folder=DATA_ROOT/'Diary'/'Attachments'/str(rid); folder.mkdir(parents=True,exist_ok=True)
        for f in files:
            src=Path(f); dest=folder/src.name; n=1
            while dest.exists(): dest=folder/f'{src.stem}_{n}{src.suffix}'; n+=1
            shutil.copy2(src,dest); kind=src.suffix.lower().lstrip('.') or 'file'; self.db.execute('INSERT INTO diary_attachments(diary_id,original_name,media_kind,path,created_at,deleted) VALUES(?,?,?,?,?,0)',(rid,src.name,kind,str(dest),self.db.now()))
        self.db.audit('ATTACH_FILES','diary',rid,str(len(files)))
    def show_attachments(self):
        rid=self.selected_id()
        if rid is None:return
        rows=self.db.all('SELECT original_name,path FROM diary_attachments WHERE diary_id=? AND deleted=0',(rid,)); text='\n'.join(f"• {r['original_name']}\n  {r['path']}" for r in rows) or self.i18n.t('empty.records'); QMessageBox.information(self,'Adjuntos' if self.i18n.language=='es' else 'Attachments',text)
    def export_txt(self):
        rid=self.selected_id()
        if rid is None:return
        row=self.db.one('SELECT title,body,category,mood,created_at FROM diary WHERE id=?',(rid,))
        if not row:return
        path,_=QFileDialog.getSaveFileName(self,'Exportar diario' if self.i18n.language=='es' else 'Export diary',f"{row['title']}.txt",'Text (*.txt)')
        if not path:return
        Path(path).write_text(f"{row['title']}\n{row['created_at']} · {row['category']} · {row['mood'] or ''}\n\n{row['body'] or ''}",encoding='utf-8'); self.db.audit('EXPORT_TXT','diary',rid,path)
