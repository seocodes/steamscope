# Copilot Instructions for steamscope

A Steam deals tracker that scrapes game discounts over time, stores them in MongoDB, and uses historical deal analysis plus a Gemini-powered advisor to judge whether a proposed discount is good.

See also [AGENTS.md](../AGENTS.md) and [PLANNING.md](../PLANNING.md).

---

## Current status (update when merging phases)

| Phase | Status |
|-------|--------|
| 1 — Setup | Done |
| 2 — Scraper (single page) | Done |
| 3 — MongoDB | Done |
| 4 — Pagination | **Next** |
| 5 — Scheduler + logging | Done |
| 6 — Data collection | Not started |
| 7 — MongoDB analysis (deal context) | Not started |
| 8 — Deal advisor + Gemini | Not started |

**Do not re-implement** unless fixing bugs: `fetch_page`, `parse_game`, `scrape_deals`, `validate_game_record`, `insert_deals`, `start_scheduler`.

**Dual imports:** `scraper.py` and `scheduler.py` use `try: from application.X` / `except ModuleNotFoundError: from X` so they work both as `uv run python application/scraper.py` and as package imports. Do not remove this pattern.

---

## Definition of done (by phase)

| Phase | Done when |
|-------|-----------|
| 2 | One Steam specials page scrapes; records validate; manual run inserts to MongoDB |
| 3 | `MONGO_URI` in `.env`; `insert_deals` works; `uv run python application/db.py` pings |
| 4 | 4–5 pages per run via `&page={n}` on search URL; 100+ unique games logged |
| 5 | `uv run python main.py` runs daily at `SCRAPE_TIME`; `logs/scraper.log` has run lines |
| 6 | Scheduler ran 3–5 days; document count grows in Atlas |
| 7 | `build_deal_context(title)` returns valid JSON for a title with 2+ scrape rows; CLI test works |
| 8 | Local web UI: pick game + proposed price → Gemini verdict displayed; missing game / missing API key handled |

---

## Build & Run Commands

All commands use [`uv`](https://github.com/astral-sh/uv) — deterministic installs via `uv.lock`.

### Install Dependencies
```bash
uv sync
```
Installs production + dev dependencies (jupyter, pandas, matplotlib for optional exploration).

### MongoDB Connection Test
```bash
uv run python application/db.py
```

### Run Scraper (Manual)
```bash
uv run python application/scraper.py
```
Fetches one Steam specials page, parses deals, validates records, inserts into MongoDB.

### Run Scheduler (Background)
```bash
uv run python main.py
```
Runs the scraper **once per day** at `SCRAPE_TIME` (default `06:00`, 24h `HH:MM`). Set `RUN_ON_STARTUP=true` in `.env` for an immediate first run.

### Deal Advisor Web App (Phase 8 — planned)
```bash
uv run uvicorn web.app:app --reload
```
Requires `GEMINI_API_KEY` in `.env` and Phase 7 context builder implemented.

### Jupyter Notebook (optional)
```bash
uv run jupyter notebook analysis/notebook.ipynb
```
For exploratory charts only — not required for Phases 7–8.

### Tests (not yet set up)

There is no `tests/` directory and no `pytest` dependency yet. When adding tests:
- `uv add --dev pytest`
- Mock HTTP with `unittest.mock.patch`; mock MongoDB with `mongomock` or a test DB
- Do not hit Steam on every CI run

---

## Architecture & Phases

The project is built in **8 phases**:

1. **Phase 1**: Project setup ✓
2. **Phase 2**: Basic scraper (single page, validation, DB insert) ✓
3. **Phase 3**: MongoDB integration ✓
4. **Phase 4**: Pagination (4–5 pages per run, ~100–125 games) — **next**
5. **Phase 5**: Scheduler + logging (daily `SCRAPE_TIME`, `logs/scraper.log`) ✓
6. **Phase 6**: Data collection (let it run 3–5 days)
7. **Phase 7**: MongoDB queries + deal context JSON builder
8. **Phase 8**: Deal advisor website + Google Gemini API

### Data Flow
```
Steam Web Page → requests → BeautifulSoup (parse HTML)
                            ↓
                        Dict per game
                            ↓
                        MongoDB insert
                            ↓
                        Query history by title
                            ↓
                        Deal context JSON
                            ↓
                        Gemini API → verdict
                            ↓
                        Web UI (game + proposed price)
```

### File Organization

| File | Phase(s) | Purpose |
|------|----------|---------|
| `application/scraper.py` | 2–4 | Fetch HTML, parse deals, pagination |
| `application/db.py` | 3–7 | MongoDB connection, insert, queries |
| `application/scheduler.py` | 5 | Daily job + file logging |
| `application/context.py` | 7 | Build deal context JSON |
| `application/gemini_advisor.py` | 8 | Call Gemini; return verdict |
| `main.py` | 5 | Entry point; starts scheduler |
| `web/app.py` | 8 | FastAPI deal advisor site |
| `web/templates/index.html` | 8 | Player form + verdict display |
| `scripts/print_context.py` | 7 | CLI test for context JSON |
| `analysis/notebook.ipynb` | optional | Exploratory charts only |
| `logs/scraper.log` | 5+ | Auto-generated; one line per run |

---

## Key Conventions

### Environment Variables
- Store secrets in `.env` (never commit)
- Template: `.env.example` (committed)
- Variables:
  - `MONGO_URI` — MongoDB Atlas connection string
  - `SCRAPE_TIME` — daily run time, `HH:MM` (default `06:00`)
  - `RUN_ON_STARTUP` — `true` / `false` (default `false`)
  - `GEMINI_API_KEY` — Google AI Studio key (Phase 8)
- Loaded with `python-dotenv` in `db.py` (extend to advisor modules as needed)

### Dependencies Management
- **Production**: `pyproject.toml` `[project] dependencies`
  - `requests`, `beautifulsoup4`, `pymongo`, `python-dotenv`, `schedule`
- **Production (Phase 8 — add when implementing)**: `fastapi`, `uvicorn`, `google-genai`, `jinja2`
- **Dev**: `[dependency-groups] dev`
  - `jupyter`, `pandas`, `matplotlib`, `seaborn` (optional exploration)
- Install all: `uv sync`
- Install prod only: `uv sync --no-dev`

### Code Style
- Python 3.14+ (`.python-version`, `requires-python` in `pyproject.toml`)
- BeautifulSoup with `html.parser`
- HTTP requests need a realistic `User-Agent` (Steam blocks bare bots)
- Try/except per field in `parse_game`; invalid records skipped, not fatal

### Scraper Implementation Notes
- Base URL: `https://store.steampowered.com/search/?specials=1`
- Pagination: append `&page={n}` for Phase 4
- **Polite scraping:** `time.sleep(1)` between page requests and between deal processing
- HTML: `search_result_row`, `discount_pct`, `discount_original_price`, `discount_final_price`
- Retries with exponential backoff in `fetch_page`

### Logging
- Scheduler logger: `steamscope.scheduler` → `logs/scraper.log` + console
- Scraper uses module-level `logging` when run directly

### Deal Advisor (Phase 8)

- **Input:** Player selects `title` and enters `proposed_discounted_price`.
- **Context:** Built by `application/context.py` from MongoDB history (min/max/avg prices, recent snapshots).
- **AI:** Google Gemini (free-tier flash model via `google-genai`); prompt compares proposed price to history only.
- **Output JSON:** `{ "verdict": "good|fair|wait", "summary": "..." }` for the web UI.
- **Guardrails:** No Gemini call if the game has no scrape history; clear error if `GEMINI_API_KEY` is missing.

**Planned routes:**

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Render form |
| `/api/games` | GET | Distinct titles from MongoDB |
| `/api/advise` | POST | `{ "title": "...", "proposed_price": 29.99 }` → verdict |

---

## MongoDB Schema

### Current document shape

```json
{
  "title": "Elden Ring",
  "original_price": 199.99,
  "discounted_price": 99.99,
  "discount_pct": 50,
  "url": "https://store.steampowered.com/app/...",
  "scraped_at": "2025-03-25T14:00:00"
}
```

Sufficient for Phases 7–8 (price history over `scraped_at`).

### Optional enrichment fields

```json
{
  "genres": ["RPG", "Action"],
  "rating": "Very Positive",
  "review_count": 120400
}
```

Improve AI context but are not required for the deal advisor.

Collection: `steamscope.deals` (database: `steamscope`, collection: `deals`)

---

## Development Tips

- **Phase workflow:** [PLANNING.md](../PLANNING.md) for step-by-step tasks; update the status table above when a phase merges
- **Manual first:** Run `uv run python application/scraper.py` before changing the scheduler
- **Atlas:** Confirm inserts in the MongoDB Atlas UI
- **Scheduler test:** Use `RUN_ON_STARTUP=true` or set `SCRAPE_TIME` a few minutes ahead instead of waiting until tomorrow
- **Phase 7 test:** Use `scripts/print_context.py` to validate JSON before wiring Gemini
- **Gemini:** Get API key from [Google AI Studio](https://aistudio.google.com/); store as `GEMINI_API_KEY`

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.33.0 | HTTP requests to Steam |
| `beautifulsoup4` | ≥4.14.3 | HTML parsing |
| `pymongo` | ≥4.16.0 | MongoDB driver |
| `python-dotenv` | ≥1.2.2 | Load `.env` variables |
| `schedule` | ≥1.2.2 | Job scheduling |
| `fastapi` | (Phase 8) | Deal advisor web API |
| `uvicorn` | (Phase 8) | ASGI server |
| `google-genai` | (Phase 8) | Gemini API client |
| `pandas` | ≥3.0.1 (dev) | Optional data exploration |
| `matplotlib` | ≥3.10.8 (dev) | Optional plotting |
| `seaborn` | ≥0.13.2 (dev) | Optional statistical plots |
| `jupyter` | ≥1.1.1 (dev) | Optional notebooks |
