# Agent instructions (steamscope)

**Read first:** [.github/copilot-instructions.md](.github/copilot-instructions.md) for build commands, current status, and conventions.

**Step-by-step build guide:** [PLANNING.md](PLANNING.md)

## Current status

| Phase | Status |
|-------|--------|
| 1 — Setup | Done |
| 2 — Scraper (single page) | Done |
| 3 — MongoDB | Done |
| 4 — Pagination | **Next** |
| 5 — Scheduler + logging | Done |
| 6 — Data collection | Not started |
| 7–8 — Notebook + ML | Not started |

## Do not re-implement unless fixing bugs

- `application/scraper.py`: `fetch_page`, `parse_game`, `scrape_deals`, `validate_game_record`
- `application/db.py`: `insert_deals`, `get_deals_collection`
- `application/scheduler.py`: daily job via `SCRAPE_TIME`

## Schema note

MongoDB documents today include only: `title`, `url`, `original_price`, `discounted_price`, `discount_pct`, `scraped_at`. Fields `genres`, `rating`, and `review_count` are planned before Phases 7–8 — do not assume they exist in the database yet.
