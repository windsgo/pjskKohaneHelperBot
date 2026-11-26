"""Persistent converter completion reminders, keyed by QQ number."""
import re
import time
from decimal import Decimal, InvalidOperation

from sekai_toolkit.bot.stamina import StaminaStore


class ConverterStore(StaminaStore):
    def __init__(self, path):
        super().__init__(path)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS converter (qq INTEGER PRIMARY KEY, due_at INTEGER NOT NULL, group_id INTEGER, half_sent INTEGER DEFAULT 0, done_sent INTEGER DEFAULT 0)')

    def command(self, qq, group_id, text, now=None):
        match = re.fullmatch(r'转换器(?:\s+(?:-计时|-time))?\s+(\S+)', text.strip(), re.I)
        if not match:
            return '用法：转换器 (-计时/-time) 22；例如 转换器 -time 22，表示22小时后完成。'
        try:
            hours = Decimal(match.group(1))
        except InvalidOperation:
            hours = Decimal(0)
        if not hours.is_finite() or not Decimal('0.01') <= hours <= Decimal(168):
            return '剩余时间需为 0.01–168 小时的数字，例如 转换器 22。'
        now = int(now if now is not None else time.time())
        due_at = now + int(hours * 3600)
        with self._db() as db:
            db.execute('INSERT INTO converter(qq,due_at,group_id,half_sent,done_sent) VALUES(?,?,?,?,0) ON CONFLICT(qq) DO UPDATE SET due_at=excluded.due_at,group_id=excluded.group_id,half_sent=excluded.half_sent,done_sent=0', (qq, due_at, group_id, int(due_at - now <= 1800)))
        return f'转换器已记录：约 {hours} 小时后完成（{time.strftime("%m-%d %H:%M",time.localtime(due_at))}）。完成前半小时和完成时各提醒一次。'

    def due(self, now=None):
        now = int(now if now is not None else time.time())
        with self._db() as db:
            db.execute('DELETE FROM converter WHERE due_at<?', (now - 6 * 3600,))
            return db.execute('SELECT qq,group_id,CASE WHEN due_at<=? THEN "done" ELSE "half" END FROM converter WHERE (done_sent=0 AND due_at<=?) OR (half_sent=0 AND due_at-1800<=? AND due_at>?)', (now, now, now, now)).fetchall()

    def query(self,qq,now=None):
        now=int(now if now is not None else time.time())
        with self._db() as db:
            row=db.execute('SELECT due_at FROM converter WHERE qq=?',(qq,)).fetchone()
        if not row or now-row[0]>6*3600:return '暂无有效转换器计时。请发送 转换器 -time 22。'
        left=max(0,row[0]-now)
        return f'转换器预计 {time.strftime("%m-%d %H:%M",time.localtime(row[0]))} 完成。'+(' 已到时间。' if not left else f' 还剩约 {left//3600}小时{(left%3600)//60}分钟。')

    def mark(self, qq, phase):
        with self._db() as db:
            if phase == 'done':
                db.execute('UPDATE converter SET half_sent=1,done_sent=1 WHERE qq=?', (qq,))
            else:
                db.execute('UPDATE converter SET half_sent=1 WHERE qq=?', (qq,))
