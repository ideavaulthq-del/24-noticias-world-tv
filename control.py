"""Painel local de revisão editorial. Não valida factos automaticamente."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from pathlib import Path
import json, html, secrets, subprocess, sys
ROOT=Path(__file__).resolve().parent
TOKEN=secrets.token_urlsafe(24)
def read(name, default):
 try: return json.loads((ROOT/name).read_text(encoding='utf-8'))
 except (OSError, ValueError): return default
def e(s): return html.escape(str(s),quote=True)
class App(BaseHTTPRequestHandler):
 def reply(self,status,body,ctype='text/html; charset=utf-8'):
  data=body.encode();self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if self.path in ('/index.html','/feed.json','/audit_report.json'):
   p=ROOT/self.path[1:]
   return self.reply(200,p.read_text(encoding='utf-8'),'application/json' if p.suffix=='.json' else 'text/html') if p.exists() else self.reply(404,'Não encontrado')
  if self.path!='/':return self.reply(404,'Não encontrado')
  queue=read('review_queue.json',{}).get('articles',[]); overrides=read('editorial_overrides.json',{}); feed=read('feed.json',{})
  page=['<!doctype html><html lang="pt-PT"><meta charset="utf-8"><title>24 CONTROL</title><style>body{font:16px Arial;background:#f4f5f7;margin:0;color:#222}header{background:#181818;color:white;padding:25px}main{max-width:1050px;margin:auto}article,section{background:white;border-radius:12px;padding:22px;margin:20px;box-shadow:0 2px 9px #0001}h1 em{color:#e33;font-style:normal}label{display:block;margin:12px 0}input:not([type=checkbox]),textarea,select{display:block;box-sizing:border-box;width:100%;padding:10px;border:1px solid #aaa;border-radius:5px}textarea{height:85px}button{background:#c62828;color:white;border:0;padding:12px 20px;border-radius:5px;cursor:pointer}a{color:#a11}</style><header><h1>24 <em>CONTROL™</em> | Redação</h1></header><main>']
  page.append(f'<section><p>Na fila: {len(queue)} | Em emissão: {len(feed.get("news",[]))}</p><a href="/index.html" target="_blank">Ver canal TV</a> · <a href="/audit_report.json" target="_blank">Ver auditoria</a><form method="post" action="/refresh"><input type="hidden" name="token" value="{TOKEN}"><p><button>Atualizar fontes e emissão</button></p></form></section>')
  for a in queue:
   aid=a['id']; prior=overrides.get(aid,{})
   page.append(f'<article><small>{e(a.get("source",""))} · {e(a.get("published_at",""))}</small><h3>{e(a.get("title",""))}</h3><p><a href="{e(a.get("article_url",""))}" target="_blank" rel="noopener noreferrer">Consultar fonte original</a></p><form method="post" action="/approve"><input type="hidden" name="token" value="{TOKEN}"><input type="hidden" name="id" value="{e(aid)}">')
   page.append(f'<label>Título original<input name="title" required minlength="15" maxlength="180" value="{e(prior.get("title",""))}"></label><label>Resumo verificado<textarea name="summary" required minlength="20" maxlength="400">{e(prior.get("summary",""))}</textarea></label><label>Imagem HTTPS (opcional)<input name="image_url" value="{e(prior.get("image_url",""))}"></label><label>Crédito da imagem<input name="image_credit" value="{e(prior.get("image_credit",""))}"></label><label>Licença<select name="image_license"><option value="">Sem imagem</option>')
   for lic in ('CC0','CC BY 4.0','licenca_propria','autorizacao_escrita'):page.append(f'<option value="{lic}" {"selected" if prior.get("image_license")==lic else ""}>{lic}</option>')
   page.append('</select></label><label><input type="checkbox" name="checked" required value="yes"> Confirmei os factos, o texto e os direitos</label><button>Aprovar</button></form>')
   if prior.get('approved'):page.append(f'<form method="post" action="/revoke"><input type="hidden" name="token" value="{TOKEN}"><input type="hidden" name="id" value="{e(aid)}"><button>Revogar aprovação</button></form>')
   page.append('</article>')
  page.append('</main></html>');self.reply(200,''.join(page))
 def do_POST(self):
  if self.headers.get('Content-Type','').split(';')[0]!='application/x-www-form-urlencoded':return self.reply(415,'Formato inválido')
  size=int(self.headers.get('Content-Length','0'))
  if size<1 or size>10000:return self.reply(413,'Pedido demasiado grande')
  form={k:v[0] for k,v in parse_qs(self.rfile.read(size).decode(),keep_blank_values=True).items()}
  if not secrets.compare_digest(form.get('token',''),TOKEN):return self.reply(403,'Não autorizado')
  if self.path=='/refresh':
   try:
    result=subprocess.run([sys.executable,str(ROOT/'update_feed.py')],cwd=ROOT,timeout=80,capture_output=True,text=True)
    if result.returncode:return self.reply(500,e(result.stderr[-1000:]))
   except subprocess.TimeoutExpired:return self.reply(504,'Atualização excedeu tempo limite')
  elif self.path in ('/approve','/revoke'):
   aid=form.get('id','');queue=read('review_queue.json',{}).get('articles',[])
   if aid not in [a['id'] for a in queue]:return self.reply(400,'Notícia não encontrada')
   overrides=read('editorial_overrides.json',{})
   if self.path=='/revoke':overrides.pop(aid,None)
   else:
    title=form.get('title','').strip();summary=form.get('summary','').strip();url=form.get('image_url','').strip();credit=form.get('image_credit','').strip();lic=form.get('image_license','')
    if form.get('checked')!='yes' or not (15<=len(title)<=180 and 20<=len(summary)<=400):return self.reply(400,'Verificação editorial obrigatória')
    if url and (not url.startswith('https://') or not credit or lic not in ('CC0','CC BY 4.0','licenca_propria','autorizacao_escrita')):return self.reply(400,'Imagem sem licença válida declarada')
    overrides[aid]={'approved':True,'title':title,'summary':summary,'image_url':url,'image_credit':credit if url else '', 'image_license':lic if url else ''}
   tmp=ROOT/'editorial_overrides.tmp';tmp.write_text(json.dumps(overrides,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(ROOT/'editorial_overrides.json')
  else:return self.reply(404,'Não encontrado')
  self.send_response(303);self.send_header('Location','/');self.end_headers()
if __name__=='__main__':
 print('Painel: http://127.0.0.1:8000/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8000),App).serve_forever()
