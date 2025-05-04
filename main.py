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

os.makedirs("static", exist_ok=True)
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

@app.get("/login")
def login():
    return HTMLResponse("""
    <html><body>
    <h2>Login</h2>
    <form method='post' action='/login'>
        <label>Email</label><input type='email' name='email' required />
        <button type='submit'>Entrar</button>
    </form>
    </body></html>""")

@app.post("/login")
def login_post(request: Request, email: str = Form(...)):
    request.session['user'] = email
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.post("/api/analisar", response_class=HTMLResponse)
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
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    def limitar(texto, limite):
        return texto[:limite] if texto else ""

    texto_pdf = ""
    if curriculo:
        try:
            contents = await curriculo.read()
            nome_temp = f"temp_{uuid4()}.pdf"
            with open(nome_temp, "wb") as f:
                f.write(contents)
            reader = PdfReader(nome_temp)
            texto_pdf = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception:
            texto_pdf = "Erro ao ler o currículo PDF."

    linkedin_conteudo = limitar(linkedin_conteudo, 500)
    preferencias = limitar(preferencias, 300)
    texto_pdf = limitar(texto_pdf, 1000)

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
    Currículo extraído: {texto_pdf}

    A análise deve incluir: 
    1. Pontos fortes identificados
    2. Áreas de melhoria
    3. Sugestões de desenvolvimento
    4. Feedback empático final
    """

    try:
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}]
        )
        resposta = completion.choices[0].message.content if completion.choices else "Erro: resposta vazia da IA."
    except Exception as e:
        resposta = f"Erro ao processar a análise com a IA: {e}"

    async with aiofiles.open(f"static/historico_{user}.txt", "a") as f:
        await f.write(f"\n===== {nome} =====\n{resposta}\n")

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
