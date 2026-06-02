# Agent instructions (steamscope)

**Read first:** [.github/copilot-instructions.md](.github/copilot-instructions.md) for build commands, current status, and conventions.

**Step-by-step build guide:** [PLANNING.md](PLANNING.md)

## Current status

| Phase | Status |
|-------|--------|
| 1 — Setup | Done |
| 2 — Scraper (single page) | Done |
| 3 — MongoDB | Done |
| 4 — Pagination | Done |
| 5 — Scheduler + logging | Done |
| 6 — Data collection | Not started |
| 7 — MongoDB analysis (deal context) | Done |
| 8 — Deal advisor + Gemini | In progress (Gemini advisor done; web UI pending) |

## Do not re-implement unless fixing bugs

- `application/scraper.py`: `fetch_page`, `parse_game`, `scrape_deals`, `validate_game_record`
- `application/db.py`: `insert_deals`, `get_deals_collection`
- `application/scheduler.py`: daily job via `SCRAPE_TIME`

## Schema note

MongoDB documents today include: `title`, `url`, `original_price`, `discounted_price`, `discount_pct`, `scraped_at`. That is enough for Phases 7–8 (price history over time). Optional fields `genres`, `rating`, and `review_count` enrich AI context but are not required — do not assume they exist in the database yet.

## Files (Phases 7–8)

| File | Purpose | Status |
|------|---------|--------|
| `application/context.py` | Build deal context JSON from MongoDB history | Done |
| `application/gemini_advisor.py` | Call Gemini with context; return verdict | Done (returns text) |
| `web/app.py` | FastAPI deal advisor site | Not started |
| `scripts/print_context.py` | CLI to dump context JSON for testing | Not started (current smoke test: `application/test_context.py`) |
