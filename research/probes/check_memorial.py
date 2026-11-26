from pathlib import Path
s=Path('plot_background_maps.py').read_text(encoding='utf-8');s=s[:s.index('images=[make')]
exec(compile(s,'plot_background_maps.py','exec'))
make(8,COLORS[3])
print('Memorial rendered')
