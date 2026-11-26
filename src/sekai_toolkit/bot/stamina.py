"""Persistent per-QQ stamina reminders."""
import re
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

COMMAND = re.compile(r'^火\s+(最大值|记录)(?:\s+(.*))?$', re.I)


class StaminaStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS stamina (qq INTEGER PRIMARY KEY, capacity INTEGER, current INTEGER, next_at INTEGER, full_at INTEGER, group_id INTEGER, half_sent INTEGER DEFAULT 0, full_sent INTEGER DEFAULT 0)')

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def command(self, qq, group_id, text, now=None):
        match = COMMAND.fullmatch(text.strip())
        if not match:
            return None
        now = int(now if now is not None else time.time())
        kind, tail = match.groups()
        with self._db() as db:
            row = db.execute('SELECT capacity FROM stamina WHERE qq=?', (qq,)).fetchone()
            if kind == '最大值':
                parts = (tail or '').split()
                if len(parts) == 2 and parts[0] == '-v':
                    parts = parts[1:]
                if len(parts) != 1 or not parts[0].isdigit() or not 1 <= int(parts[0]) <= 999:
                    return '用法：火 最大值 50（也可以写 火 最大值 -v 50）'
                cap = int(parts[0])
                db.execute('INSERT INTO stamina(qq,capacity) VALUES(?,?) ON CONFLICT(qq) DO UPDATE SET capacity=excluded.capacity,current=NULL,next_at=NULL,full_at=NULL,half_sent=0,full_sent=0', (qq, cap))
                return f'已设置体力上限 {cap}。请再发送 火 记录 -cur 23 -min 12。'
            if not row or not row[0]:
                return '请先设置上限：火 最大值 50（或 火 最大值 -v 50）；再用 火 记录 -cur 23 -min 12。'
            parts = (tail or '').split()
            if len(parts) == 4 and parts[0] == '-cur' and parts[2] == '-min':
                values = (parts[1], parts[3])
            elif len(parts) == 2:
                values = parts
            else:
                return '用法：火 记录 -cur 23 -min 12（可简写 火 记录 23 12）。'
            if not all(v.isdigit() for v in values):
                return '当前体力和剩余分钟都需要填写整数。'
            cur, minutes = map(int, values)
            cap = row[0]
            if not 0 <= cur <= cap or not 1 <= minutes <= 30:
                return f'当前体力需在 0–{cap}；下一点体力的剩余时间需在 1–30 分钟。'
            full_at = now if cur == cap else now + minutes * 60 + (cap - cur - 1) * 1800
            half_sent = int(cur == cap or full_at - 1800 <= now)
            full_sent = int(cur == cap)
            db.execute('UPDATE stamina SET current=?,next_at=?,full_at=?,group_id=?,half_sent=?,full_sent=? WHERE qq=?', (cur, now + minutes * 60, full_at, group_id, half_sent, full_sent, qq))
            return f'已记录 {cur}/{cap}；预计 {time.strftime("%m-%d %H:%M", time.localtime(full_at))} 回满。' + (' 已满体力，无需提醒。' if cur == cap else ' 届时和提前半小时各提醒一次。')

    def query(self, qq, now=None):
        now=int(now if now is not None else time.time())
        with self._db() as db:
            row=db.execute('SELECT capacity,current,next_at,full_at FROM stamina WHERE qq=?',(qq,)).fetchone()
        if not row or not row[0]:return '尚未设置体力上限。请发送 火 最大值 50。'
        cap,cur,next_at,full_at=row
        if full_at is None or (now-full_at)>6*3600:return f'体力上限：{cap}；暂无有效记录。请发送 火 记录 -cur 23 -min 12。'
        estimated=min(cap,cur+max(0,(now-next_at+1800)//1800)) if now>=next_at else cur
        left=max(0,full_at-now)
        return f'体力：约 {estimated}/{cap}；预计 {time.strftime("%m-%d %H:%M",time.localtime(full_at))} 回满。'+(' 已到满体力时间。' if not left else f' 距回满约 {left//3600}小时{(left%3600)//60}分钟。')

    def due(self, now=None):
        now = int(now if now is not None else time.time())
        with self._db() as db:
            db.execute('UPDATE stamina SET current=NULL,next_at=NULL,full_at=NULL,group_id=NULL,half_sent=0,full_sent=0 WHERE full_at IS NOT NULL AND full_at<?', (now - 6 * 3600,))
            return db.execute('SELECT qq,capacity,group_id,CASE WHEN full_at<=? THEN "full" ELSE "half" END FROM stamina WHERE full_at IS NOT NULL AND ((full_sent=0 AND full_at<=?) OR (half_sent=0 AND full_at-1800<=? AND full_at>?))', (now, now, now, now)).fetchall()

    def mark(self, qq, phase):
        column = 'half_sent' if phase == 'half' else 'full_sent'
        with self._db() as db:
            if phase == 'full':
                db.execute('UPDATE stamina SET full_sent=1,half_sent=1 WHERE qq=?', (qq,))
            else:
                db.execute(f'UPDATE stamina SET {column}=1 WHERE qq=?', (qq,))

