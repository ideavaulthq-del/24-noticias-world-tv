#!/usr/bin/env python3
"""RSS + meteorologia, sem dependências externas. Executar com Python 3."""
import json, re, hashlib, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from editorial import enrich
from source_audit import audit

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ('RTP Notícias', 'Portugal', 'https://www.rtp.pt/noticias/rss/'),
    ('BBC News', 'Mundo', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('BBC Business', 'Economia', 'https://feeds.bbci.co.uk/news/business/rss.xml'),
    ('BBC Technology', 'Tecnologia', 'https://feeds.bbci.co.uk/news/technology/rss.xml'),
]
AGENT = '24NoticiasFeed/13.0 (+RSS reader; attribution)'

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':AGENT,'Accept':'application/rss+xml, application/xml, application/json, text/xml'})
    with urllib.request.urlopen(req,timeout=12) as r:
        return r.read(2_000_000)

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()

def timestamp(raw):
    from email.utils import parsedate_to_datetime
    try: return parsedate_to_datetime(raw).astimezone(timezone.utc).isoformat()
    except Exception: return None

def editorial_title(title):
    """Normalização editorial limitada: NÃO é reescrita independente nem verificação factual."""
    title=clean(title)
    title=re.sub(r'\s+[|–-]\s+(BBC News|RTP Notícias|BBC)$','',title,flags=re.I)
    title=title.rstrip(' .')
    return title[:180]

def news():
    found=[]; seen=set(); now=datetime.now(timezone.utc)
    for source,category,url in SOURCES:
        try:
            root=ET.fromstring(get(url))
            for item in root.findall('.//item')[:25]:
                title=clean(item.findtext('title'))
                link=(item.findtext('link') or '').strip()
                pub=timestamp(item.findtext('pubDate'))
                if not title or not link or not pub: continue
                dt=datetime.fromisoformat(pub)
                if not timedelta(0)<=now-dt<=timedelta(hours=48): continue
                key=hashlib.sha256(re.sub(r'\W+','',title.casefold()).encode()).hexdigest()[:20]
                if key in seen:continue
                seen.add(key)
                # Sem imagens externas não licenciadas, nem reprodução de descrições RSS.
                found.append({'id':key,'title':editorial_title(title),'original_title':title,'summary':'Informação divulgada por '+source+'. Consulte a publicação original para conhecer os detalhes e o contexto.','source':source,'category':category,'published_at':pub,'article_url':link,'image_url':'','verification_status':'fonte_unica','editorial_status':'titulo_normalizado'})
            print(f'{source}: recolha concluída')
        except Exception as e:
            print(f'{source}: indisponível ({type(e).__name__})')
    return sorted(found,key=lambda x:x['published_at'],reverse=True)[:45]

def weather():
    # Open-Meteo: verificar condições de utilização e atribuição antes de uso comercial.
    params=urllib.parse.urlencode({'latitude':38.7167,'longitude':-9.1333,'current':'temperature_2m,weather_code','timezone':'Europe/Lisbon'})
    try:
        data=json.loads(get('https://api.open-meteo.com/v1/forecast?'+params))
        current=data['current']; codes={0:'Céu limpo',1:'Predominantemente limpo',2:'Parcialmente nublado',3:'Encoberto',45:'Nevoeiro',61:'Chuva fraca',63:'Chuva',65:'Chuva forte',80:'Aguaceiros',95:'Trovoada'}
        return {'location':'Lisboa','temperature_c':current['temperature_2m'],'description':codes.get(current['weather_code'],'Condições variáveis'),'updated_at':datetime.now(timezone.utc).isoformat(),'source':'Open-Meteo'}
    except Exception as e:
        print('Meteorologia indisponível:',type(e).__name__)
        return None

def main():
    target=ROOT/'feed.json'; previous={}
    if target.exists():
        try: previous=json.loads(target.read_text(encoding='utf-8'))
        except Exception: pass
    raw_articles=news()
    (ROOT/'review_queue.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),'articles':raw_articles},ensure_ascii=False,indent=2),encoding='utf-8')
    articles=enrich(raw_articles,ROOT/'editorial_overrides.json'); meteo=weather()
    audits=[audit(a) for a in articles]
    (ROOT/'audit_report.json').write_text(json.dumps({'generated_at':datetime.now(timezone.utc).isoformat(),'audits':audits},ensure_ascii=False,indent=2),encoding='utf-8')
    # Manter dados anteriores apenas se ainda recentes; nunca converter falhas em falsas notícias.
    if not articles:
        now=datetime.now(timezone.utc)
        for item in previous.get('news',[]):
            try:
                if timedelta(0)<=now-datetime.fromisoformat(item['published_at'])<=timedelta(hours=48):articles.append(item)
            except Exception:pass
    if meteo is None:
        old=previous.get('weather')
        if old:
            try:
                if datetime.now(timezone.utc)-datetime.fromisoformat(old['updated_at'])<timedelta(minutes=30):meteo=old
            except Exception:pass
    # Só conteúdos aprovados são emitidos; títulos RSS continuam na fila editorial.
    approved=[a for a in articles if a.get('editorial_status')=='revisto_manualmente']
    output={'audit_report':'audit_report.json','pending_review':len(articles)-len(approved),'editorial_notice':'Correspondência entre fontes é apenas temática e NÃO confirma factos. Títulos RSS não são redação original; apenas textos revistos manualmente têm aprovação editorial.','generated_at':datetime.now(timezone.utc).isoformat(),'news':approved,'weather':meteo}
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(target)
    print(f'Feed atualizado: {len(approved)} notícias aprovadas; {len(articles)-len(approved)} pendentes; meteorologia: {bool(meteo)}')

if __name__=='__main__':main()
