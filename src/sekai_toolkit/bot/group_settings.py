"""Per-group persistent Bot preferences."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class GroupSettings:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS group_settings (group_id INTEGER PRIMARY KEY, reply TEXT NOT NULL DEFAULT "group", auto_recall INTEGER NOT NULL DEFAULT 1)')
            db.execute('CREATE TABLE IF NOT EXISTS global_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10)
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def get(self,group_id):
        if group_id is None:return ('group',True)
        with self._db() as db:
            row=db.execute('SELECT reply,auto_recall FROM group_settings WHERE group_id=?',(int(group_id),)).fetchone()
        return (row[0],bool(row[1])) if row else ('group',True)

    def set_reply(self,group_id,mode):
        if mode not in ('group','private'):raise ValueError(mode)
        with self._db() as db:
            db.execute('INSERT INTO group_settings(group_id,reply) VALUES(?,?) ON CONFLICT(group_id) DO UPDATE SET reply=excluded.reply',(int(group_id),mode))

    def set_auto_recall(self,group_id,enabled):
        with self._db() as db:
            db.execute('INSERT INTO group_settings(group_id,auto_recall) VALUES(?,?) ON CONFLICT(group_id) DO UPDATE SET auto_recall=excluded.auto_recall',(int(group_id),int(enabled)))

    def group_decode_enabled(self):
        with self._db() as db:
            row=db.execute('SELECT value FROM global_settings WHERE key=?',('group_decode',)).fetchone()
        return row is None or row[0]=='1'

    def set_group_decode(self,enabled):
        with self._db() as db:
            db.execute('INSERT INTO global_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',('group_decode','1' if enabled else '0'))

    def heartbeat_enabled(self):
        with self._db() as db:
            row=db.execute('SELECT value FROM global_settings WHERE key=?',('heartbeat_enabled',)).fetchone()
        return row is None or row[0]=='1'

    def set_heartbeat_enabled(self,enabled):
        with self._db() as db:
            db.execute('INSERT INTO global_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',('heartbeat_enabled','1' if enabled else '0'))
