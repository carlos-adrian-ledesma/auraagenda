from __future__ import annotations
import shutil
from pathlib import Path
from PySide6.QtWidgets import QFileDialog,QMessageBox
from .generic import GenericCrudPage
from ..widgets import FieldSpec as F
from ..paths import DATA_ROOT

class _FileCrud(GenericCrudPage):
    target_folder='Files'
    def _editor(self,spec,value=None):
        w=super()._editor(spec,value)
        if spec.name=='storage_mode' and value is None and hasattr(w,'setCurrentText'):
            w.setCurrentText(self.db.setting('file_storage_default','reference'))
        return w
    def _dialog(self,record=None):
        values=super()._dialog(record)
        if not values:return values
        path=values.get('path','').strip()
        if not path:
            chosen,_=QFileDialog.getOpenFileName(self,'Select file')
            if chosen: path=chosen; values['path']=chosen
        if not path:return values
        if values.get('storage_mode')=='local_copy':
            src=Path(path)
            if src.is_file():
                folder=DATA_ROOT/self.target_folder; folder.mkdir(parents=True,exist_ok=True); dest=folder/src.name; n=1
                while dest.exists() and dest.resolve()!=src.resolve(): dest=folder/f'{src.stem}_{n}{src.suffix}'; n+=1
                if dest.resolve()!=src.resolve(): shutil.copy2(src,dest)
                values['path']=str(dest)
            else:
                QMessageBox.warning(self,self.i18n.t('error.title'),('Archivo no encontrado' if self.i18n.language=='es' else 'File not found'))
        return values

class LibraryPage(_FileCrud):
    target_folder='Library/Files'
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.library','Documentos, fotos, videos, audios y enlaces por referencia o copia local.','Documents, photos, videos, audio and links by reference or local copy.','library',['title','file_type','category','storage_mode','favorite','path'],[F('title','Título','Title',required=True),F('file_type','Tipo','Type'),F('path','Ruta (vacía = elegir archivo)','Path (empty = choose file)'),F('storage_mode','Modo','Storage mode','combo',('reference','local_copy')),F('category','Categoría','Category'),F('tags','Etiquetas','Tags'),F('favorite','Favorito','Favorite','bool')],'id DESC')

class MultimediaPage(_FileCrud):
    target_folder='Multimedia/Files'
    def __init__(self,db,i18n):
        super().__init__(db,i18n,'page.multimedia','Covers, canciones, videos, audios, portadas, letras y proyectos.','Covers, songs, videos, audio, artwork, lyrics and projects.','multimedia',['title','media_type','artist','song','status','path'],[F('title','Título','Title',required=True),F('media_type','Tipo','Type','combo',('Cover','Song','Video','Audio','Artwork','Lyrics','Project')),F('artist','Artista','Artist'),F('song','Canción','Song'),F('path','Ruta (vacía = elegir archivo)','Path (empty = choose file)'),F('storage_mode','Modo','Storage mode','combo',('reference','local_copy')),F('status','Estado','Status'),F('tags','Etiquetas','Tags')],'id DESC')
