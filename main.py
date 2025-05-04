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
      <title>Mentor Virtual - Análise de Perfil Profissional</title>
      <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' rel='stylesheet'>
      <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; color: #111827; padding: 2rem; max-width: 960px; margin: auto; }}
        h1 {{ color: #1f2937; font-size: 2.5rem; margin-bottom: 1rem; }}
        label {{ font-weight: 600; display: block; margin-top: 1rem; }}
        input, textarea {{ width: 100%; padding: 0.75rem; margin-top: 0.25rem; border-radius: 8px; border: 1px solid #d1d5db; font-size: 1rem; background-color: #fff; }}
        button {{ margin-top: 2rem; padding: 0.75rem 2rem; background-color: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: background-color 0.3s; }}
        button:hover {{ background-color: #1d4ed8; }}
        form {{ background-color: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05); }}
      </style>
    </head>
    <body>
      <h1>Mentor Virtual - Análise de Perfil Profissional</h1>
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
    </body></html>"""

@app.post("/resultado", response_class=HTMLResponse)
def resultado_page(nome: str = Form(...), resultado: str = Form(...)):
    return f"""
    <html lang='pt-BR'>
    <head>
      <meta charset='UTF-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
      <title>Resultado da Análise - Mentor Virtual</title>
      <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap' rel='stylesheet'>
      <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f9fafb; color: #1f2937; padding: 2rem; max-width: 960px; margin: auto; }}
        h1 {{ font-size: 2rem; color: #111827; margin-bottom: 1.25rem; }}
        .box {{ background-color: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05); }}
        pre {{ white-space: pre-wrap; font-size: 1rem; line-height: 1.6; color: #374151; background-color: #f3f4f6; padding: 1rem; border-radius: 8px; }}
        a.download {{ display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background-color: #10b981; color: #fff; border-radius: 8px; text-decoration: none; transition: background-color 0.3s; }}
        a.download:hover {{ background-color: #059669; }}
        a.voltar {{ display: inline-block; margin-top: 1.5rem; text-decoration: none; color: #2563eb; font-weight: 600; }}
      </style>
    </head>
    <body>
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

@app.post("/api/analisar")
async def analisar(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
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
    conteudo_cv = ""

    if curriculo and curriculo.filename.endswith(".pdf"):
        reader = PdfReader(curriculo.file)
        conteudo_cv = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    prompt = f"""
    Realize uma análise profissional com base nas seguintes informações do usuário:

    Nome: {nome}
    Cargo atual: {cargo}
    Experiência: {experiencia}
    Habilidades Técnicas: {habilidades}
    Soft Skills: {soft_skills}
    Objetivo Profissional: {objetivo}
    Desafios: {desafios}
    LinkedIn: {linkedin}
    Conteúdo do LinkedIn: {linkedin_conteudo}
    Preferências de Carreira: {preferencias}
    Currículo: {conteudo_cv}

    Gere:
    1. Pontos fortes
    2. Áreas de melhoria
    3. Sugestões de desenvolvimento
    4. Um feedback final encorajador
    """

    resposta = await client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    resultado = resposta.choices[0].message.content

    nome_arquivo = f"analise_{nome.replace(' ', '_')}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for linha in resultado.split("\n"):
        pdf.multi_cell(0, 10, linha)

    os.makedirs("static", exist_ok=True)
    caminho_arquivo = os.path.join("static", nome_arquivo)
    pdf.output(caminho_arquivo)

    return RedirectResponse(url="/resultado", status_code=303).include_form_data({
        "nome": nome,
        "resultado": resultado
    })
