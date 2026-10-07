from __future__ import annotations
import tempfile
from pathlib import Path
from app.database import Database

def temp_db():
    td=tempfile.TemporaryDirectory(); db=Database(Path(td.name)/'auraagenda.db'); return td,db
