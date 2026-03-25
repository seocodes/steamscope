# steamscope 🎮

> A Steam deals tracker that scrapes, stores, and analyzes game discounts over time.

Built as a personal learning project to practice web scraping, NoSQL databases, data analysis, and machine learning — all with Python.

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
| Scheduling    | `schedule`                | Automate scraper runs every 6–12h   |
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
├── .gitignore
├── LICENSE
├── README.md
│
├── application/               # Core source package
│   ├── scraper.py             # Fetches and parses Steam deals page
│   ├── db.py                  # MongoDB connection and insert/query logic
│   └── scheduler.py           # Automated run logic (calls scraper every 6–12h)
│
├── analysis/                  # Data analysis and ML
│   ├── notebook.ipynb         # Main analysis notebook (charts + model)
│   └── model.py               # Extracted ML logic (optional standalone)
│
├── logs/                      # Auto-generated at runtime, not committed
│   └── scraper.log            # One line per run: timestamp + result
│
└── tests/
    ├── test_scraper.py        # Unit tests for scraper logic
    └── test_db.py             # Unit tests for DB connection and inserts
```

---

## 📦 Data Schema

Each document stored in MongoDB represents one game scraped in one run:

```json
{
  "title":            "Elden Ring",
  "original_price":   199.99,
  "discounted_price": 99.99,
  "discount_pct":     50,
  "genres":           ["RPG", "Action"],
  "rating":           "Very Positive",
  "review_count":     120400,
  "url":              "https://store.steampowered.com/app/...",
  "scraped_at":       "2025-03-25T14:00:00"
}
```

---

## 🗺️ Roadmap

- [x] Phase 1 — Project setup and folder structure
- [ ] Phase 2 — Steam scraper (single page, console output only)
- [ ] Phase 3 — MongoDB integration (`db.py`)
- [ ] Phase 4 — Pagination (scrape 4–5 pages per run, ~100–125 games)
- [ ] Phase 5 — Scheduler + logging (`scheduler.py` + `main.py`)
- [ ] Phase 6 — Data collection period *(let it run for 3–5 days)*
- [ ] Phase 7 — Visualization notebook (4+ charts)
- [ ] Phase 8 — ML model: "great deal" classifier

---

## ⚙️ Setup

### Prerequisites

- Python 3.11+
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
```

### 5. Run the scraper manually (test)

```bash
uv run python application/scraper.py
```

### 6. Start the scheduler

```bash
uv run python main.py
```

The scheduler will run the scraper automatically every 6 hours and log each run to `logs/scraper.log`.

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

- **Bar chart** — top discounted genres
- **Histogram** — discount % distribution across all games
- **Heatmap** — average discount by day of week scraped
- **Scatter plot** — rating vs. discount % correlation

---

## 🤖 ML Model

| | |
|---|---|
| **Target** | `is_great_deal` — `True` if `discount_pct >= 50` AND rating is "Mostly Positive" or better |
| **Features** | genre (encoded), original price, review count, day of week |
| **Model** | `RandomForestClassifier` |
| **Evaluation** | Accuracy score + confusion matrix |

---

## 📋 Requirements

- Python 3.11+
- MongoDB Atlas account (free)
- Internet connection for scraping and DB access

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Always respect a website's `robots.txt` and terms of service. Steam's public search page does not require authentication or API keys.

---

## 📄 License

MIT