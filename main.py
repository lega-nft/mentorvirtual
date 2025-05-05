
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    return RedirectResponse("/menu")

@app.get("/client/resultado")
def client_resultado(request: Request):
    return templates.TemplateResponse("client/result.html", {"request": request, "resultado": "Exemplo de perfil gerado pela IA."})
