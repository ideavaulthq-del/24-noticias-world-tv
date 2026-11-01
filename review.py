#!/usr/bin/env python3
"""Fila editorial local. Não aprova factos automaticamente."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Gerir propostas de notícias para revisão humana')
parser.add_argument('--list',action='store_true',help='Listar artigos pendentes')
parser.add_argument('--id',help='ID da notícia')
parser.add_argument('--title',help='Título original escrito pelo editor')
parser.add_argument('--summary',help='Resumo original escrito pelo editor')
parser.add_argument('--image-url',default='')
parser.add_argument('--image-credit',default='')
parser.add_argument('--image-license',default='')
args=parser.parse_args()
queue=json.loads((ROOT/'review_queue.json').read_text(encoding='utf-8')).get('articles',[]) if (ROOT/'review_queue.json').exists() else []
if args.list:
 for a in queue:print(f"{a['id']} | {a['source']} | {a['title']} | {a['article_url']}")
elif args.id:
 article=next((a for a in queue if a['id']==args.id),None)
 if not article:parser.error('ID não encontrado na fila editorial')
 if not args.title or not args.summary:parser.error('Título e resumo originais são obrigatórios')
 if not (15<=len(args.title)<=180 and 20<=len(args.summary)<=400):parser.error('Título ou resumo fora dos limites')
 if args.image_url and (not args.image_url.startswith('https://') or not args.image_credit or args.image_license not in ('CC0','CC BY 4.0','licenca_propria','autorizacao_escrita')):parser.error('Imagem exige HTTPS, crédito e licença válida')
 target=ROOT/'editorial_overrides.json';data=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
 data[args.id]={'approved':True,'title':args.title,'summary':args.summary,'image_url':args.image_url,'image_credit':args.image_credit,'image_license':args.image_license}
 target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Aprovação editorial guardada. Confirmar previamente os factos e direitos. Executar update_feed.py para publicar.')
else:parser.print_help()
