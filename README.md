# SteamScope

SteamScope tracks Steam discounts over time and uses that history to evaluate whether a proposed sale price is actually worth it.

The project is a practical backend learning exercise around web scraping, MongoDB, FastAPI, Redis, external AI APIs, automated tests, and CI.

## Goal

SteamScope answers one question:

> Is this discount actually good for this game?

The app compares a proposed discounted price with previously scraped Steam sale data and returns a concise recommendation based on the game's own historical prices.

## Current Status

The current MVP includes:

- Steam sale scraping with validation and retry handling.
- MongoDB Atlas persistence for historical deal snapshots.
- Daily scheduling with configurable runtime and log output.
- Historical context generation for a selected game.
- Gemini-based deal analysis from compact JSON context.
- FastAPI web interface and JSON API.
- Pydantic request validation for the advisor endpoint.
- Redis rate limiting by client IP.
- Redis response caching for repeated advisor requests.
- Unit tests for validation, cache keys, and rate limit behavior.
- GitHub Actions CI running the test suite automatically.

## Tech Stack

| Layer | Tooling | Purpose |
| --- | --- | --- |
| Scraping | `requests`, `beautifulsoup4` | Fetch and parse Steam sale pages |
| Database | MongoDB Atlas, `pymongo` | Store historical deal snapshots |
| Cache / rate limit | Redis, `redis-py` | Reduce repeated work and limit abuse |
| Scheduling | `schedule` | Run the scraper daily |
| Backend | FastAPI, Pydantic, Jinja2 | Serve the web UI and API |
| AI | Google Gemini API | Evaluate proposed prices against historical context |
| Tests | `pytest` | Validate core behavior without external services |
| CI | GitHub Actions | Run tests in a clean environment on push/PR |
| Environment | `python-dotenv`, `uv` | Manage config and dependencies |

## Project Structure

```text
steamscope/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions test workflow
├── application/
│   ├── context.py                 # Historical deal context builder
│   ├── context_smoke_test.py      # Manual smoke test for advisor flow
│   ├── db.py                      # MongoDB connection and queries
│   ├── gemini_advisor.py          # Gemini prompt and response parsing
│   ├── redis_client.py            # Redis client, rate limit, cache key helpers
│   ├── scheduler.py               # Daily scraper scheduling and logging
│   └── scraper.py                 # Steam scraping and record parsing
├── tests/
│   ├── test_api_validation.py     # Pydantic request validation tests
│   └── test_redis_client.py       # Cache key and rate limit tests
├── web/
│   ├── app.py                     # FastAPI app and advisor endpoint
│   ├── static/
│   │   └── script.js              # Browser-side form submission
│   └── templates/
│       └── index.html             # Advisor UI
├── main.py                        # Scheduler entry point
├── pyproject.toml                 # Project metadata, deps, pytest config
├── uv.lock                        # Reproducible dependency lockfile
├── .env.example                   # Environment variable template
├── README.md
└── PLANNING.md
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

This intentionally small schema is enough to build price history, compare lows and averages, and produce useful recommendations once enough snapshots have been collected.

## Advisor Flow

```text
Browser
  -> FastAPI request validation
  -> Redis rate limit by IP
  -> Redis cache lookup
  -> MongoDB historical data query
  -> Gemini deal analysis
  -> Redis cache write with TTL
  -> JSON response
```

Detailed flow:

1. The scraper collects discounted games from Steam and stores them in MongoDB.
2. The web UI lists distinct game titles from the database.
3. The user selects a game and enters a proposed discounted price.
4. FastAPI/Pydantic validates the request body.
5. Redis counts requests per IP and blocks excess calls with `429 Too Many Requests`.
6. Redis checks whether the same `title + proposed_price` analysis is already cached.
7. On cache miss, `application/context.py` builds a compact historical summary.
8. `application/gemini_advisor.py` sends that context to Gemini.
9. The response is cached for a short TTL and returned as JSON.

## Setup

### Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv)
- MongoDB Atlas connection string
- Google Gemini API key
- Redis, local or hosted

### Install Dependencies

```bash
uv sync --dev
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
REDIS_URL=redis://localhost:6379/0
```

`SCRAPE_TIME` uses 24-hour `HH:MM` format. Set `RUN_ON_STARTUP=true` if you want one scrape to run immediately when the scheduler starts.

### Run Redis Locally

Using Docker:

```bash
docker run --name steamscope-redis -p 6379:6379 redis:7-alpine
```

If the container already exists:

```bash
docker start steamscope-redis
```

Check Redis:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

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

## Security And Reliability Notes

- Frontend validation improves UX; backend validation is the real security boundary.
- `AdviceRequest` rejects empty titles, negative prices, overly large prices, and unexpected fields.
- Internal errors are logged server-side and returned as generic API errors.
- Redis rate limiting reduces accidental spam and basic abuse of the Gemini-backed endpoint.
- Redis caching reduces repeated calls to MongoDB and Gemini for identical advisor requests.
- The UI uses text rendering for API output, not HTML injection, which lowers XSS risk.
- `.env` must stay local and should never be committed.

## Tests

Run the test suite:

```bash
uv run python -m pytest
```

The current tests cover:

- Cache key normalization.
- Price normalization for cache keys.
- Rate limit blocking after the configured limit.
- Redis expiration being set once per fixed window.
- API request validation with Pydantic.

Testing model:

```text
Arrange -> prepare data
Act -> run behavior
Assert -> verify expectation
```

For external dependencies, the tests use small fakes instead of real Redis, MongoDB, or Gemini. This keeps unit tests fast, deterministic, and cheap.

## CI

GitHub Actions runs the tests automatically on push and pull request.

Workflow file:

```text
.github/workflows/ci.yml
```

Mental model:

```text
GitHub receives a push
-> creates a clean Ubuntu machine
-> checks out the repository
-> installs Python and uv
-> installs dependencies
-> runs pytest
-> marks the commit green or red
```

CI is not deployment. CI answers:

```text
Does this code still pass the automated checks in a clean environment?
```

CD would answer:

```text
Can this checked code be automatically deployed?
```

This project currently uses CI only.

## Roadmap

- [x] Project setup with `uv`
- [x] Steam scraper with validation
- [x] MongoDB integration
- [x] Multi-page scraping
- [x] Scheduler and logging
- [x] Historical deal context builder
- [x] Gemini advisor integration
- [x] Basic FastAPI web interface
- [x] API request validation
- [x] Redis rate limiting
- [x] Redis response caching
- [x] Unit tests with `pytest`
- [x] GitHub Actions CI
- [ ] More polished advisor response UI
- [ ] More graceful frontend loading/error states
- [ ] Idempotent scraper writes with unique indexes/upserts
- [ ] Optional deployment with production secrets management

## Notes

- `.env` should never be committed.
- `logs/scraper.log` is generated at runtime.
- The advisor is only as useful as the available historical data. Running the scraper over multiple days improves recommendation quality.
- This project is for educational purposes. Respect Steam's terms of service and avoid aggressive scraping.

## License

MIT
