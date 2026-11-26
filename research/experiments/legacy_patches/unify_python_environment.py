from pathlib import Path
for n in ['qqbot_server.py','sekai_report.py','decode_sekai.py','test_qqbot_flow.py','test_qqbot_auth.py','test_openqq_flow.py','test_qqbot_file_fallback.py']:
 p=Path(n);s=p.read_text(encoding='utf-8-sig')
 s=s.replace("sys.path.insert(0,str(ROOT/'vendor'))", "sys.path.insert(0,str(ROOT/'vendor')) if sys.prefix==sys.base_prefix else None")
 s=s.replace("sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))", "sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor')) if sys.prefix==sys.base_prefix else None")
 s=s.replace("env['PYTHONPATH']=str(ROOT/'vendor')+os.pathsep+env.get('PYTHONPATH','')", "env['PYTHONPATH']=(str(ROOT/'vendor')+os.pathsep+env.get('PYTHONPATH','')) if sys.prefix==sys.base_prefix else str(ROOT)")
 p.write_text(s,encoding='utf-8')
