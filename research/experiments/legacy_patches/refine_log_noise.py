from pathlib import Path
p=Path('render_compact_report.py');s=p.read_text(encoding='utf-8');s=s.replace("if key in NEEDED:ICONS[key]=Image.open(path).convert('RGBA')", "if key in NEEDED and key not in ICONS:ICONS[key]=Image.open(path).convert('RGBA')")
p.write_text(s,encoding='utf-8')
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8');s=s.replace("     LOG.info('匹配烤森文件 | %s | 等待任务=%s',name,self.queue.qsize())\n",'')
s=s.replace("     try:self.queue.put_nowait((event,file));self.seen[key]=now", "     try:\n      self.queue.put_nowait((event,file));self.seen[key]=now\n      LOG.info('已加入绘图队列 | 文件=%s | 等待任务=%s',name,self.queue.qsize())")
s=s.replace(",job.name,",",job.name[:8],").replace(",job.name)",",job.name[:8])")
p.write_text(s,encoding='utf-8')
