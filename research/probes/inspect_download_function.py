from pathlib import Path
s=Path('D:/self/openqq-v0.5.0-win-x64/native/session.cjs').read_text(encoding='utf-8')
p=s.find('downloadRichMedia({');print(s[p-1600:p])
