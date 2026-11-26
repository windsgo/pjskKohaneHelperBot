from pathlib import Path
s=Path('D:/self/openqq-v0.5.0-win-x64/native/session.cjs').read_text(encoding='utf-8')
for word in ['downloadRichMedia({','onRichMediaDownloadComplete','kind:"get_file"','get_file','group_upload']:
 start=s.find(word);print(word,s[max(0,start-180):start+550])
