from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import os
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=".")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Armazena resultados temporários em memória
results_store = {}

# ----------------- Rotas principais -----------------

@app.get("/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/login")
def process_login(request: Request, email: str = Form(...)):
    return RedirectResponse(url="/menu", status_code=303)

@app.get("/menu")
def menu(request: Request):
    return templates.TemplateResponse("menu/menu.html", {"request": request})

# ----------------- Mentor - Análise de Perfil -----------------

@app.get("/mentor")
def mentor_form(request: Request):
    return templates.TemplateResponse("mentor/formulario.html", {"request": request})

@app.post("/api/mentor")
async def analisar_perfil(request: Request, nome: str = Form(...), objetivo: str = Form(...), experiencia: str = Form(...), habilidades: str = Form(...)):
    prompt = f"""
Analise o seguinte perfil profissional com base nas informações fornecidas:
Nome: {nome}
Objetivo profissional: {objetivo}
Experiência: {experiencia}
Habilidades: {habilidades}

Forneça uma análise em 4 seções:
1. Pontos fortes
2. Áreas de melhoria
3. Sugestões de desenvolvimento
4. Feedback empático final
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"nome": nome, "resultado": resultado}
    return RedirectResponse(url=f"/mentor/resultado?id={uid}", status_code=303)

@app.get("/mentor/resultado")
def mostrar_resultado_mentor(request: Request, id: str):
    data = results_store.get(id)
    nome = data["nome"] if data else "Usuário"
    resultado = data["resultado"] if data else "Nenhum resultado disponível."
    return templates.TemplateResponse("mentor/resultado.html", {"request": request, "nome": nome, "resultado": resultado})

# ----------------- LinkedIn - Otimização -----------------

@app.get("/linkedin")
def linkedin_form(request: Request):
    return templates.TemplateResponse("linkedin/linkedin_form.html", {"request": request})

@app.post("/api/linkedin")
async def linkedin_analise(request: Request, nome: str = Form(...), cargo: str = Form(...), resumo: str = Form(...), experiencia: str = Form(...)):
    prompt = f"""
Otimize a seguinte bio do LinkedIn com um tom profissional, persuasivo e envolvente.
Nome: {nome}
Cargo atual: {cargo}
Bio atual: {resumo}
Experiência detalhada: {experiencia}

Gere uma versão aprimorada para a seção 'Sobre' do LinkedIn.
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"nome": nome, "resultado": resultado}
    return RedirectResponse(url=f"/linkedin/resultado?id={uid}", status_code=303)

@app.get("/linkedin/resultado")
def linkedin_resultado(request: Request, id: str):
    data = results_store.get(id)
    nome = data["nome"] if data else "Usuário"
    resultado = data["resultado"] if data else "Nenhum resultado disponível."
    return templates.TemplateResponse("linkedin/linkedin_resultado.html", {"request": request, "nome": nome, "resultado": resultado})

# ----------------- Cliente Ideal -----------------

@app.get("/cliente")
def cliente_form(request: Request):
    return templates.TemplateResponse("client/cliente_form.html", {"request": request})

@app.post("/api/cliente")
async def analisar_cliente(
    request: Request,
    segmento: str = Form(...),
    dores: str = Form(...),
    solucoes: str = Form(...),
    perfil: str = Form(...),
    objetivo: str = Form(...),
    fontes: str = Form(""),
    abordagem: str = Form("Email de prospecção")
):
    prompt = f"""
Você é um especialista em marketing e vendas. Com base nas seguintes informações, gere um perfil detalhado de cliente ideal (ICP), com persona fictícia, objetivos, dores, necessidades, estilo de comunicação, e sugestões de abordagem:

Segmento: {segmento}
Dores: {dores}
Soluções: {solucoes}
Perfil típico: {perfil}
Objetivo: {objetivo}
Fontes externas: {fontes}
Tipo de abordagem desejada: {abordagem}

Inclua ao final sugestões práticas e diretas de abordagem (ex: modelo de email, pitch).
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"resultado": resultado}
    return RedirectResponse(url=f"/cliente/resultado?id={uid}", status_code=303)

@app.get("/cliente/resultado")
def resultado_cliente(request: Request, id: str):
    data = results_store.get(id)
    resultado = data["resultado"] if data else "Nenhum resultado disponível."
    return templates.TemplateResponse("client/cliente_resultado.html", {"request": request, "resultado": resultado})
