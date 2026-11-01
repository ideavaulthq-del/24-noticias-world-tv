24 NOTÍCIAS™ WORLD TV ENGINE 14.0

Requisitos: Python 3.10+, Internet para atualização, OBS para transmissão.

1. Na pasta do projeto, executar: python update_feed.py
2. A recolha cria review_queue.json com artigos para análise.
3. Consultar: python review.py --list
4. Confirmar os factos na fonte original e, quando necessário, em fontes independentes.
5. Escrever título e resumo próprios, sem copiar textos protegidos.
6. Aprovar exemplo: python review.py --id ID --title "Título original com 15 ou mais caracteres" --summary "Resumo original verificado com 20 ou mais caracteres."
7. Para fotografias, acrescentar --image-url, --image-credit e --image-license com licença adequada e verificada.
8. Executar novamente: python update_feed.py
9. Servir: python -m http.server 8000
10. No OBS, fonte Browser: http://localhost:8000/index.html, 1920x1080.
11. Agendar update_feed.py a cada 5-10 minutos no sistema operativo. Manter o servidor local ativo.

Atenção: O sistema NÃO contém IA generativa nem verificação automática de factos. A aprovação é humana. A fila editorial não é publicada diretamente. O Open-Meteo e RSS exigem verificação das condições de uso, especialmente para transmissões comerciais. Não emitir imagens sem licença adequada. Testar o OBS e a ligação à Internet antes da live.


NOVO NA 14.0: RASCUNHOS ASSISTIDOS POR IA (OPCIONAL)
1. Executar python update_feed.py para criar review_queue.json.
2. Definir OPENAI_API_KEY no ambiente (serviço pago conforme utilização). Nunca colocar a chave no HTML ou em ficheiros públicos.
3. Executar python draft_ai.py --limit 3 (faz até 3 pedidos à API).
4. Ler ai_drafts.json. A IA recebe apenas título, fonte, data e URL, NÃO consulta nem verifica o artigo.
5. Verificar manualmente a fonte primária, cruzar dados e aprovar apenas texto factual e original com review.py.
6. Executar python update_feed.py para atualizar o feed.
Rascunhos IA nunca entram automaticamente na emissão. Sem chave, o sistema 13.0 continua a funcionar.
A API requer Internet, conta e créditos próprios; integração não testada com serviço externo neste ambiente.

VERSÃO 15.0 — AUDITORIA DE FONTES E IMAGENS
- source_audit.py verifica formato HTTPS, número de fontes relacionadas, frescura e metadados de licença/crédito.
- update_feed.py produz audit_report.json a cada recolha.
- A correspondência de fontes NÃO prova independência nem veracidade. A verificação de licenças é apenas formal, não jurídica.
- Nenhum conteúdo passa automaticamente a aprovado por causa da auditoria. Mantém-se aprovação humana obrigatória.
- Não há pesquisa factual autónoma, pesquisa automática de imagens, nem validação real das licenças.
- Testar: python -m unittest discover -v

VERSÃO 16.0 — 24 CONTROL™
Execute python control.py e abra http://127.0.0.1:8000/
No OBS use http://127.0.0.1:8000/index.html com 1920x1080.
Aprovações e revogações exigem depois clicar em Atualizar fontes e emissão.
Painel apenas local. Não publicar na Internet nem assumir que o sistema verifica factos ou licenças.
