from pathlib import Path
p=Path('plot_background_maps.py');s=p.read_text(encoding='utf-8').replace('HEIGHT=2760','HEIGHT=1900').replace('min(2060/bw,1960/bh)','min(2060/bw,1160/bh)').replace('top=300+round((1960-dh)/2)','top=260+round((1160-dh)/2)').replace('box[3]>2270','box[3]>1440').replace('(80,2340)','(80,1465)').replace('ly=2410+','ly=1540+');p.write_text(s,encoding='utf-8')
