from pathlib import Path
p=Path('sekai_report.py');s=p.read_text(encoding='utf-8-sig');old="  w=3840;oh=round(overview.height*w/overview.width);canvas=Image.new('RGB',(w,oh+contact.height),'white');canvas.paste(overview.resize((w,oh),Image.Resampling.LANCZOS),(0,0));canvas.paste(contact,(0,oh));outputs={'report':canvas}"
new="""  w=max(im.width for im in maps);oh=round(overview.height*w/overview.width)
  scaled_maps=[im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS) for im in maps]
  canvas=Image.new('RGB',(w,oh+sum(im.height for im in scaled_maps)),'white')
  canvas.paste(overview.resize((w,oh),Image.Resampling.LANCZOS),(0,0));y=oh
  for im in scaled_maps:canvas.paste(im,(0,y));y+=im.height
  outputs={'report':canvas}"""
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=Path('USAGE.md');s=p.read_text(encoding='utf-8').replace('总览与四图高清拼成一张','总览在上，四张地图依次竖排拼成一张').replace('整张拼接宽3840像素','整张竖排拼接宽1920像素，每张地图保留原始像素尺寸');p.write_text(s,encoding='utf-8')
