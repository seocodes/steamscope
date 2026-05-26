# 3. O `scraper.py` explicado

Este é o arquivo mais importante **hoje**. Vale abrir `application/scraper.py` lado a lado com este texto.

---

## O que o arquivo faz (uma frase)

**Baixa a página de ofertas da Steam, transforma cada jogo em um dicionário Python, valida, e manda salvar no MongoDB.**

---

## As funções (quem faz o quê)

```
fetch_page()        → baixa HTML e vira objeto BeautifulSoup
scrape_deals()      → percorre todos os jogos da página
parse_game()        → extrai dados de UM jogo
validate_game_record() → confere se o dicionário faz sentido
(main)              → orquestra tudo e chama insert_deals()
```

Pense numa linha de produção:

```
Internet → fetch_page → scrape_deals → parse_game → validate → lista → MongoDB
```

---

## Imports no topo

```python
import re, requests, logging, time
from datetime import datetime
from bs4 import BeautifulSoup
```

| Biblioteca | Papel simples |
|------------|----------------|
| `requests` | Abre URLs como um navegador |
| `BeautifulSoup` | Lê HTML bagunçado e acha pedaços (título, preço) |
| `re` | Pega números dentro de textos tipo "R$ 49,99" |
| `logging` | Escreve mensagens de progresso/erro |
| `datetime` | Marca **quando** foi a coleta (`scraped_at`) |

O bloco `try/except` dos imports:

```python
try:
    from application.db import insert_deals
except ModuleNotFoundError:
    from db import insert_deals
```

Isso permite rodar de dois jeitos (`uv run python application/scraper.py` ou importando como pacote). **Não precisa mexer nisso agora.**

---

## `validate_game_record(record)`

**Por que existe?** A Steam muda o HTML, ou um jogo vem sem preço. Se salvar lixo no banco, depois a análise e a IA ficam erradas.

Ela checa, por exemplo:

- Título existe e tem tamanho razoável (3–200 caracteres)
- URL contém `steampowered.com`
- Preços são números e o preço com desconto não é maior que o original
- Desconto entre 0 e 100%
- Tem `scraped_at`

Retorna `(True, "")` se ok, ou `(False, "mensagem do erro")`.

**Como você pensaria isso do zero:** antes de salvar qualquer coisa, pergunte *“eu confiaria nesse dado numa planilha?”* Se não, descarte e registre no log.

---

## `fetch_page(max_retries=3, timeout=10)`

**Passo a passo:**

1. Monta a URL: `https://store.steampowered.com/search/?specials=1`
2. Manda um **User-Agent** (finge ser um navegador — Steam bloqueia robôs óbvios)
3. `requests.get(..., timeout=10)` — espera no máximo 10 segundos
4. Se der erro de rede, **tenta de novo** até 3 vezes, esperando 1s, 2s, 4s entre tentativas (isso se chama *backoff*)
5. Se funcionar, devolve `BeautifulSoup` do HTML; se não, `None`

**Do zero:** sempre assuma que a internet falha. Nunca faça um único `get` sem timeout e sem segunda chance.

---

## `scrape_deals(page, rate_limit_delay=1)`

1. `page.find_all("a", class_="search_result_row")` — acha **cada linha de jogo** no HTML
2. Para cada uma, chama `parse_game(deal)`
3. Usa um `set` chamado `seen_urls` para não repetir o mesmo jogo na mesma execução
4. `time.sleep(1)` entre jogos — educação com o servidor da Steam (não bombardear)

Retorna uma **lista** de dicionários válidos.

---

## `parse_game(element)`

Cada `element` é um pedaço de HTML de **um** jogo.

### Campos críticos (se falhar, descarta o jogo)

- **title** — `<span class="title">`
- **url** — atributo `href` do link

### Campos com fallback (se falhar, usa 0 ou continua)

- **discount_pct** — `<div class="discount_pct">`, tira só os dígitos com `re`
- **original_price** / **discounted_price** — classes `discount_original_price` e `discount_final_price`

Exemplo mental do preço:

```text
HTML: "R$ 49,99"
re.findall(r"\d+[.,]\d+", ...) → ["49,99"]
replace(",", ".") → float 49.99
```

No final:

```python
record["scraped_at"] = datetime.now().isoformat()
is_valid, error_msg = validate_game_record(record)
```

Se inválido → `return None` (jogo ignorado).

---

## O bloco `if __name__ == "__main__":`

Só roda quando você executa o arquivo diretamente:

```python
page = fetch_page(...)
valid_records = scrape_deals(page)
inserted_count = insert_deals(valid_records)
```

É o **roteiro do filme**: buscar → extrair → salvar.

---

## Exercício para fixar (faça você mesmo)

1. Rode o scraper e anote quantos jogos válidos aparecem no log.
2. Abra o Atlas e confira **um** documento — os campos batem com o que o código monta?
3. (Opcional) Comente temporariamente a validação de URL e veja o que acontece — depois desfaça. Aprender vendo quebra é válido.

---

## O que **você** vai mudar na Fase 4 (paginação)

Hoje `fetch_page` usa **uma URL fixa**. Na Fase 4 você vai:

- Passar o número da página na URL: `&page=2`, `&page=3`...
- Chamar `fetch_page` várias vezes num loop
- Juntar listas com `.extend()`

O `parse_game` e `validate_game_record` **quase não mudam**. Só quem orquestra muda.

Próximo: [04-banco-e-agendador.md](04-banco-e-agendador.md)
