
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

from application.db import list_games_titles
from application.gemini_advisor import analyze_deal


class game(BaseModel):
    title: str
    price: float
    
templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
async def home(request: Request):
    games = list_games_titles()
    # ERRO AQUI
    print(games)
    return templates.TemplateResponse(
        name="index.html", request=request, context={"games": games})

# @app.post("/api/analyze/")
# def analyze_game(game: game):
    