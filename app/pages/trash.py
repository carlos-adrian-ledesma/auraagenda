from __future__ import annotations
from PySide6.QtWidgets import QComboBox,QHBoxLayout,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem
from .base import Page

TABLES=['agenda','alarms','tasks','habits','lists','diary','writing','people','goals','cycle_records','wellness_logs','health_items','sleep_logs','mood_logs','selfcare','beauty_products','wardrobe','outfits','finance','trips','library','multimedia']
class TrashPage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.db=db; self.i18n=i18n; row=QHBoxLayout(); self.selector=QComboBox(); self.selector.addItems(TABLES); self.restore_btn=QPushButton(); self.delete_btn=QPushButton(); self.delete_btn.setObjectName('Danger'); row.addWidget(self.selector); row.addWidget(self.restore_btn); row.addWidget(self.delete_btn); row.addStretch(); self.layout_root.addLayout(row); self.table=QTableWidget(0,3); self.layout_root.addWidget(self.table,1); self.selector.currentTextChanged.connect(self.refresh); self.restore_btn.clicked.connect(self.restore); self.delete_btn.clicked.connect(self.permanent); self.retranslate(); self.refresh()
    def retranslate(self): self.title_label.setText(self.i18n.t('page.trash')); self.subtitle_label.setText('Elementos eliminados de forma reversible.' if self.i18n.language=='es' else 'Reversibly deleted items.'); self.restore_btn.setText(self.i18n.t('common.restore')); self.delete_btn.setText(self.i18n.t('common.delete')); self.table.setHorizontalHeaderLabels(['ID','Resumen','Fecha'] if self.i18n.language=='es' else ['ID','Summary','Date'])
    def refresh(self):
        t=self.selector.currentText();
        try: rows=self.db.all(f'SELECT * FROM {t} WHERE deleted=1 ORDER BY id DESC')
        except Exception: rows=[]
        self.table.setRowCount(len(rows));
        for r,row in enumerate(rows):
            keys=row.keys(); summary=' · '.join(str(row[k]) for k in keys if k not in {'id','deleted','created_at','updated_at'} and row[k] not in (None,'') )[:140]; dt=str(row['updated_at'] if 'updated_at' in keys else row['created_at'] if 'created_at' in keys else '')
            for c,v in enumerate((row['id'],summary,dt)): self.table.setItem(r,c,QTableWidgetItem(str(v)))
    def selected(self):
        r=self.table.currentRow(); return int(self.table.item(r,0).text()) if r>=0 and self.table.item(r,0) else None
    def restore(self):
        rid=self.selected();
        if rid is None:return
        self.db.restore(self.selector.currentText(),rid); self.refresh()
    def permanent(self):
        rid=self.selected();
        if rid is None:return
        if QMessageBox.question(self,self.i18n.t('common.confirm'),('¿Eliminar definitivamente?' if self.i18n.language=='es' else 'Delete permanently?'))!=QMessageBox.Yes:return
        t=self.selector.currentText(); self.db.execute(f'DELETE FROM {t} WHERE id=? AND deleted=1',(rid,)); self.db.audit('DELETE_PERMANENT',t,rid); self.refresh()
