from pathlib import Path
s=Path('D:/self/openqq-v0.5.0-win-x64/native/session.cjs').read_text(encoding='utf-8')
for word in ['case"download_file"','"download_file"','get_group_root_files']:
 p=s.find(word);print(word,s[max(0,p-180):p+600])
