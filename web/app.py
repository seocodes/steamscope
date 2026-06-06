
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

from application.db import list_games_titles
from application.gemini_advisor import analyze_deal
from application.context import build_deal_context

class AdviceRequest(BaseModel):
    title: str
    proposed_price: float
    
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
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/advise")
def advise_game(advice_request: AdviceRequest):
    try:
        context = build_deal_context(
            advice_request.title,
            advice_request.proposed_price,
        )
        analysis = analyze_deal(context)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JSONResponse(content=analysis)
