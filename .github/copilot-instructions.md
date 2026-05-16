# Copilot Instructions for steamscope

A Steam deals tracker that scrapes game discounts over time, stores them in MongoDB, and performs analysis + ML classification.

## Build & Run Commands

All commands use [`uv`](https://github.com/astral-sh/uv) — a fast Python package manager with deterministic installs via `uv.lock`.

### Install Dependencies
```bash
uv sync
```
Installs exact versions from `uv.lock` (includes dev dependencies like jupyter, pandas, matplotlib, scikit-learn).

### Run Scraper (Manual)
```bash
uv run python application/scraper.py
```
Fetches Steam deals page, parses HTML with BeautifulSoup, prints game titles and prices to console.

### Run Scheduler (Background)
```bash
uv run python main.py
```
Starts the scheduler that runs the scraper automatically every 6 hours (configurable in `application/scheduler.py`).

### Run Tests
```bash
uv run python -m pytest tests/
```
Runs unit tests for scraper and database modules. Tests are empty stubs as of Phase 2.

### Run Single Test
```bash
uv run python -m pytest tests/test_scraper.py::test_name -v
```

### Jupyter Notebook
```bash
uv run jupyter notebook analysis/notebook.ipynb
```
Interactive environment for data analysis and ML model training (Phase 7-8).

## Architecture & Phases

**Current Status**: Phase 2 (Basic Scraper) — Single page fetching and HTML parsing working

The project is built in **8 phases**, each adding a layer:

1. **Phase 1**: Project setup ✓
2. **Phase 2**: Basic scraper (single page, console output) ✓ **(current)**
3. **Phase 3**: MongoDB integration (connection + inserts)
4. **Phase 4**: Pagination (scrape 4–5 pages per run, ~100–125 games)
5. **Phase 5**: Scheduler + logging (auto-run every 6–12h, write to `logs/scraper.log`)
6. **Phase 6**: Data collection (let it run 3–5 days)
7. **Phase 7**: Visualization (matplotlib + seaborn; 4+ charts)
8. **Phase 8**: ML model (RandomForest classifier for "great deals")

### Data Flow
```
Steam Web Page → requests → BeautifulSoup (parse HTML)
                            ↓
                        Dict per game
                            ↓
                        MongoDB insert
                            ↓
                        pandas + jupyter
                            ↓
                        Charts + ML
```

### File Organization

| File | Phase(s) | Purpose |
|------|----------|---------|
| `application/scraper.py` | 2–4, 10 | Fetch HTML, parse deals, pagination |
| `application/db.py` | 3–5 | MongoDB connection, insert/query logic |
| `application/scheduler.py` | 5–8 | Job scheduler with error handling |
| `main.py` | 5–8 | Entry point; starts scheduler |
| `analysis/notebook.ipynb` | 7–8 | Data analysis, visualizations, ML training |
| `tests/` | All | Unit tests for scraper and DB |
| `logs/scraper.log` | 5+ | Auto-generated; one line per run |

## Key Conventions

### Environment Variables
- Store secrets in `.env` (never commit)
- Template: `.env.example` (committed, safe)
- Required: `MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/steamscope`
- Load with `python-dotenv` in `db.py`

### Dependencies Management
- **Production**: Listed in `[project] dependencies` in `pyproject.toml`
  - `requests`, `beautifulsoup4`, `pymongo`, `python-dotenv`, `schedule`
- **Dev** (optional): Listed in `[dependency-groups] dev` in `pyproject.toml`
  - `jupyter`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`
- Install all: `uv sync`
- Install prod only: `uv sync --no-dev`
- Add new: `uv add package_name` (or `uv add --dev package_name`)

### Code Style
- Python 3.14+ (pinned in `.python-version`)
- BeautifulSoup for HTML parsing (uses `html.parser`)
- HTTP requests with `User-Agent` header (Steam blocks requests without it)
- MongoDB documents are dicts with fields: `title`, `original_price`, `discounted_price`, `discount_pct`, `genres`, `rating`, `review_count`, `url`, `scraped_at`
- Try/except for graceful handling of missing HTML elements (prices, ratings may not always be present)

### Scraper Implementation Notes
- **Polite scraping**: Add `time.sleep(1)` between page requests to avoid overwhelming the server
- **HTML structure**: Steam's search results page uses `search_result_row` class for game containers; look for nested divs with classes like `discount_pct`, `discount_original_price`, `discount_final_price`
- **Error handling**: Missing price/rating data is expected and should be handled gracefully (don't crash; log a warning)
- **User-Agent required**: Steam blocks requests without a realistic User-Agent header (already implemented)

### Logging
- Use Python's built-in `logging` module
- Log file: `logs/scraper.log` (created automatically; not committed)
- Format: Include timestamp, log level, and message
- Scheduler should catch exceptions and log them without crashing

### ML Target & Features
- **Target variable**: `is_great_deal` = `discount_pct >= 50` AND `rating` in ["Very Positive", "Mostly Positive"]
- **Features**: genre (encoded), original price, review count, day of week scraped
- **Model**: `RandomForestClassifier` from `scikit-learn`
- **Evaluation**: accuracy score + confusion matrix

## Testing

Test files exist but are empty stubs:
- `tests/test_scraper.py` — test `fetch_page()` and `parse_deals()`
- `tests/test_db.py` — test MongoDB connection and insert logic

### Test Writing Checklist (for future phases)
- Mock HTTP requests (use `unittest.mock.patch` to avoid hitting Steam on every test run)
- Mock MongoDB (use a local test database or `mongomock`)
- Test parsing logic with sample HTML
- Test error handling (missing fields, network errors, DB connection failures)

## Development Tips

- **Phase-based workflow**: Check `PLANNING.md` for detailed step-by-step implementation guide
- **Test manually first**: Run scraper manually (`uv run python application/scraper.py`) before integrating with scheduler
- **Check MongoDB Atlas**: Verify documents are being inserted by viewing the Atlas dashboard (free tier)
- **Scheduler testing**: Temporarily set to `schedule.every(1).minutes.do(job)` to verify scheduling works without waiting 6 hours
- **Jupyter**: Notebooks are isolated from the main app; use them for exploration and prototyping. Extract production code to modules.

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.33.0 | HTTP requests to Steam |
| `beautifulsoup4` | ≥4.14.3 | HTML parsing |
| `pymongo` | ≥4.16.0 | MongoDB driver |
| `python-dotenv` | ≥1.2.2 | Load `.env` variables |
| `schedule` | ≥1.2.2 | Job scheduling |
| `pandas` | ≥3.0.1 (dev) | Data manipulation |
| `matplotlib` | ≥3.10.8 (dev) | Plotting |
| `seaborn` | ≥0.13.2 (dev) | Statistical plots |
| `scikit-learn` | ≥1.8.0 (dev) | ML models |
| `jupyter` | ≥1.1.1 (dev) | Notebooks |

## MongoDB Schema

Each scraped game is stored as a document:

```json
{
  "title": "Elden Ring",
  "original_price": 199.99,
  "discounted_price": 99.99,
  "discount_pct": 50,
  "genres": ["RPG", "Action"],
  "rating": "Very Positive",
  "review_count": 120400,
  "url": "https://store.steampowered.com/app/...",
  "scraped_at": "2025-03-25T14:00:00"
}
```

Collection: `steamscope.deals` (database: `steamscope`, collection: `deals`)
