from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator, Field
from fastapi.templating import Jinja2Templates
import logging
import json

from application.db import list_games_titles
from application.redis_client import create_redis_client, check_rate_limit, build_advice_cache_key
from application.gemini_advisor import analyze_deal
from application.context import build_deal_context

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

    allowed = check_rate_limit(redis_client, rate_limit_key, limit=5, period=45)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    cache_key = build_advice_cache_key(
        advice_request.title,
        advice_request.proposed_price,
    )

    cached = redis_client.get(cache_key)
    
    if cached:
        return JSONResponse(content=json.loads(cached))

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
    except ValueError:
        logger.exception("Advisor service is not configured correctly.")
        raise HTTPException(status_code=503, detail="Advisor service unavailable")
        
    except Exception:
        logger.exception("Advisor service error")
        raise HTTPException(status_code=502, detail="Advisor service failed")

    redis_client.setex(
        cache_key,
        300,  # 5 minutes
        json.dumps(analysis),
    )

    return JSONResponse(content=analysis)
