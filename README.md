# SteamScope

SteamScope e um MVP em Python para acompanhar descontos da Steam e usar o historico coletado para responder uma pergunta simples:

> Esse preco promocional parece bom para este jogo?

O projeto esta em um ponto funcional para estudo e uso local, mas ainda nao esta pronto como produto. Por enquanto, ele fica como esta: scraper, persistencia, API, interface web simples, cache/rate limit e testes basicos.

## Situacao Atual

O que ja existe:

- Scraper de promocoes da Steam com parsing via BeautifulSoup.
- Validacao basica dos registros coletados.
- Escrita idempotente no MongoDB usando `idempotency_key` e upsert.
- Scheduler diario configuravel por variaveis de ambiente.
- Geracao de contexto historico por jogo.
- Advisor com Google Gemini retornando um JSON de recomendacao.
- App FastAPI com pagina HTML simples e endpoint JSON.
- Redis para rate limit por IP e cache de respostas do advisor.
- Testes unitarios para validacao da API, cache/rate limit e parsing da resposta do Gemini.
- CI no GitHub Actions rodando Ruff e pytest.

O que ainda esta cru:

- A UI apenas envia o formulario e mostra o JSON bruto da resposta.
- O scraper depende da estrutura atual da pagina da Steam, entao pode quebrar se o HTML mudar.
- O historico so fica realmente util depois de varios dias de coleta.
- Nao ha deploy configurado.
- Nao ha camada de autenticacao, observabilidade ou tratamento operacional mais robusto.
- O projeto exige MongoDB, Redis e chave do Gemini para o fluxo completo.

## Stack

| Area | Ferramentas |
| --- | --- |
| Scraping | `requests`, `beautifulsoup4` |
| Banco | MongoDB Atlas, `pymongo` |
| Backend | FastAPI, Pydantic, Jinja2 |
| IA | Google Gemini API (`google-genai`) |
| Cache / rate limit | Redis, `redis-py` |
| Scheduler | `schedule` |
| Testes | `pytest`, `ruff` |
| Ambiente | `uv`, `python-dotenv` |

## Estrutura

```text
steamscope/
├── application/
│   ├── context.py             # Monta o contexto historico do jogo
│   ├── context_smoke_test.py  # Smoke test manual do fluxo de contexto/advisor
│   ├── db.py                  # Conexao e consultas MongoDB
│   ├── gemini_advisor.py      # Prompt, chamada Gemini e parsing da resposta
│   ├── redis_client.py        # Cliente Redis, rate limit e cache keys
│   ├── scheduler.py           # Agendamento diario do scraper
│   └── scraper.py             # Scraper e parser das promocoes da Steam
├── tests/
│   ├── test_api_validation.py
│   ├── test_gemini_advisor.py
│   └── test_redis_client.py
├── web/
│   ├── app.py                 # App FastAPI
│   ├── static/script.js       # Submit do formulario
│   └── templates/index.html   # UI simples do advisor
├── main.py                    # Entrada do scheduler
├── pyproject.toml
├── uv.lock
├── PLANNING.md
└── README.md
```

## Fluxo Principal

```text
Scraper
  -> Steam specials
  -> parser/validacao
  -> MongoDB

Web advisor
  -> FastAPI
  -> Pydantic validation
  -> Redis rate limit
  -> Redis cache lookup
  -> MongoDB historico por titulo
  -> Gemini
  -> Redis cache write
  -> JSON response
```

## Modelo de Dados

Cada documento em `steamscope.deals` representa um jogo visto em uma execucao do scraper:

```json
{
  "title": "Elden Ring",
  "original_price": 199.99,
  "discounted_price": 99.99,
  "discount_pct": 50,
  "url": "https://store.steampowered.com/app/...",
  "steam_app_id": "1245620",
  "scraped_at": "2026-06-10T06:00:00",
  "scraped_date": "2026-06-10",
  "idempotency_key": "steam_specials:1245620:2026-06-10"
}
```

## Setup Local

Prerequisitos:

- Python 3.14+
- `uv`
- MongoDB Atlas ou MongoDB acessivel por URI
- Redis local ou remoto
- Chave da Google Gemini API

Instale as dependencias:

```bash
uv sync --dev
```

Crie o `.env`:

```bash
cp .env.example .env
```

Variaveis esperadas:

```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/steamscope
SCRAPE_TIME=06:00
RUN_ON_STARTUP=false
GEMINI_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379/0
ADVISOR_CACHE_TTL_SECONDS=300
RATE_LIMIT_PERIOD_SECONDS=45
RATE_LIMIT_MAX_REQUESTS=5
```

Redis local com Docker:

```bash
docker run --name steamscope-redis -p 6379:6379 redis:7-alpine
```

Se o container ja existir:

```bash
docker start steamscope-redis
```

## Como Rodar

Testar conexao com MongoDB:

```bash
uv run python application/db.py
```

Rodar o scraper manualmente:

```bash
uv run python application/scraper.py
```

Rodar o scheduler:

```bash
uv run python main.py
```

Rodar a web UI:

```bash
uv run uvicorn web.app:app --reload
```

Depois acesse:

```text
http://127.0.0.1:8000
```

## API

| Rota | Metodo | Descricao |
| --- | --- | --- |
| `/` | `GET` | Renderiza a pagina com os jogos encontrados no MongoDB |
| `/api/advise` | `POST` | Analisa um preco proposto para um jogo |

Request:

```json
{
  "title": "Elden Ring",
  "proposed_price": 39.99
}
```

Response esperada:

```json
{
  "verdict": "good",
  "summary": "The proposed price is below the recent average but not the historical low.",
  "confidence": 80,
  "key_insights": [
    "Recent prices are higher than the proposed price",
    "Historical low is still lower than this offer"
  ]
}
```

O endpoint tambem usa o header `X-Cache` com valores como `HIT`, `MISS` ou `BYPASS`.

## Testes

Rodar tudo:

```bash
uv run python -m pytest
```

Rodar lint:

```bash
uv run ruff check .
```

O CI em `.github/workflows/ci.yml` roda os dois em push e pull request.

## Nota Final

Este repositorio esta em um bom ponto de pausa para um projeto de aprendizado: a ideia principal esta implementada de ponta a ponta, com integracoes reais e testes basicos. O proximo trabalho relevante, se o projeto voltar a andar, seria polir a UI, fortalecer o scraper e preparar uma estrategia simples de deploy/configuracao.

## License

MIT
