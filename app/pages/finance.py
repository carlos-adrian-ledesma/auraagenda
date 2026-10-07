from __future__ import annotations
from PySide6.QtWidgets import QFileDialog,QMessageBox,QTabWidget,QPushButton
from .base import Page
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F

class FinancePage(Page):
    def __init__(self,db,i18n):
        super().__init__(); self.db=db; self.i18n=i18n; self.export_btn=QPushButton('⇩ CSV'); self.export_btn.clicked.connect(self.export_csv); self.layout_root.addWidget(self.export_btn); self.tabs=QTabWidget(); self.layout_root.addWidget(self.tabs,1)
        self.transactions=GenericCrudPage(db,i18n,'page.finance','Ingresos y gastos.','Income and expenses.','finance',['txn_date','txn_type','category','concept','amount','currency','status'],[F('txn_date','Fecha','Date','date',required=True),F('txn_type','Tipo','Type','combo',('income','expense'),required=True),F('category','Categoría','Category'),F('concept','Concepto','Concept',required=True),F('amount','Importe','Amount','double',required=True),F('currency','Moneda','Currency'),F('status','Estado','Status','combo',('paid','pending')),F('payment_method','Método de pago','Payment method'),F('recurring','Recurrente','Recurring','combo',('No','Yes')),F('due_date','Vencimiento','Due date','date'),F('note','Nota','Note','multiline')],'txn_date DESC')
        self.budgets=GenericCrudPage(db,i18n,'page.finance','Presupuestos mensuales.','Monthly budgets.','budgets',['month','category','amount','currency'],[F('month','Mes YYYY-MM','Month YYYY-MM',required=True),F('category','Categoría','Category',required=True),F('amount','Importe','Amount','double',required=True),F('currency','Moneda','Currency'),F('notes','Notas','Notes','multiline')],'month DESC')
        self.subscriptions=GenericCrudPage(db,i18n,'page.finance','Suscripciones y pagos recurrentes.','Subscriptions and recurring payments.','subscriptions',['name','amount','currency','frequency','next_payment','active'],[F('name','Nombre','Name',required=True),F('amount','Importe','Amount','double',required=True),F('currency','Moneda','Currency'),F('frequency','Frecuencia','Frequency','combo',('weekly','monthly','yearly')),F('next_payment','Próximo pago','Next payment','date'),F('payment_method','Método de pago','Payment method'),F('active','Activa','Active','bool'),F('notes','Notas','Notes','multiline')],'next_payment ASC')
        self.savings=GenericCrudPage(db,i18n,'page.finance','Objetivos de ahorro.','Savings goals.','savings_goals',['name','target_amount','current_amount','currency','target_date'],[F('name','Nombre','Name',required=True),F('target_amount','Objetivo','Target','double'),F('current_amount','Actual','Current','double'),F('currency','Moneda','Currency'),F('target_date','Fecha objetivo','Target date','date'),F('notes','Notas','Notes','multiline')],'id DESC')
        for p in (self.transactions,self.budgets,self.subscriptions,self.savings):
            p.header.hide(); p.layout_root.setContentsMargins(12,12,12,12); self.tabs.addTab(p,'')
        self.retranslate()
    def retranslate(self):
        self.title_label.setText(self.i18n.t('page.finance')); self.subtitle_label.setText('Economía personal: movimientos, presupuestos, suscripciones y ahorro.' if self.i18n.language=='es' else 'Personal finance: transactions, budgets, subscriptions and savings.')
        labels=('Movimientos','Presupuestos','Suscripciones','Ahorro') if self.i18n.language=='es' else ('Transactions','Budgets','Subscriptions','Savings')
        for i,(p,label) in enumerate(zip((self.transactions,self.budgets,self.subscriptions,self.savings),labels)): self.tabs.setTabText(i,label); p.retranslate()
    def refresh(self):
        for p in (self.transactions,self.budgets,self.subscriptions,self.savings): p.refresh()
    def add_record(self): self.transactions.add_record()

    def export_csv(self):
        import csv
        path,_=QFileDialog.getSaveFileName(self,'Export finance','finance.csv','CSV (*.csv)')
        if not path:return
        rows=self.db.all('SELECT txn_date,txn_type,category,concept,amount,currency,status,payment_method,note FROM finance WHERE deleted=0 ORDER BY txn_date')
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f); w.writerow(['date','type','category','concept','amount','currency','status','payment_method','note']);
            for r in rows:w.writerow([r[k] for k in r.keys()])
        self.db.audit('EXPORT_CSV','finance',None,path)
        QMessageBox.information(self,self.i18n.t('success.title'),path)
