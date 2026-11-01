"""Camada editorial prudente: correspondência temática NÃO é verificação factual."""
import json,re,unicodedata
from pathlib import Path
STOP={'sobre','para','entre','depois','antes','mais','menos','portugal','mundo','news','with','from','that','this','have','will','says','após','ainda','como','pela','pelo','esta','este','uma','uns','das','dos','and','the','for','com','que','não'}
def tokens(s):
 s=unicodedata.normalize('NFKD',s.casefold());s=''.join(c for c in s if not unicodedata.combining(c))
 return {x for x in re.findall(r'[a-z0-9]{4,}',s) if x not in STOP}
def related(a,b):
 x,y=tokens(a),tokens(b)
 return len(x&y)>=3 and len(x&y)/max(1,min(len(x),len(y)))>=.55

def enrich(articles, overrides_path):
 overrides={}
 if overrides_path.exists():
  obj=json.loads(overrides_path.read_text(encoding='utf-8'))
  if not isinstance(obj,dict):raise ValueError('editorial_overrides.json tem de ser um objeto')
  overrides=obj
 out=[]
 for a in articles:
  a=dict(a); matches=[]
  for b in articles:
   if b['id']!=a['id'] and b['source']!=a['source'] and related(a['original_title'],b['original_title']):matches.append({'source':b['source'],'article_url':b['article_url']})
  a['related_sources']=matches[:4]
  a['verification_status']='fontes_relacionadas_nao_verificadas' if matches else 'fonte_unica'
  a['editorial_status']='titulo_normalizado'
  a['image_url']=''
  a['image_credit']=''
  a['image_license']=''
  o=overrides.get(a['id'])
  if isinstance(o,dict) and o.get('approved') is True:
   title=o.get('title','');summary=o.get('summary','');image=o.get('image_url','')
   if not isinstance(title,str) or not 15<=len(title)<=180:continue
   if not isinstance(summary,str) or not 20<=len(summary)<=400:continue
   license_name=o.get('image_license','')
   credit=o.get('image_credit','')
   if image and (not isinstance(image,str) or not image.startswith('https://') or not isinstance(credit,str) or not credit.strip() or license_name not in ('CC0','CC BY 4.0','licenca_propria','autorizacao_escrita')):continue
   a.update(title=title,summary=summary,image_url=image,image_credit=credit if image else '',image_license=license_name if image else '',editorial_status='revisto_manualmente',verification_status='revisto_por_editor')
  out.append(a)
 return out
