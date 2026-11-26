from pathlib import Path
p=Path('qqbot_server.py');s=p.read_text(encoding='utf-8-sig').replace('hmac.compare_digest(token,config.token)',"hmac.compare_digest(token.encode('utf-8'),config.token.encode('utf-8'))")
s=s.replace(" p.add_argument('--token',default=os.environ.get('SEKAI_BOT_TOKEN',''))", " p.add_argument('--token',default=os.environ.get('SEKAI_BOT_TOKEN',''))\n p.add_argument('--no-token',action='store_true',help='Ignore token environment variable (local listening only)')")
s=s.replace(' a=p.parse_args()',' a=p.parse_args()\n if a.no_token:a.token=\'\'')
s=s.replace(" web.run_app(create_app(a),host=a.host,port=a.port)"," LOG.info('Token authentication: %s', 'enabled' if a.token else 'disabled (local only)')\n web.run_app(create_app(a),host=a.host,port=a.port)")
p.write_text(s,encoding='utf-8')
