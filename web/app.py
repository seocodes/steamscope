import json
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, field_validator
from redis.exceptions import RedisError

from application.context import build_deal_context
from application.db import list_games_titles
from application.gemini_advisor import analyze_deal
from application.redis_client import build_advice_cache_key, check_rate_limit, create_redis_client


class AdviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(min_length=1, max_length=200)
    proposed_price: float = Field(ge=0, le=10000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be empty")
        return value

ADVISOR_CACHE_TTL_SECONDS = int(os.getenv("ADVISOR_CACHE_TTL_SECONDS", 300))
RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", 45))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 5))

redis_client = create_redis_client()

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="web/templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/")
async def home(request: Request):
    try:
        games = list_games_titles()
        return templates.TemplateResponse(
            name="index.html", request=request, context={"games": games}
        )
    except Exception:
        # Log interno detalhado com stack trace
        logger.exception("Failed to render home page")
        # Resposta de erro genérica para o cliente
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


@app.post("/api/advise")
def advise_game(request: Request, advice_request: AdviceRequest):
    # Se tiver uma rotating proxy eh F pa nois
    client_ip = request.client.host
    rate_limit_key = f"rate_limit:advise:{client_ip}"

    try:
        allowed = check_rate_limit(
            redis_client,
            rate_limit_key,
            RATE_LIMIT_MAX_REQUESTS,
            RATE_LIMIT_PERIOD_SECONDS,
        )
    except RedisError:
        logger.warning("Redis unavailable, skipping rate limit")  # fail-open
        allowed = True

    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # default status is MISS, will be updated if cache is hit or bypassed
    cache_status = "MISS"
    cache_key = build_advice_cache_key(
        advice_request.title,
        advice_request.proposed_price,
    )

    try:
        cached = redis_client.get(cache_key)
    except RedisError:
        logger.warning("Redis unavailable, skipping cache")  # fail-open
        cached = None
        cache_status = "BYPASS"

    if cached:
        try:
            return JSONResponse(
                content=json.loads(cached),
                headers={"X-Cache": "HIT"},
            )
        except json.JSONDecodeError:
            logger.warning("Cache data is invalid, bypassing")
            cache_status = "BYPASS"

    try:
        context = build_deal_context(
            advice_request.title,
            advice_request.proposed_price,
        )
    except ValueError as exc:
        logger.exception("Invalid input.")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        analysis = analyze_deal(context)
    except ValueError as exc:
        logger.exception("Advisor service is not configured correctly.")
        raise HTTPException(status_code=503, detail="Advisor service unavailable") from exc

    except Exception as exc:
        logger.exception("Advisor service error")
        raise HTTPException(status_code=502, detail="Advisor service failed") from exc

    try:
        redis_client.setex(
            cache_key,
            ADVISOR_CACHE_TTL_SECONDS,  # 5 minutes by default
            json.dumps(analysis),
        )
    except RedisError:
        logger.warning("Redis unavailable, skipping cache write")
        cache_status = "BYPASS"

    return JSONResponse(
        content=analysis,
        headers={"X-Cache": cache_status},
    )
