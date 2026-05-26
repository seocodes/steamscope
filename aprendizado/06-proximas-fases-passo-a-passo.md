# 6. Próximas fases — passo a passo para você desenvolver

Este guia segue o [PLANNING.md](../PLANNING.md) e o [README.md](../README.md), mas em linguagem de **tarefas que você executa**, não de código pronto.

---

## Fase 4 — Paginação (sua próxima tarefa de código)

### Objetivo

Em uma execução, coletar **4 ou 5 páginas** da Steam (~100+ jogos), não só a primeira.

### O que mudar (mentalmente)

| Onde | Mudança |
|------|---------|
| `fetch_page` | Receber `page_num` e montar URL com `&page={page_num}` |
| `scraper.py` (main ou nova função) | Loop `for page in range(1, 6)` |
| Lista de jogos | `all_records.extend(records_da_pagina)` |
| Entre páginas | `time.sleep(1)` — já usa no scrape, use entre páginas também |

### URL exemplo

```
https://store.steampowered.com/search/?specials=1&page=2
```

### Ordem de implementação (sugestão)

1. Altere `fetch_page` para imprimir a URL com `page=2` e teste se o HTML vem diferente.
2. Faça um loop que só **conta** quantos `search_result_row` existem por página.
3. Só depois junte tudo em `insert_deals` uma vez no final (mais simples) **ou** insira por página (também válido).

### Como testar

```bash
uv run python application/scraper.py
```

Log deve mostrar total **bem maior** que uma página só. Confira no Atlas.

### Quando pedir ajuda à IA

> “Meu loop chama fetch_page 5 vezes mas a lista final tem jogos duplicados. Uso seen_urls por URL — onde devo resetar o set?”

---

## Fase 6 — Coleta de dados (quase nenhum código)

### Objetivo

Ter **histórico** de vários dias para o mesmo jogo.

### O que fazer

1. Termine a Fase 4.
2. Configure `.env` com `SCRAPE_TIME` e `RUN_ON_STARTUP` como preferir.
3. Rode `uv run python main.py` e deixe o PC ligado (ou rode manualmente 1x por dia durante 3–5 dias).
4. No Atlas, filtre por um `title` e veja vários `scraped_at` diferentes.

**Sem histórico, a Fase 7 não tem sentido** — a IA não teria com o que comparar.

---

## Fase 7 — Contexto JSON (você escreve o back-end)

### Arquivos novos

- Funções em `application/db.py`
- `application/context.py`
- `scripts/print_context.py` (teste rápido)

### Passo 7.1 — `list_game_titles()`

```python
# Ideia: collection.distinct("title")
# Retorna lista de strings ordenadas
```

Teste: imprimir quantos jogos únicos existem.

### Passo 7.2 — `query_deals_by_title(title)`

```python
# find({"title": title}).sort("scraped_at", -1)
# Retorna lista de dicts (sem _id ou convertendo)
```

Teste: para um jogo que você sabe que tem 2+ registros, imprimir quantos vieram.

### Passo 7.3 — `build_deal_context(title, proposed_price)`

Calcule com Python puro (sem pandas obrigatório):

- `scrape_count` — len da lista
- `first_seen` / `last_seen` — min e max de `scraped_at`
- `lowest_discounted_price` — min dos `discounted_price`
- `highest_discounted_price` — max
- `average_discounted_price` — soma / quantidade
- `average_discount_pct` — idem
- `recent_snapshots` — últimos 5 registros, só campos úteis

Retorne o dict no formato do README (seção Deal Advisor).

### Passo 7.4 — CLI de teste

`scripts/print_context.py`:

```bash
uv run python scripts/print_context.py "Nome Exato Do Jogo"
```

Use `json.dumps(..., indent=2)` para ler bonito no terminal.

### Erro comum

Título com aspas ou nome ligeiramente diferente — copie o `title` **exato** do Atlas.

---

## Fase 8 — Gemini + site

Divida em **duas metades**: API Python primeiro, HTML depois (pode pedir ajuda no HTML).

### Parte A — `gemini_advisor.py` (você)

1. `uv add google-genai` (quando for implementar)
2. Ler `GEMINI_API_KEY` do `.env`
3. Função `analyze_deal(context)`:
   - Se `scrape_count == 0`, retorne erro sem chamar API
   - Monte um prompt em português ou inglês pedindo JSON: `verdict` + `summary`
   - Compare **só** `proposed_discounted_price` com o histórico
4. Teste com context fake antes do site

### Parte B — `web/app.py` (FastAPI sugerido)

Rotas:

| Rota | O que faz |
|------|-----------|
| `GET /` | Mostra formulário |
| `GET /api/games` | JSON com títulos |
| `POST /api/advise` | Recebe título + preço, chama context + gemini |

Fluxo do POST:

```
receber JSON → build_deal_context → analyze_deal → devolver JSON
```

Rodar:

```bash
uv run uvicorn web.app:app --reload
```

### Parte C — Front (pode usar IA com moderação)

- Um `<select>` preenchido via `/api/games`
- Campo numérico para preço
- Botão que faz `fetch('/api/advise', { method: 'POST', ... })`
- Área que mostra `verdict` e `summary`

**Importante:** mesmo que a IA gere o HTML, **leia** cada tag e teste mudando um texto você mesmo.

---

## Checklist geral (marque na ordem)

- [ ] Fase 4 — paginação funcionando
- [ ] Fase 6 — 3+ dias de dados no Atlas
- [ ] `list_game_titles` e `query_deals_by_title`
- [ ] `build_deal_context` + script de teste
- [ ] `analyze_deal` com Gemini
- [ ] API FastAPI com 3 rotas
- [ ] Página HTML mínima funcionando

---

## Campos opcionais (`genres`, `rating`, `review_count`)

**Não são obrigatórios** para o consultor de preços. Só faça se quiser enriquecer o scraper **depois** que 4–8 estiverem estáveis.

Se fizer: mesma receita — novo campo no `parse_game`, nova regra em `validate_game_record`, teste no Atlas.

---

## Resumo da sua jornada

| Você aprende escrevendo | Pode pedir rascunho à IA |
|-------------------------|---------------------------|
| Paginação, db queries, context, Gemini, rotas API | HTML/CSS mais polido |
| Validações e regras de negócio | Ajustes finos de prompt |
| Testes no terminal e Atlas | |

O projeto já tem uma base **profissional o suficiente** para você evoluir devagar. Confie no processo: uma fase, um teste, um commit mental (“isso funciona”), depois a próxima.

---

[Voltar ao índice](README.md)
