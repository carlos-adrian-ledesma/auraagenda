from __future__ import annotations
import logging,sys,traceback
from logging.handlers import RotatingFileHandler
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtWidgets import QApplication,QMessageBox,QSplashScreen
from .database import Database
from .i18n import I18n
from .main_window import MainWindow
from .onboarding import OnboardingWizard
from .paths import DISPLAY_NAME,LOG_PATH,ensure_structure,resource_path
from .services.autolock import AutoLockController
from .styles import stylesheet


def configure_logging():
    ensure_structure()
    root = logging.getLogger()
    root.setLevel(logging.ERROR)
    if not root.handlers:
        handler = RotatingFileHandler(
            LOG_PATH, maxBytes=3 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        root.addHandler(handler)

def exception_hook(exc_type,exc_value,exc_tb):
    detail=''.join(traceback.format_exception(exc_type,exc_value,exc_tb)); logging.error('Unhandled exception\n%s',detail); app=QApplication.instance()
    if app: QMessageBox.critical(None,'AuraAgenda',f'{exc_type.__name__}: {exc_value}\n\nLog: {LOG_PATH}')

def main()->int:
    configure_logging(); sys.excepthook=exception_hook; app=QApplication(sys.argv); app.setApplicationName(DISPLAY_NAME); app.setOrganizationName('QuintaDimension Tecnologia'); app.setWindowIcon(QIcon(str(resource_path('assets/AuraAgenda.ico'))))
    splash_px=QPixmap(str(resource_path('assets/auraagenda_splash.png'))); splash=QSplashScreen(splash_px.scaled(640,640,Qt.KeepAspectRatio,Qt.SmoothTransformation)); splash.show(); app.processEvents()
    try:
        db=Database(); i18n=I18n(db.setting('language','es')); app.setStyleSheet(stylesheet(db.setting('theme','Pink Crystal'), int(db.setting('font_size','10') or 10)));
        if db.setting('onboarding_complete','0')!='1':
            splash.hide(); wizard=OnboardingWizard(db,i18n); wizard.exec(); splash.show(); app.processEvents()
        window=MainWindow(db,i18n)
        controller=AutoLockController(app,window,db,i18n)
        window._auto_lock_controller=controller
        window.settings.settings_changed.connect(controller.on_settings_changed)
        QTimer.singleShot(250, controller.initial_security_check)
    except Exception as exc:
        splash.close(); logging.error('Startup error\n%s',traceback.format_exc()); QMessageBox.critical(None,'AuraAgenda',f'AuraAgenda could not open.\n{type(exc).__name__}: {exc}\n\nLog: {LOG_PATH}'); return 1
    splash.finish(window); window.show(); return app.exec()

if __name__=='__main__': raise SystemExit(main())
