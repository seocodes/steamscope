from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator, Field
from fastapi.templating import Jinja2Templates
import logging

from application.db import list_games_titles
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
def advise_game(advice_request: AdviceRequest):
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
    

    return JSONResponse(content=analysis)
