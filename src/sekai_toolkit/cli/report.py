import argparse,os,runpy,sys
from pathlib import Path
from sekai_toolkit.common.paths import ROOT
from PIL import Image
def main():
 p=argparse.ArgumentParser(description='Decode a MySekai binary and render an offline report')
 p.add_argument('input',type=Path,help='Encrypted response bin path')
 p.add_argument('--output',type=Path,default=ROOT/'output')
 p.add_argument('--mode',choices=['1+1','1+4','stitched'],default='1+1')
 p.add_argument('--format',choices=['png','jpg','webp'],default='png')
 p.add_argument('--dpi',type=int,default=144)
 p.add_argument('--quality',type=int,default=95)
 p.add_argument('--keyset',choices=['auto','cn','legacy'],default='auto')
 a=p.parse_args()
 if a.dpi<=0 or not 1<=a.quality<=100:p.error('dpi must be positive; quality must be 1..100')
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 sys.argv=['decode_sekai.py',str(a.input.resolve()),'--out',str(out/'data'),'--keyset',a.keyset]
 runpy.run_module('sekai_toolkit.decoder.decode_sekai',run_name='__main__')
 os.environ['SEKAI_RESPONSE']=str(out/'data/response.json');os.environ['SEKAI_RENDER_OUT']=str(out/'rendered')
 runpy.run_module('sekai_toolkit.report.renderer',run_name='__main__')
 src=out/'rendered'; overview=Image.open(src/'overview.png').convert('RGB')
 maps=[Image.open(src/f'site_{s}.png').convert('RGB') for s in [5,6,7,8]]
 mw,mh=maps[0].size
 contact=Image.new('RGB',(mw*2,mh*2),'white')
 for i,im in enumerate(maps):contact.paste(im,((i%2)*mw,(i//2)*mh))
 outputs={'overview':overview}
 if a.mode=='1+1':outputs['maps']=contact
 elif a.mode=='1+4':outputs.update({f'site_{s}':im for s,im in zip([5,6,7,8],maps)})
 else:
  w=max(im.width for im in maps);oh=round(overview.height*w/overview.width)
  scaled_maps=[im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS) for im in maps]
  canvas=Image.new('RGB',(w,oh+sum(im.height for im in scaled_maps)),'white')
  canvas.paste(overview.resize((w,oh),Image.Resampling.LANCZOS),(0,0));y=oh
  for im in scaled_maps:canvas.paste(im,(0,y));y+=im.height
  outputs={'report':canvas}
 for name,im in outputs.items():im.save(out/f'{name}.{a.format}',dpi=(a.dpi,a.dpi),quality=a.quality)
 print('Output:',out)
if __name__=='__main__':main()
