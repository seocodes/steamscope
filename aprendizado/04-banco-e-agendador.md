# 4. Banco de dados e agendador

Arquivos: `application/db.py`, `application/scheduler.py`, `main.py`

---

## `db.py` — a ponte com o MongoDB

### Ideia central

O scraper **não precisa saber** como o MongoDB funciona por dentro. Ele só chama:

```python
insert_deals(lista_de_dicionarios)
```

Isso é **separação de responsabilidades**: um arquivo coleta, outro armazena.

### Funções

| Função | O que faz |
|--------|-----------|
| `get_mongo_uri()` | Lê `MONGO_URI` do `.env`; se não existir, erro claro |
| `create_client()` | Abre conexão com o Atlas |
| `ping_mongodb()` | Testa se o servidor responde (`admin.command("ping")`) |
| `get_deals_collection()` | Aponta para banco `steamscope`, collection `deals` |
| `insert_deals(records)` | `insert_many` e fecha a conexão |

### `load_dotenv()`

Na linha 8: carrega o arquivo `.env` para o Python enxergar variáveis como `MONGO_URI`.

### `insert_deals` em detalhe

```python
client, collection = get_deals_collection()
try:
    result = collection.insert_many(records, ordered=False)
    return len(result.inserted_ids)
finally:
    client.close()
```

- `ordered=False` — se um documento falhar, os outros ainda tentam entrar
- `finally: client.close()` — **sempre** fecha conexão, mesmo com erro

### Rodar só o teste de banco

```bash
uv run python application/db.py
```

Deve imprimir que o ping funcionou.

### O que já foi **adicionado** nas Fases 7–8

Funções novas no **mesmo** arquivo, por exemplo:

- `list_games_titles()` — lista nomes únicos para o dropdown do site
- `query_deals_by_title(title)` — histórico de um jogo

Padrão: mesma estrutura — abre client, usa collection, fecha no `finally`.

---

## `scheduler.py` — o despertador diário

### Fluxo

```
start_scheduler()
  → configure_logging()     # cria logs/scraper.log
  → lê SCRAPE_TIME do .env
  → schedule.every().day.at(horario).do(run_scraper_job)
  → loop infinito: schedule.run_pending() + sleep(1)
```

### `run_scraper_job(logger)`

É uma cópia enxuta do final do `scraper.py`:

1. `fetch_page()`
2. `scrape_deals()`
3. `insert_deals()`

Se a página não carregar, **loga erro e retorna** — não derruba o agendador. Amanhã tenta de novo.

### `RUN_ON_STARTUP`

Se `true`, roda um scrape **imediatamente** ao iniciar — ótimo para testar sem esperar o horário.

### Parar o agendador

`Ctrl+C` no terminal → mensagem “Scheduler stopped by user”.

---

## `main.py` — porta de entrada

Arquivo pequeno de propósito:

```python
from application.scheduler import start_scheduler

def main():
    start_scheduler()

if __name__ == "__main__":
    main()
```

**Por que existe?** Convenção: `uv run python main.py` é fácil de lembrar. Toda a lógica pesada fica em `application/`.

---

## Como os três arquivos conversam

```
main.py
   └── chama start_scheduler() em scheduler.py
           └── chama fetch_page, scrape_deals (scraper.py)
           └── chama insert_deals (db.py)
```

Quando você roda `scraper.py` direto, **pula** o agendador — útil para debug.

---

## Exercício

1. Rode `uv run python main.py` com `RUN_ON_STARTUP=true`.
2. Abra `logs/scraper.log` e leia as linhas como um diário: o que aconteceu?
3. No Atlas, veja se `scraped_at` de documentos novos é de hoje.

Próximo: [05-como-pensar-como-dev.md](05-como-pensar-como-dev.md)
