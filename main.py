import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from app.api.api import api_router
from app.frontend.views import frontend_router
from app.core.database import engine, Base
from app.core.config import settings, JINJA2_FILTERS

# Cria as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")
templates.env.auto_reload = settings.TEMPLATES_AUTO_RELOAD

for name, function in JINJA2_FILTERS.items():
    templates.env.filters[name] = function

templates.env.globals.update({
    'settings': settings,
    'tojson': json.dumps
})

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(frontend_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, workers=1, reload=True, log_level="info")
