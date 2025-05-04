from fastapi import FastAPI, Form, UploadFile, File, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from fpdf import FPDF
from PyPDF2 import PdfReader
from uuid import uuid4
from starlette.middleware.sessions import SessionMiddleware
import aiofiles
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "secret"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return f"""
    <html lang='pt-BR'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
      <title>Mentor Virtual – Análise de Perfil Profissional</title>
      <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' rel='stylesheet'>
      <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; color: #111827; padding: 2rem; max-width: 960px; margin: auto; }}
        .logo {{ width: 180px; margin-bottom: 1.5rem; }}
        h1 {{ color: #1f2937; font-size: 2.5rem; margin-bottom: 1rem; }}
        label {{ font-weight: 600; display: block; margin-top: 1rem; }}
        input, textarea {{ width: 100%; padding: 0.75rem; margin-top: 0.25rem; border-radius: 8px; border: 1px solid #d1d5db; font-size: 1rem; background-color: #fff; }}
        button {{ margin-top: 2rem; padding: 0.75rem 2rem; background-color: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: background-color 0.3s; }}
        button:hover {{ background-color: #1d4ed8; }}
        form {{ background-color: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05); }}
      </style>
    </head>
    <body>
      <img src='/static/logo.png' alt='Mentor Virtual Logo' class='logo'/>
      <h1>Mentor Virtual – Análise de Perfil Profissional</h1>
      <form action='/api/analisar' method='post' enctype='multipart/form-data'>
        <label>Nome completo</label><input type='text' name='nome' required />
        <label>Email</label><input type='email' name='email' required />
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
    </body></html>"

@app.post("/resultado", response_class=HTMLResponse)
def resultado_page(nome: str = Form(...), resultado: str = Form(...)):
    return f"""
    <html lang='pt-BR'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
      <title>Resultado da Análise – Mentor Virtual</title>
      <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' rel='stylesheet'>
      <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f9fafb; color: #1f2937; padding: 2rem; max-width: 960px; margin: auto; }}
        .logo {{ width: 160px; margin-bottom: 2rem; }}
        h1 {{ font-size: 2rem; color: #111827; margin-bottom: 1.25rem; }}
        .box {{ background-color: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05); }}
        pre {{ white-space: pre-wrap; font-size: 1rem; line-height: 1.6; color: #374151; }}
        a.download {{ display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background-color: #10b981; color: #fff; border-radius: 8px; text-decoration: none; transition: background-color 0.3s; }}
        a.download:hover {{ background-color: #059669; }}
        a.voltar {{ display: inline-block; margin-top: 1.5rem; text-decoration: none; color: #2563eb; font-weight: 600; }}
      </style>
    </head>
    <body>
      <img src='/static/logo.png' alt='Mentor Virtual Logo' class='logo'/>
      <div class='box'>
        <h1>Olá, {nome} 👋</h1>
        <p>Veja abaixo sua análise personalizada:</p>
        <pre>{resultado}</pre>
        <a href='/static/analise_{nome}.pdf' class='download'>📄 Baixar Análise em PDF</a><br>
        <a href='/' class='voltar'>⬅ Voltar ao formulário</a>
      </div>
    </body>
    </html>
    """
