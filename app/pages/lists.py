from __future__ import annotations
from PySide6.QtWidgets import QHBoxLayout,QInputDialog,QPushButton,QTableWidget,QTableWidgetItem
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
class ListsPage(GenericCrudPage):
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.lists','Checklists para compras, viajes, regalos, ideas y más.','Checklists for shopping, travel, gifts, ideas and more.','lists',['name','list_type','updated_at'],[F('name','Nombre','Name',required=True),F('list_type','Tipo','Type','combo',('Compras','Supermercado','Viaje','Equipaje','Cumpleaños','Pendientes','Regalos','Ideas','Películas','Libros','Wishlist','Personalizada')),F('notes','Notas','Notes','multiline')],'id DESC')
        row=QHBoxLayout(); self.add_item_btn=QPushButton(); self.toggle_btn=QPushButton(); self.del_item_btn=QPushButton(); row.addWidget(self.add_item_btn); row.addWidget(self.toggle_btn); row.addWidget(self.del_item_btn); row.addStretch(); self.layout_root.addLayout(row); self.items=QTableWidget(0,5); self.layout_root.addWidget(self.items,1); self.table_widget.itemSelectionChanged.connect(self.refresh_items); self.add_item_btn.clicked.connect(self.add_item); self.toggle_btn.clicked.connect(self.toggle_item); self.del_item_btn.clicked.connect(self.delete_item); self.retranslate()
    def retranslate(self):
        super().retranslate()
        if hasattr(self,'items'):
            if self.i18n.language=='es': self.add_item_btn.setText('＋ Elemento'); self.toggle_btn.setText('✓ Marcar/desmarcar'); self.del_item_btn.setText('− Elemento'); self.items.setHorizontalHeaderLabels(['ID','✓','Elemento','Cantidad','Prioridad'])
            else: self.add_item_btn.setText('＋ Item'); self.toggle_btn.setText('✓ Toggle'); self.del_item_btn.setText('− Item'); self.items.setHorizontalHeaderLabels(['ID','✓','Item','Quantity','Priority'])
    def refresh(self): super().refresh(); self.refresh_items()
    def refresh_items(self):
        if not hasattr(self,'items'): return
        lid=self.selected_id(); rows=self.db.all('SELECT id,checked,text,quantity,priority FROM list_items WHERE list_id=? AND deleted=0 ORDER BY position,id',(lid,)) if lid else []; self.items.setRowCount(len(rows))
        for r,row in enumerate(rows):
            for c,v in enumerate((row['id'],'✓' if row['checked'] else '',row['text'],row['quantity'] or '',row['priority'] or '')): self.items.setItem(r,c,QTableWidgetItem(str(v)))
    def add_item(self):
        lid=self.selected_id()
        if not lid:return
        label='Elemento' if self.i18n.language=='es' else 'Item'; text,ok=QInputDialog.getText(self,label,label)
        if ok and text.strip(): self.db.execute('INSERT INTO list_items(list_id,text,position) VALUES(?,?,?)',(lid,text.strip(),999)); self.refresh_items()
    def _selected_item(self):
        r=self.items.currentRow(); return int(self.items.item(r,0).text()) if r>=0 and self.items.item(r,0) else None
    def toggle_item(self):
        rid=self._selected_item()
        if rid:self.db.execute('UPDATE list_items SET checked=CASE checked WHEN 0 THEN 1 ELSE 0 END WHERE id=?',(rid,)); self.refresh_items()
    def delete_item(self):
        rid=self._selected_item()
        if rid:self.db.execute('UPDATE list_items SET deleted=1 WHERE id=?',(rid,)); self.refresh_items()
