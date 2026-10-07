from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QHBoxLayout,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem
from .base import Page
from ..services.backup import BackupService

class BackupPage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.db=db; self.i18n=i18n; self.service=BackupService(db)
        row=QHBoxLayout(); self.create_btn=QPushButton(); self.create_btn.setObjectName('Primary'); self.restore_btn=QPushButton(); row.addWidget(self.create_btn); row.addWidget(self.restore_btn); row.addStretch(); self.layout_root.addLayout(row)
        self.table=QTableWidget(0,5); self.layout_root.addWidget(self.table,1); self.create_btn.clicked.connect(self.create_backup); self.restore_btn.clicked.connect(self.restore_backup); self.retranslate(); self.refresh()
    def retranslate(self):
        self.title_label.setText(self.i18n.t('page.backup')); self.subtitle_label.setText('Copias locales verificables con respaldo de seguridad antes de restaurar.' if self.i18n.language=='es' else 'Verifiable local backups with a safety copy before restore.'); self.create_btn.setText(self.i18n.t('backup.create')); self.restore_btn.setText(self.i18n.t('backup.restore')); self.table.setHorizontalHeaderLabels(['Fecha','Tipo','Tamaño','Estado','Ruta'] if self.i18n.language=='es' else ['Date','Kind','Size','Status','Path'])
    def refresh(self):
        rows=self.db.all('SELECT created_at,kind,size_bytes,status,path FROM backups ORDER BY id DESC'); self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            vals=[row['created_at'],row['kind'],f"{int(row['size_bytes'] or 0)/1024/1024:.2f} MB",row['status'],row['path']]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))
        self.table.resizeColumnsToContents()
    def create_backup(self):
        try: p=self.service.create('Manual'); QMessageBox.information(self,self.i18n.t('success.title'),str(p)); self.refresh()
        except Exception as exc: QMessageBox.critical(self,self.i18n.t('error.title'),str(exc))
    def restore_backup(self):
        f,_=QFileDialog.getOpenFileName(self,'Backup','','ZIP (*.zip)')
        if not f:return
        try: self.service.restore(Path(f)); QMessageBox.information(self,self.i18n.t('success.title'),self.i18n.t('backup.valid'))
        except Exception as exc: QMessageBox.critical(self,self.i18n.t('error.title'),str(exc))
