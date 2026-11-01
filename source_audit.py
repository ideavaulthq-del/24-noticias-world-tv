"""Auditoria de URLs e licenças; não constitui fact-checking automático."""
from urllib.parse import urlparse
from datetime import datetime, timezone

ALLOWED_LICENSES={'CC0','CC BY 4.0','licenca_propria','autorizacao_escrita'}

def safe_https(url):
    if not isinstance(url,str): return False
    try:
        p=urlparse(url)
        return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password and p.hostname not in ('localhost','127.0.0.1')
    except ValueError:return False

def audit(article):
    issues=[]
    if not safe_https(article.get('article_url')): issues.append('fonte_sem_url_https_valida')
    sources={article.get('source')}|{s.get('source') for s in article.get('related_sources',[]) if isinstance(s,dict)}
    if len(sources)<2: issues.append('sem_segunda_fonte_independente')
    image=article.get('image_url')
    if image:
        if not safe_https(image):issues.append('imagem_url_invalida')
        if article.get('image_license') not in ALLOWED_LICENSES:issues.append('imagem_sem_licenca_reconhecida')
        if not article.get('image_credit','').strip():issues.append('imagem_sem_credito')
        if article.get('image_license')=='autorizacao_escrita' and not article.get('image_permission_ref'):issues.append('falta_referencia_autorizacao')
    try:
        published=datetime.fromisoformat(article['published_at'].replace('Z','+00:00'))
        if published.tzinfo is None or not 0 <= (datetime.now(timezone.utc)-published).total_seconds() <= 48*3600:issues.append('data_fora_de_validade')
    except (KeyError,TypeError,ValueError):issues.append('data_invalida')
    return {'article_id':article.get('id'),'sources_detected':len(sources),'issues':issues,'status':'revisao_humana_obrigatoria' if issues else 'elegivel_para_revisao_humana'}
