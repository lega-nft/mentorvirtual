from fastapi import FastAPI, Form, UploadFile, File, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from fpdf import FPDF
from PyPDF2 import PdfReader
from uuid import uuid4
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
import os
from authlib.integrations.starlette_client import OAuth, OAuthError
import aiofiles

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    <html lang='pt-BR'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
      <title>Mentor Virtual</title>
      <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f9fafb; color: #333; padding: 2rem; max-width: 800px; margin: auto; }}
        h1 {{ color: #1d4ed8; font-size: 2rem; }}
        label {{ font-weight: 600; display: block; margin-top: 1rem; }}
        input, textarea {{ width: 100%; padding: 0.6rem; margin-top: 0.3rem; border-radius: 6px; border: 1px solid #ccc; font-size: 1rem; }}
        input[type='file'] {{ border: none; }}
        button {{ margin-top: 2rem; padding: 0.75rem 2rem; background-color: #1d4ed8; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }}
        button:hover {{ background-color: #2563eb; }}
      </style>
    </head>
    <body>
      <h1>Mentor Virtual – Análise de Perfil Profissional</h1>
      <form action='/api/analisar' method='post' enctype='multipart/form-data'>
        <label>Nome completo</label><input type='text' name='nome' required />
        <label>Cargo atual</label><input type='text' name='cargo' required />
        <label>Experiência profissional</label><textarea name='experiencia' rows='4' required></textarea>
        <label>Habilidades técnicas</label><textarea name='habilidades' rows='3' required></textarea>
        <label>Soft Skills</label><textarea name='soft_skills' rows='3' required></textarea>
        <label>Objetivo profissional</label><input type='text' name='objetivo' required />
        <label>Desafios enfrentados</label><textarea name='desafios' rows='3'></textarea>
        <label>LinkedIn</label><input type='url' name='linkedin' />
        <label>Conteúdo do LinkedIn (copie e cole)</label><textarea name='linkedin_conteudo' rows='5'></textarea>
        <label>Preferências de carreira</label><textarea name='preferencias' rows='3'></textarea>
        <label>Ou envie seu currículo (PDF)</label><input type='file' name='curriculo' accept='application/pdf' />
        <button type='submit'>🔍 Analisar Perfil</button>
      </form>
    </body></html>"""

@app.post("/api/analisar", response_class=HTMLResponse)
async def analisar(
    request: Request,
    nome: str = Form(...),
    cargo: str = Form(...),
    experiencia: str = Form(...),
    habilidades: str = Form(...),
    soft_skills: str = Form(...),
    objetivo: str = Form(...),
    desafios: str = Form(""),
    linkedin: str = Form(""),
    linkedin_conteudo: str = Form(""),
    preferencias: str = Form(""),
    curriculo: UploadFile = File(None)
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    texto_pdf = ""
    if curriculo:
        try:
            contents = await curriculo.read()
            with open(f"temp_{uuid4()}.pdf", "wb") as f:
                f.write(contents)
            reader = PdfReader(f.name)
            texto_pdf = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception:
            texto_pdf = "Erro ao ler o currículo PDF."

    prompt = f"""
    Considere o seguinte perfil profissional e gere uma análise com sugestões práticas de desenvolvimento:

    Nome: {nome}
    Cargo atual: {cargo}
    Experiência: {experiencia}
    Habilidades técnicas: {habilidades}
    Soft skills: {soft_skills}
    Objetivo profissional: {objetivo}
    Desafios enfrentados: {desafios}
    LinkedIn: {linkedin}
    Conteúdo do LinkedIn: {linkedin_conteudo}
    Preferências: {preferencias}
    Currículo extraído: {texto_pdf[:1000]}

    A análise deve incluir: 
    1. Pontos fortes identificados
    2. Áreas de melhoria
    3. Sugestões de desenvolvimento
    4. Feedback empático final
    """

    try:
completion = await client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": prompt}]
)
resposta = completion.choices[0].message.content if completion.choices else "Erro: resposta vazia da IA."

    # salvar histórico
    async with aiofiles.open(f"static/historico_{user}.txt", "a") as f:
        await f.write(f"\n===== {nome} =====\n{resposta}\n")

    # gerar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for linha in resposta.split("\n"):
        pdf.multi_cell(0, 10, linha)
    pdf_path = f"static/{uuid4()}.pdf"
    pdf.output(pdf_path)

    return f"""
    <html><body>
    <h2>Olá, {nome} 👋</h2>
    <p>Veja abaixo sua análise personalizada:</p>
    <pre>{resposta}</pre>
    <a href='/{pdf_path}' download>📄 Baixar Análise em PDF</a><br><br>
    <a href='/'>⬅ Voltar ao formulário</a>
    </body></html>"""

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
