#!/usr/bin/env python3
"""Rascunhos assistidos por IA, SEM publicação nem verificação factual automática."""
import os,json,argparse,urllib.request,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def propose(article, api_key, model):
    instruction=("És editor de notícias em português de Portugal. Recebes APENAS título RSS, fonte e data. "
      "Não tens acesso ao artigo completo. Não acrescentes factos, números, declarações, causas ou conclusões. "
      "Propõe um título original e um resumo cauteloso entre 20 e 400 caracteres, deixando explícito que os detalhes carecem de verificação. "
      "Não copies o título palavra por palavra. Responde apenas com JSON: title, summary, review_notes. "
      "O texto é um RASCUNHO, não é notícia verificada.")
    payload={'model':model,'instructions':instruction,'input':json.dumps({k:article.get(k) for k in ('original_title','source','published_at','article_url')},ensure_ascii=False),'text':{'format':{'type':'json_schema','name':'news_draft','strict':True,'schema':{'type':'object','properties':{'title':{'type':'string'},'summary':{'type':'string'},'review_notes':{'type':'string'}},'required':['title','summary','review_notes'],'additionalProperties':False}}}}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=40) as resp:result=json.load(resp)
    text=''.join(part.get('text','') for item in result.get('output',[]) for part in item.get('content',[]) if part.get('type')=='output_text')
    obj=json.loads(text)
    if not (15<=len(obj['title'])<=180 and 20<=len(obj['summary'])<=400):raise ValueError('Rascunho fora dos limites')
    return obj

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=3);parser.add_argument('--model',default='gpt-4.1-mini');args=parser.parse_args()
    key=os.environ.get('OPENAI_API_KEY')
    if not key:parser.error('Definir OPENAI_API_KEY. A API pode ter custos; não são feitos pedidos sem chave.')
    queue_file=ROOT/'review_queue.json'
    if not queue_file.exists():parser.error('Executar primeiro python update_feed.py')
    articles=json.loads(queue_file.read_text(encoding='utf-8')).get('articles',[])
    output=ROOT/'ai_drafts.json'; existing=json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    for a in articles[:max(0,min(args.limit,20))]:
        if a['id'] in existing:continue
        try:
            draft=propose(a,key,args.model)
            existing[a['id']]={'id':a['id'],'source':a['source'],'article_url':a['article_url'],'published_at':a['published_at'],'draft':draft,'status':'PENDENTE_REVISAO_HUMANA','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            output.write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding='utf-8')
            print('Rascunho criado (NÃO publicado):',a['id'])
        except Exception as exc:print('Falha:',a['id'],type(exc).__name__)
    print('Rever ai_drafts.json; confirmar factos e redigir/aprovar com review.py. Nenhum rascunho é publicado automaticamente.')
if __name__=='__main__':main()
