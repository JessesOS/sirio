"""Submit a Seedance 2.5 edit job to Enhancor (source video + look reference), poll, download."""
import sys,os,json,time
from pathlib import Path
APP=Path('/Users/jesseallan/Master/Side_Projects/Sirio/repos/Genjustsu-Open-Source-Workflow')
sys.path.insert(0,str(APP));os.chdir(APP)
import config;config.load_env()
import requests
from media_host import upload
job=Path(sys.argv[1]);draft=sys.argv[2]=='draft'
BASE='https://apireq.enhancor.ai/api/seedance2.5/v1/';H={'x-api-key':os.environ['ENHANCOR_API_KEY']}
hook=json.loads((APP/'.runtime-webhook.json').read_text())['url']
def log(s):print(s,flush=True);(job/'status.txt').write_text(s)
if not (job/'response.json').exists():
    if not draft:log('No draft to finalise');sys.exit(1)
    log('uploading media')
    urls=[upload(job/'source.mp4')]+([upload(job/'look-reference.jpg')] if (job/'look-reference.jpg').exists() else [])
    p={'mode':'edit','prompt':(job/'prompt.txt').read_text().strip(),'resolution':'1080p','aspect_ratio':'adaptive','output_format':'mp4','pass_faces':False,'is_draft':draft,'webhook_url':hook,'videos':[urls[0]],'images':urls[1:],'audios':[]}
    if (job/'options.json').exists():p.update(json.loads((job/'options.json').read_text()))
    (job/'request.json').write_text(json.dumps({k:v for k,v in p.items() if k not in('webhook_url','videos','images')},indent=2))
    r=requests.post(BASE+'queue',headers=H,json=p,timeout=90)
    if not r.ok:log(f'REJECTED {r.status_code}: {r.text[:400]}');sys.exit(1)
    (job/'response.json').write_text(r.text)
if not draft and not (job/'final-response.json').exists():
    did=json.loads((job/'response.json').read_text())['requestId']
    r=requests.post(BASE+'queue',headers=H,json={'draft_id':did,'webhook_url':hook},timeout=90)
    if not r.ok:log(f'REJECTED {r.status_code}: {r.text[:400]}');sys.exit(1)
    (job/'final-response.json').write_text(r.text)
rid=json.loads((job/('response.json' if draft else 'final-response.json')).read_text())['requestId'];log('submitted '+rid)
for _ in range(240):
    j=requests.post(BASE+'status',headers=H,json={'request_id':rid},timeout=30).json()
    st=j.get('status');(job/('provider-status.json' if draft else 'final-provider-status.json')).write_text(json.dumps({k:v for k,v in j.items() if k not in('result','thumbnail')}))
    if st=='COMPLETED':
        out=job/('draft.mp4' if draft else 'final.mp4');out.write_bytes(requests.get(j['result'],timeout=300).content)
        log(f"COMPLETED cost={j.get('cost')} saved={out.name}");sys.exit(0)
    if st=='FAILED':log('FAILED: '+json.dumps(j)[:400]);sys.exit(1)
    time.sleep(10)
log('TIMEOUT still '+str(st));sys.exit(2)
