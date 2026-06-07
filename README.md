# SteamScope

SteamScope is a Python project that tracks Steam discounts over time and uses that history to evaluate whether a proposed sale price is actually worth it.

The project is being built as a practical learning exercise around web scraping, MongoDB, scheduled jobs, small data summaries, FastAPI, and AI-assisted recommendations.

## Current Status

The core MVP is in progress and already includes:

- Steam sale scraping with validation and retry handling.
- MongoDB Atlas persistence for historical deal snapshots.
- Daily scheduling with configurable runtime and log output.
- Historical context generation for a selected game.
- Gemini-based deal analysis from compact JSON context.
- A simple FastAPI web interface for selecting a game and submitting a proposed price.

The main remaining work is to keep collecting enough historical data, refine the web experience, and improve response formatting/error handling in the advisor flow.

## Goal

SteamScope is designed to answer a simple question:

> Is this discount actually good for this game?

The app compares a proposed discounted price with previously scraped Steam sale data and returns a concise verdict based on the game's own price history.

## Tech Stack

| Layer | Tooling | Purpose |
| --- | --- | --- |
| Scraping | `requests`, `beautifulsoup4` | Fetch and parse Steam sale pages |
| Database | MongoDB Atlas, `pymongo` | Store deal snapshots over time |
| Scheduling | `schedule` | Run the scraper daily |
| Backend | FastAPI, Jinja2 | Serve the local advisor UI and API |
| AI | Google Gemini API | Evaluate proposed prices against historical context |
| Environment | `python-dotenv`, `uv` | Manage configuration and dependencies |
| Analysis | Jupyter, pandas, matplotlib, seaborn | Optional exploratory analysis |

## Project Structure

```text
steamscope/
├── main.py                    # Scheduler entry point
├── pyproject.toml             # Project metadata and dependencies
├── uv.lock                    # Reproducible dependency lockfile
├── .python-version            # Python version used by uv
├── .env.example               # Environment variable template
├── README.md
├── PLANNING.md                # Development plan and phase notes
│
├── application/
│   ├── db.py                  # MongoDB connection and queries
│   ├── scraper.py             # Steam scraping and record parsing
│   ├── scheduler.py           # Daily scraper scheduling and logging
│   ├── context.py             # Historical deal context builder
│   ├── gemini_advisor.py      # Gemini prompt and response parsing
│   └── test_context.py        # Manual smoke test for context/advisor flow
│
├── web/
│   ├── app.py                 # FastAPI app and advisor endpoint
│   ├── templates/
│   │   └── index.html         # Game selector and price form
│   └── static/
│       └── script.js          # Browser-side form submission
│
└── logs/
    └── scraper.log            # Runtime log file, generated locally
```

## Data Model

Each document in `steamscope.deals` represents one game captured during one scrape run:

```json
{
  "title": "Elden Ring",
  "original_price": 199.99,
  "discounted_price": 99.99,
  "discount_pct": 50,
  "url": "https://store.steampowered.com/app/...",
  "scraped_at": "2026-06-06T06:00:00"
}
```

This intentionally small schema is enough to build price history, compare lows and averages, and produce a useful recommendation once enough snapshots have been collected.

## Advisor Flow

1. The scraper collects discounted games from Steam and stores them in MongoDB.
2. The web UI lists distinct game titles from the database.
3. The user selects a game and enters a proposed discounted price.
4. `application/context.py` builds a compact historical summary.
5. `application/gemini_advisor.py` sends that context to Gemini.
6. The UI displays the returned verdict JSON.

The current advisor response is intentionally direct and developer-friendly. A more polished presentation layer is a planned improvement.

## Setup

### Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv)
- MongoDB Atlas connection string
- Google Gemini API key

### Install Dependencies

```bash
uv sync
```

### Configure Environment

Create a local `.env` file from the template:

```bash
cp .env.example .env
```

Fill in the values:

```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/steamscope
SCRAPE_TIME=06:00
RUN_ON_STARTUP=false
GEMINI_API_KEY=your_key_here
```

`SCRAPE_TIME` uses 24-hour `HH:MM` format. Set `RUN_ON_STARTUP=true` if you want one scrape to run immediately when the scheduler starts.

## Running the Project

Test the MongoDB connection:

```bash
uv run python application/db.py
```

Run the scraper manually:

```bash
uv run python application/scraper.py
```

Start the daily scheduler:

```bash
uv run python main.py
```

Start the local web app:

```bash
uv run uvicorn web.app:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## API

| Route | Method | Description |
| --- | --- | --- |
| `/` | `GET` | Renders the advisor form with game titles from MongoDB |
| `/api/advise` | `POST` | Analyzes a proposed price for a selected game |

Example request:

```json
{
  "title": "Elden Ring",
  "proposed_price": 39.99
}
```

Example response shape:

```json
{
  "verdict": "good",
  "summary": "The proposed price is below the recent average but not the historical low.",
  "confidence": 80,
  "key_insights": [
    "Recent prices are higher than the proposed price",
    "Historical low is still lower than this offer"
  ]
}
```

## Roadmap

- [x] Project setup with `uv`
- [x] Steam scraper with validation
- [x] MongoDB integration
- [x] Multi-page scraping
- [x] Scheduler and logging
- [x] Historical deal context builder
- [x] Gemini advisor integration
- [x] Basic FastAPI web interface
- [ ] Longer data collection period for stronger recommendations
- [ ] Better UI formatting for advisor results
- [ ] More graceful frontend/API error handling
- [ ] Optional exploratory notebooks and visualizations

## Notes

- `.env` should never be committed.
- `logs/scraper.log` is generated at runtime.
- The advisor is only as useful as the available historical data. Running the scraper over multiple days improves the quality of recommendations.
- This project is for educational purposes. Respect Steam's terms of service and avoid aggressive scraping.

## License

MIT
