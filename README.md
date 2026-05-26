# steamscope 🎮

> A Steam deals tracker that scrapes, stores, and analyzes game discounts over time.

Built as a personal learning project to practice web scraping, NoSQL databases, data analysis, and AI-assisted recommendations — all with Python.

For AI-assisted development, see [AGENTS.md](AGENTS.md) and [.github/copilot-instructions.md](.github/copilot-instructions.md).

---

## 🎯 Goal

Answer the question:

> *"Is this discount actually good for this game?"*

The final deliverable is a **simple website** where you pick a game, enter a proposed sale price, and get a plain-language verdict — powered by **historical data in MongoDB** and **Google Gemini** analyzing a compact JSON summary of that game's past deals.

---

## 🧰 Tech Stack

| Layer         | Tool                      | Purpose                                      |
|---------------|---------------------------|----------------------------------------------|
| Scraping      | `requests` + `bs4`        | Fetch and parse Steam HTML                   |
| Database      | MongoDB Atlas (free tier) | Store and persist scraped data               |
| Scheduling    | `schedule`                | Daily automated scraper runs                 |
| Analysis      | `pymongo` + Python        | Query history, build deal context JSON       |
| Web           | FastAPI + HTML templates  | Game picker, price input, verdict display    |
| AI            | Google Gemini API         | Judge if a proposed discount is good         |
| Notebook      | `jupyter` (optional)      | Exploratory charts only                      |

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
│   ├── db.py                  # MongoDB connection, insert, and queries
│   ├── scheduler.py           # Daily scheduled runs + logging
│   ├── context.py             # (planned) Build deal context JSON
│   └── gemini_advisor.py      # (planned) Call Gemini for verdict
│
├── web/                       # (planned) Deal advisor website
│   ├── app.py                 # FastAPI routes
│   ├── templates/
│   │   └── index.html         # Game select + price form + verdict
│   └── static/                # Optional minimal CSS
│
├── scripts/                   # (planned) CLI helpers
│   └── print_context.py       # Dump context JSON for one title
│
├── analysis/                  # Optional — not on critical path
│   └── notebook.ipynb         # Exploratory charts only
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

This schema is enough for Phases 7–8 (price history over time).

### Optional enrichment

These fields improve AI context but are **not required** for the deal advisor:

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
- [ ] Phase 7 — MongoDB deal context builder (`context.py`, db queries)
- [ ] Phase 8 — Deal advisor website + Gemini (`web/`, `gemini_advisor.py`)

---

## ⚙️ Setup

### Prerequisites

- Python 3.14+ (see `.python-version` and `pyproject.toml`)
- [`uv`](https://github.com/astral-sh/uv) package manager
- A free [MongoDB Atlas](https://www.mongodb.com/atlas) account
- A [Google AI Studio](https://aistudio.google.com/) API key for Gemini (Phase 8)

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

Open `.env` and fill in your values:

```
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/steamscope
SCRAPE_TIME=06:00
RUN_ON_STARTUP=false
GEMINI_API_KEY=your_key_here
```

- `SCRAPE_TIME` — 24-hour format (`HH:MM`); scheduler runs the scraper once per day at this time.
- `RUN_ON_STARTUP` — set to `true` to run one scrape immediately when starting `main.py`.
- `GEMINI_API_KEY` — required for Phase 8 (deal advisor); get one from Google AI Studio.

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

## 🤖 Deal Advisor (Phases 7–8)

### User flow

1. Pick a game from a dropdown (titles scraped into MongoDB).
2. Enter the **proposed discounted price** you are considering.
3. The backend loads that game's price history, builds a JSON context, and asks Gemini for a verdict.
4. The site shows a short answer: **good**, **fair**, or **wait**, plus a brief explanation.

### Example context JSON (sent to Gemini)

```json
{
  "game": "Elden Ring",
  "proposed_discounted_price": 39.99,
  "history": {
    "scrape_count": 12,
    "first_seen": "2025-03-20T06:00:00",
    "last_seen": "2025-03-25T06:00:00",
    "lowest_discounted_price": 34.99,
    "highest_discounted_price": 59.99,
    "average_discounted_price": 44.50,
    "average_discount_pct": 38,
    "recent_snapshots": [
      { "discounted_price": 39.99, "discount_pct": 50, "scraped_at": "2025-03-25T06:00:00" }
    ]
  }
}
```

### Planned API routes (Phase 8)

| Route          | Method | Purpose                                              |
|----------------|--------|------------------------------------------------------|
| `/`            | GET    | Render the form                                      |
| `/api/games`   | GET    | List distinct game titles from MongoDB               |
| `/api/advise`  | POST   | `{ "title": "...", "proposed_price": 29.99 }` → verdict |

---

## 📊 Optional Visualizations

Not required for the deal advisor. If you explore data in `analysis/notebook.ipynb`:

- **Histogram** — discount % distribution (works with current schema)
- **Heatmap** — average discount by day of week (`scraped_at`)
- **Bar chart** — top discounted genres (needs optional `genres` field)
- **Scatter plot** — rating vs discount % (needs optional `rating` field)

---

## 📋 Requirements

- Python 3.14+
- MongoDB Atlas account (free)
- Google Gemini API key (Phase 8)
- Internet connection for scraping, DB access, and Gemini

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Always respect a website's `robots.txt` and terms of service. Steam's public search page does not require authentication or API keys.

---

## 📄 License

MIT
