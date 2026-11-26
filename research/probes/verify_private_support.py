from pathlib import Path
p=Path('test_openqq_flow.py');s=p.read_text(encoding='utf-8')
s=s.replace("event={'post_type':'notice','notice_type':'group_upload','self_id':999,'user_id':123,'group_id':456,'file':{'id':'test-file','name':'[428] response_mkcn_test.bin','size':BIN.stat().st_size,'busid':102}}", "event={'post_type':'message','message_type':'private','self_id':999,'user_id':123,'message_id':101,'file':{'id':'test-file','name':'[428] response_mkcn_test.bin','size':BIN.stat().st_size}}\n    event['message']=[{'type':'file','data':event['file']}]" )
s=s.replace("await ws.send_json({**event,'file':{**event['file'],'name':'ignore.bin'}})","await ws.send_json({**event,'message':[{'type':'file','data':{**event['file'],'name':'ignore.bin'}}]})")
s=s.replace("assert message['action']=='send_group_msg';assert message['params']['group_id']==456", "assert message['action']=='send_private_msg';assert message['params']['user_id']==123")
s=s.replace('five valid PNG replies','five valid private-chat PNG replies')
Path('test_openqq_private.py').write_text(s,encoding='utf-8')
