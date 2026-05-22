# steamscope 🎮

> A Steam deals tracker that scrapes, stores, and analyzes game discounts over time.

Built as a personal learning project to practice web scraping, NoSQL databases, data analysis, and machine learning — all with Python.

For AI-assisted development, see [AGENTS.md](AGENTS.md) and [.github/copilot-instructions.md](.github/copilot-instructions.md).

---

## 🎯 Goal

Answer the question:

> *"What kinds of games go on sale the most, how deep are the discounts, and is there a pattern in when deals happen?"*

The final deliverable is a Jupyter notebook with charts and a simple ML model that predicts whether a game is a **"great deal"** based on its features.

---

## 🧰 Tech Stack

| Layer         | Tool                      | Purpose                             |
|---------------|---------------------------|-------------------------------------|
| Scraping      | `requests` + `bs4`        | Fetch and parse Steam HTML          |
| Database      | MongoDB Atlas (free tier) | Store and persist scraped data      |
| Scheduling    | `schedule`                | Daily automated scraper runs        |
| Analysis      | `pandas`                  | Query and manipulate collected data |
| Visualization | `matplotlib` + `seaborn`  | Charts and plots                    |
| ML            | `scikit-learn`            | Deal quality classifier             |
| Notebook      | `jupyter`                 | Interactive analysis environment    |

---

## 📁 Project Structure

```
steamscope/
│
├── main.py                    # Entry point — runs the scheduler
├── pyproject.toml             # Project metadata and dependencies
├── uv.lock                    # Lockfile — guarantees reproducible installs
├── .python-version            # Pinned Python version for uv
├── .env                       # Secrets — NEVER commit this
├── .env.example               # Template for .env — safe to commit
├── AGENTS.md                  # Short agent status and pointers
├── .gitignore
├── LICENSE
├── README.md
│
├── application/               # Core source package
│   ├── scraper.py             # Fetches and parses Steam deals page
│   ├── db.py                  # MongoDB connection and insert/query logic
│   └── scheduler.py           # Daily scheduled runs + logging
│
├── analysis/                  # Data analysis and ML
│   ├── notebook.ipynb         # Main analysis notebook (charts + model)
│   └── model.py               # Extracted ML logic (optional standalone)
│
└── logs/                      # Auto-generated at runtime, not committed
    └── scraper.log            # One line per run: timestamp + result
```

---

## 📦 Data Schema

### Current (stored today)

Each document in `steamscope.deals` represents one game from one scrape run:

```json
{
  "title":            "Elden Ring",
  "original_price":   199.99,
  "discounted_price": 99.99,
  "discount_pct":     50,
  "url":              "https://store.steampowered.com/app/...",
  "scraped_at":       "2025-03-25T14:00:00"
}
```

### Planned (before analysis / ML)

Add these fields in a future scraper step (required for genre/rating charts and the ML model):

```json
{
  "genres":       ["RPG", "Action"],
  "rating":       "Very Positive",
  "review_count": 120400
}
```

---

## 🗺️ Roadmap

- [x] Phase 1 — Project setup and folder structure
- [x] Phase 2 — Steam scraper (single page, validation, MongoDB insert)
- [x] Phase 3 — MongoDB integration (`db.py`)
- [ ] Phase 4 — Pagination (scrape 4–5 pages per run, ~100–125 games)
- [x] Phase 5 — Scheduler + logging (`scheduler.py` + `main.py`)
- [ ] Phase 6 — Data collection period *(let it run for 3–5 days)*
- [ ] Phase 7 — Visualization notebook (4+ charts)
- [ ] Phase 8 — ML model: "great deal" classifier

---

## ⚙️ Setup

### Prerequisites

- Python 3.14+ (see `.python-version` and `pyproject.toml`)
- [`uv`](https://github.com/astral-sh/uv) package manager
- A free [MongoDB Atlas](https://www.mongodb.com/atlas) account

### 1. Clone the repository

```bash
git clone https://github.com/your-username/steamscope.git
cd steamscope
```

### 2. Install uv (if you don't have it)

```bash
pip install uv
```

### 3. Install all dependencies

```bash
uv sync
```

This reads `uv.lock` and installs the exact same versions used in development — no manual version management needed.

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your MongoDB Atlas connection string:

```
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/steamscope
SCRAPE_TIME=06:00
RUN_ON_STARTUP=false
```

- `SCRAPE_TIME` — 24-hour format (`HH:MM`); scheduler runs the scraper once per day at this time.
- `RUN_ON_STARTUP` — set to `true` to run one scrape immediately when starting `main.py`.

### 5. Test MongoDB connection (optional)

```bash
uv run python application/db.py
```

### 6. Run the scraper manually (test)

```bash
uv run python application/scraper.py
```

### 7. Start the scheduler

```bash
uv run python main.py
```

The scheduler runs the scraper once per day at `SCRAPE_TIME` and logs each run to `logs/scraper.log`.

---

## 🗄️ MongoDB Atlas — Free Tier Setup

This project uses MongoDB Atlas M0 — free forever, no credit card required.

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster → choose **M0 Free**
4. Create a database user (username + password)
5. Whitelist your IP address (or use `0.0.0.0/0` for development)
6. Click **Connect** → **Drivers** → copy the connection string
7. Paste it into your `.env` file as `MONGO_URI`

---

## 📊 Planned Visualizations

Requires `genres` and `rating` in the database (see planned schema above).

- **Bar chart** — top discounted genres
- **Histogram** — discount % distribution across all games
- **Heatmap** — average discount by day of week scraped
- **Scatter plot** — rating vs. discount % correlation

Charts that work with the **current** schema: histogram (discount %), heatmap (day of week from `scraped_at`).

---

## 🤖 ML Model

| | |
|---|---|
| **Target** | `is_great_deal` — `True` if `discount_pct >= 50` AND `rating` is in `["Very Positive", "Mostly Positive", "Overwhelmingly Positive"]` |
| **Features** | genre (encoded), original price, review count, day of week |
| **Model** | `RandomForestClassifier` |
| **Evaluation** | Accuracy score + confusion matrix |

Blocked until `genres`, `rating`, and `review_count` are scraped and stored.

---

## 📋 Requirements

- Python 3.14+
- MongoDB Atlas account (free)
- Internet connection for scraping and DB access

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Always respect a website's `robots.txt` and terms of service. Steam's public search page does not require authentication or API keys.

---

## 📄 License

MIT
