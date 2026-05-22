# Steamscope Coding Plan

Simple steps to build the project, broken down until each step uses basic Python features.

**Progress:** Phases 1–3 and 5 are implemented. **Next:** Phase 4 (pagination), then extend the scraper for `genres` / `rating` / `review_count` before Phases 7–8.

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

**Still to add (before Phases 7–8):**
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

## Phase 7 — Analysis & Visualization

**Prerequisite:** `genres` and `rating` in MongoDB (Step 3 extension) for genre bar chart and rating scatter.

### Step 11: Query Data with Pandas
**Goal:** Load MongoDB data into DataFrame

**Python features:**
- `pandas.DataFrame(list(collection.find()))`
- `pd.to_datetime()` — convert date strings
- `.drop('_id', axis=1)` — remove MongoDB's internal ID

**Test:** `print(df.head())`, `print(df.shape)`

---

### Step 12: Create Charts
**Goal:** Visualize the data

**Python features:**
- `matplotlib.pyplot` — `plt.figure()`, `plt.bar()`, `plt.show()`
- `seaborn` — `sns.heatmap()`, `sns.histplot()`, `sns.scatterplot()`
- `.groupby()` — aggregate by genre
- `.value_counts()` — count occurrences
- `.corr()` — correlation between numeric columns

**Charts to build:**
1. Bar chart — top discounted genres (needs `genres`; use `.explode('genres')` then `.groupby(...)['discount_pct'].mean()`)
2. Histogram — discount % distribution (works with current schema)
3. Heatmap — discount by day of week (`df['scraped_at'].dt.day_name()`)
4. Scatter plot — rating vs discount % (needs `rating`)

---

## Phase 8 — Machine Learning

**Prerequisite:** `genres`, `rating`, `review_count` in MongoDB.

### Step 13: Prepare Data for ML
**Goal:** Transform data so a model can use it

**Python features:**
- Boolean masking: `df['is_great_deal'] = (df['discount_pct'] >= 50) & (df['rating'].isin(['Very Positive', 'Mostly Positive', 'Overwhelmingly Positive']))`
- `pd.get_dummies()` — convert categories (genre) to numbers
- `.dropna()` — remove rows with missing data
- `train_test_split` — split into training and test sets

---

### Step 14: Train Model
**Goal:** Predict if a deal is "great"

**Python features:**
- `RandomForestClassifier()` — create model
- `.fit(X_train, y_train)` — train on data
- `.predict(X_test)` — make predictions
- `accuracy_score()` — measure performance
- `confusion_matrix()` — see false positives/negatives

**Test:** Print accuracy score, verify it's reasonable (>50%)

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
- [ ] Load data with pandas
- [ ] Create 4 visualizations
- [ ] Prepare ML features
- [ ] Train RandomForest model
- [ ] Evaluate model accuracy

---

## Key File Mapping

| File | Purpose |
|------|---------|
| `application/scraper.py` | Steps 1-6, genre/rating extension |
| `application/db.py` | Steps 4-5 |
| `application/scheduler.py` | Steps 7-8 |
| `main.py` | Step 9 |
| `analysis/notebook.ipynb` | Steps 11-14 |
