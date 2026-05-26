# 2. Como rodar o projeto (sem dor de cabeça)

## O erro que você teve

Você rodou:

```bash
python3 application/scraper.py
```

Isso usa o Python **do sistema** (`/usr/bin/python3`). Esse Python **não tem** as bibliotecas do projeto (`dotenv`, `pymongo`, `requests`, etc.).

Por isso apareceu:

- `No module named 'application'` — o script não está no “modo pacote”
- depois `No module named 'dotenv'` — o `db.py` até foi encontrado, mas sem as libs instaladas

**Solução:** use sempre o ambiente do projeto com **uv**.

---

## Comandos que você deve memorizar

Sempre na **pasta raiz** do projeto (`steamscope/`, onde está o `main.py`):

```bash
# 1) Instalar dependências (primeira vez ou depois de mudar pyproject.toml)
uv sync

# 2) Testar conexão com MongoDB
uv run python application/db.py

# 3) Rodar o scraper uma vez (manual)
uv run python application/scraper.py

# 4) Rodar o agendador (fica ligado, scrape diário)
uv run python main.py
```

Pense no `uv run` como: *“usa o Python certo, com as bibliotecas certas, deste projeto”*.

---

## Arquivo `.env`

Na raiz você precisa de um `.env` (copie de `.env.example`):

```
MONGO_URI=mongodb+srv://usuario:senha@cluster....mongodb.net/steamscope
SCRAPE_TIME=06:00
RUN_ON_STARTUP=false
```

| Variável | Para quê |
|----------|----------|
| `MONGO_URI` | Endereço do MongoDB Atlas |
| `SCRAPE_TIME` | Horário do scrape diário (24h, ex: `06:00`) |
| `RUN_ON_STARTUP` | Se `true`, roda um scrape logo ao iniciar o `main.py` |

Sem `MONGO_URI` válido, o scraper pode até extrair jogos, mas **falha na hora de salvar**.

---

## Testar sem esperar até amanhã

No `.env`:

```
RUN_ON_STARTUP=true
```

Depois:

```bash
uv run python main.py
```

Você deve ver no terminal (e em `logs/scraper.log`) que o scrape rodou na hora.

Para testar só o scraper, sem agendador:

```bash
uv run python application/scraper.py
```

---

## Onde ver se deu certo

1. **Terminal** — mensagens `INFO`, quantos jogos foram inseridos.
2. **MongoDB Atlas** — painel web → Database → `steamscope` → collection `deals` → Browse Documents.
3. **`logs/scraper.log`** — quando usa o agendador.

---

## Analogia rápida

| Coisa | Analogia |
|-------|----------|
| `pyproject.toml` | Lista de compras de ingredientes |
| `uv sync` | Ir ao mercado comprar tudo |
| `uv run python ...` | Cozinhar usando **só** esses ingredientes |
| `python3` direto | Cozinhar na casa vizinha que não tem os ingredientes |

---

## Próximo passo

Com o scraper rodando pelo menos uma vez e documentos no Atlas, leia [03-scraper-explicado.md](03-scraper-explicado.md) para entender **como** o código faz isso.
