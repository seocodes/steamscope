# Steamscope Coding Plan

Simple steps to build the project, broken down until each step uses basic Python features.

**Progress:** Phases 1–3 and 5 are implemented. **Next:** Phase 4 (pagination), then Phase 6 (data collection), then Phase 7 (MongoDB deal context) and Phase 8 (deal advisor website + Gemini).

---

## Phase 2 — Basic Scraper (Single Page) ✓

### Step 1: Fetch Steam Deals Page ✓
**Goal:** Get HTML from Steam's deals page

**Python features:**
- `requests.get()` — fetch a URL
- `response.status_code` — check if request succeeded (200)
- `response.text` — get HTML as string

**Test:** Print first 500 characters of HTML to verify it loaded

---

### Step 2: Parse HTML with BeautifulSoup ✓
**Goal:** Extract game data from the HTML

**Python features:**
- `BeautifulSoup(html, 'html.parser')` — create soup object
- `.find()` / `.find_all()` — locate elements by class/tag
- `.get_text()` — extract text from elements
- `.get('attribute')` — extract attributes (like `href`)
- List comprehensions — build lists of data

**Test:** Print the title and price of the first 3 games

---

### Step 3: Extract Structured Data ✓ (partial)
**Goal:** Build a dictionary for each game with all fields

**Implemented now:** `title`, `original_price`, `discounted_price`, `discount_pct`, `url`, `scraped_at`

**Optional enrichment (not required for deal advisor):**
- `genres` — list of strings
- `rating` — string
- `review_count` — int

**Python features:**
- Dictionaries — `{'key': value}`
- String methods: `.strip()`, `.replace()`
- Regular expressions (`re.findall`) — extract numbers from prices
- Try/except — handle missing data gracefully
- Functions — `def parse_game(element):`

**Test:** Print a list of 5 game dictionaries

---

## Phase 3 — MongoDB Integration ✓

### Step 4: Connect to MongoDB ✓
**Goal:** Store scraped data persistently

**Python features:**
- `pymongo.MongoClient(uri)` — connect to database
- Environment variables (`os.getenv`) — hide credentials
- `.steamscope.deals` — select database and collection

**Test:** `uv run python application/db.py` — ping succeeds

---

### Step 5: Create Insert Function ✓
**Goal:** Save list of game dictionaries to MongoDB

**Python features:**
- `.insert_many(documents)` — batch insert
- `.insert_one(document)` — single insert
- List of dictionaries — `[{'title': '...'}, {'title': '...'}]`

**Test:** Scrape one page, insert all games, count documents in collection

---

## Phase 4 — Pagination

### Step 6: Scrape Multiple Pages
**Goal:** Get 100-125 games per run (4-5 pages)

**Python features:**
- For loop: `for page_num in range(1, 6):`
- F-strings: `f"https://store.steampowered.com/search/?specials=1&page={page_num}"`
- `time.sleep(1)` — polite delay between requests
- `.extend()` — combine lists from multiple pages

**Test:** Print total games scraped, verify count is 100+

---

## Phase 5 — Scheduler + Logging ✓

### Step 7: Add Basic Logging ✓
**Goal:** Track what the scraper does

**Python features:**
- `logging` module
- `logging.FileHandler` → `logs/scraper.log`
- `logger.info()`, `logger.error()`
- `Path.mkdir(parents=True, exist_ok=True)`

**Test:** Run scheduler, check that `logs/scraper.log` exists

---

### Step 8: Create Scheduler ✓
**Goal:** Run scraper automatically on a daily schedule

**Python features:**
- `schedule.every().day.at(scrape_time).do(job)` — `scrape_time` from `SCRAPE_TIME` env (default `06:00`)
- `while True:` loop with `schedule.run_pending()` and `time.sleep(1)`
- `RUN_ON_STARTUP=true` — optional immediate run on start
- Errors logged without crashing the loop

**Test:** Set `SCRAPE_TIME` a few minutes ahead, or use `RUN_ON_STARTUP=true`, verify log entries

---

### Step 9: Create Entry Point ✓
**Goal:** Run everything with `python main.py`

**Python features:**
- `if __name__ == '__main__':`
- Import `start_scheduler` from `application.scheduler`

**Test:** Run `uv run python main.py`, verify scheduler starts

---

## Phase 6 — Data Collection

### Step 10: Let It Run
**Goal:** Collect data for 3-5 days

- Run `uv run python main.py` and leave it running
- Verify logs show successful scrapes
- Check MongoDB Atlas dashboard for growing document count

---

## Phase 7 — MongoDB Analysis for Deal Context

**Prerequisite:** Phase 6 — at least a few days of scrape history per game (current schema is enough).

### Step 11: Query Deals by Title
**Goal:** Load historical scrape rows for one game from MongoDB

**Python features:**
- `collection.find({"title": title})` — exact match (or regex for fuzzy match later)
- `collection.distinct("title")` — list games for the web dropdown
- Sort by `scraped_at` — `sort("scraped_at", -1)`

**Files:** extend `application/db.py` with `query_deals_by_title()`, `list_game_titles()`

**Test:** Print row count and last 3 snapshots for a known title

---

### Step 12: Build Deal Context JSON
**Goal:** Aggregate history into a compact dict for the AI advisor

**Python features:**
- `min()` / `max()` / `sum() / len()` — price and discount stats
- List slicing — last 5 `recent_snapshots`
- `json.dumps()` — pretty-print for CLI validation
- Functions — `def build_deal_context(title, proposed_price):` in `application/context.py`

**Context shape:** `game`, `proposed_discounted_price`, `history` (scrape_count, date range, min/max/avg prices, recent_snapshots)

**Test:** `uv run python scripts/print_context.py "Game Title"` — prints valid JSON

**Optional (not on critical path):** exploratory charts in `analysis/notebook.ipynb` with pandas/matplotlib (histogram of discount %, heatmap by day of week)

---

## Phase 8 — Deal Advisor Website + Gemini

**Prerequisite:** Phase 7 context builder works; `GEMINI_API_KEY` in `.env`.

### Step 13: Gemini Deal Analysis
**Goal:** Send context JSON to Google Gemini and get a structured verdict

**Python features:**
- `os.getenv("GEMINI_API_KEY")` — load API key from `.env`
- `google-genai` client — call a free-tier flash model
- Prompt engineering — compare `proposed_discounted_price` to historical lows/averages only
- Parse JSON response — `{ "verdict": "good|fair|wait", "summary": "..." }`

**Files:** `application/gemini_advisor.py` — `analyze_deal(context) -> dict`

**Guardrails:** If no history for title, return a clear error without calling Gemini

**Test:** Call advisor with sample context; print verdict and summary

---

### Step 14: Simple Web UI
**Goal:** Player picks a game, enters a proposed sale price, sees if the discount is good

**Python features:**
- FastAPI (or Flask) — `GET /`, `GET /api/games`, `POST /api/advise`
- Jinja2 templates — game dropdown + price input + verdict display
- `uvicorn` — run local server

**Files:**
- `web/app.py` — routes and wiring
- `web/templates/index.html` — form + result area

**User flow:**
1. Select game from dropdown (titles from MongoDB)
2. Enter proposed discounted price
3. Backend builds context → calls Gemini → shows verdict + short explanation

**Test:** Open `http://127.0.0.1:8000`, submit one game, verify explanation references your historical data

---

## Summary Checklist

- [x] Fetch HTML with requests
- [x] Parse with BeautifulSoup
- [x] Extract core game data to dictionaries
- [ ] Extract genres, rating, review_count
- [x] Connect to MongoDB
- [x] Insert data into collection
- [ ] Scrape multiple pages
- [x] Add logging
- [x] Create scheduler
- [x] Build main.py entry point
- [ ] Collect data for 3-5 days
- [ ] Query deals by title in MongoDB
- [ ] Build deal context JSON (`application/context.py`)
- [ ] Integrate Gemini advisor (`application/gemini_advisor.py`)
- [ ] Deal advisor web UI (`web/app.py` + template)
- [ ] (Optional) Extract genres, rating, review_count
- [ ] (Optional) Exploratory charts in notebook

---

## Key File Mapping

| File | Purpose |
|------|---------|
| `application/scraper.py` | Steps 1-6, optional genre/rating extension |
| `application/db.py` | Steps 4-5, Step 11 queries |
| `application/scheduler.py` | Steps 7-8 (scheduler/logging) |
| `application/context.py` | Step 12 — deal context JSON |
| `application/gemini_advisor.py` | Step 13 — Gemini verdict |
| `main.py` | Step 9 |
| `web/app.py` | Step 14 — deal advisor site |
| `web/templates/index.html` | Step 14 — player form |
| `scripts/print_context.py` | Step 12 — CLI test for context JSON |
| `analysis/notebook.ipynb` | Optional exploratory charts only |
