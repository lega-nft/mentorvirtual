from fastapi import FastAPI, Form, UploadFile, File, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from fpdf import FPDF
from PyPDF2 import PdfReader
from uuid import uuid4
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
import os
from authlib.integrations.starlette_client import OAuth, OAuthError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

config = Config('.env')
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={"scope": "openid email profile"}
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "secret"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/login")
def login(request: Request):
    redirect_uri = request.url_for('auth')
    return oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        request.session['user'] = user["email"]
        return RedirectResponse("/")
    except OAuthError:
        return HTMLResponse("<h1>Erro na autenticação via Google.</h1>")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")
    return f"""
    <html lang=\"pt-BR\">
    <head>
      <meta charset=\"UTF-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>
      <title>Mentor Virtual</title>
      <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f9fafb; color: #333; padding: 2rem; max-width: 800px; margin: auto; }}
        h1 {{ color: #1d4ed8; font-size: 2rem; }}
        label {{ font-weight: 600; display: block; margin-top: 1rem; }}
        input, textarea {{ width: 100%; padding: 0.6rem; margin-top: 0.3rem; border-radius: 6px; border: 1px solid #ccc; font-size: 1rem; }}
        input[type=\"file\"] {{ border: none; }}
        button {{ margin-top: 2rem; padding: 0.75rem 2rem; background-color: #1d4ed8; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }}
        button:hover {{ background-color: #2563eb; }}
      </style>
    </head>
    <body>
      <h1>Mentor Virtual – Análise de Perfil Profissional</h1>
      <form action=\"/api/analisar\" method=\"post\" enctype=\"multipart/form-data\">
        <label>Nome completo</label><input type=\"text\" name=\"nome\" required />
        <label>Cargo atual</label><input type=\"text\" name=\"cargo\" required />
        <label>Experiência profissional</label><textarea name=\"experiencia\" rows=\"4\" required></textarea>
        <label>Habilidades técnicas</label><textarea name=\"habilidades\" rows=\"3\" required></textarea>
        <label>Soft Skills</label><textarea name=\"soft_skills\" rows=\"3\" required></textarea>
        <label>Objetivo profissional</label><input type=\"text\" name=\"objetivo\" required />
        <label>Desafios enfrentados</label><textarea name=\"desafios\" rows=\"3\"></textarea>
        <label>LinkedIn</label><input type=\"url\" name=\"linkedin\" />
        <label>Conteúdo do LinkedIn (copie e cole)</label><textarea name=\"linkedin_conteudo\" rows=\"5\"></textarea>
        <label>Preferências de carreira</label><textarea name=\"preferencias\" rows=\"3\"></textarea>
        <label>Ou envie seu currículo (PDF)</label><input type=\"file\" name=\"curriculo\" accept=\"application/pdf\" />
        <button type=\"submit\">🔍 Analisar Perfil</button>
      </form>
    </body></html>"

@app.get("/historico", response_class=HTMLResponse)
def historico(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")
    try:
        with open(f"static/historico_{user}.txt") as f:
            linhas = f.read().replace("\n", "<br>")
    except:
        linhas = "Nenhum histórico encontrado."
    return f"<html><body><h2>Histórico de {user}</h2><p>{linhas}</p><a href='/'>⬅ Voltar</a></body></html>"

# Permissões podem ser controladas com base no domínio do e-mail ou regras por usuário dentro de um banco futuramente
