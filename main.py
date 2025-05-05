from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import os
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory stores
results_store = {}
linkedin_store = {}
client_store = {}

# --- Auth ---
@app.get("/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/login")
def do_login(request: Request, email: str = Form(...)):
    return RedirectResponse("/menu", status_code=303)

# --- Menu ---
@app.get("/menu")
def menu(request: Request):
    return templates.TemplateResponse("menu/index.html", {"request": request})

# --- Mentor ---
@app.get("/mentor")
def mentor_form(request: Request):
    return templates.TemplateResponse("mentor/form.html", {"request": request})

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
def mentor_resultado(request: Request, id: str):
    data = results_store.get(id)
    return templates.TemplateResponse("mentor/resultado.html", {"request": request, "nome": data['nome'] if data else "Usuário", "resultado": data['resultado'] if data else "Nenhum resultado disponível."})

# --- LinkedIn ---
@app.get("/linkedin")
def linkedin_form(request: Request):
    return templates.TemplateResponse("linkedin/form.html", {"request": request})

@app.post("/api/linkedin")
async def linkedin_otimizar(request: Request, nome: str = Form(...), cargo: str = Form(...), resumo: str = Form(...), experiencia: str = Form(...)):
    prompt = f"""
Otimize a seção \"Sobre\" do LinkedIn com base nas seguintes informações:
Nome: {nome}
Cargo atual: {cargo}
Resumo atual: {resumo}
Experiência profissional: {experiencia}

Crie um novo texto com tom profissional e persuasivo, voltado para networking e oportunidades.
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    linkedin_store[uid] = {"nome": nome, "resultado": resultado}
    return RedirectResponse(url=f"/linkedin/resultado?id={uid}", status_code=303)

@app.get("/linkedin/resultado")
def linkedin_resultado(request: Request, id: str):
    data = linkedin_store.get(id)
    return templates.TemplateResponse("linkedin/resultado.html", {"request": request, "nome": data['nome'], "resultado": data['resultado']})

# --- Cliente Ideal ---
@app.get("/cliente")
def cliente_form(request: Request):
    return templates.TemplateResponse("client/form.html", {"request": request})

@app.post("/api/cliente")
async def cliente_gerar(request: Request,
    segmento: str = Form(...),
    dores: str = Form(...),
    solucoes: str = Form(...),
    perfil: str = Form(...),
    objetivo: str = Form(...),
    fontes: str = Form(""),
    abordagem: str = Form(...)):

    prompt = f"""
Com base nas seguintes informações sobre o cliente-alvo, crie uma persona completa e detalhada, incluindo sugestões de abordagem personalizada:

Segmento: {segmento}
Dores: {dores}
Soluções: {solucoes}
Perfil: {perfil}
Objetivo: {objetivo}
Fontes externas: {fontes}
Tipo de abordagem: {abordagem}

Divida o conteúdo gerado em:
1. Persona resumida (nome fictício, idade, profissão)
2. Objetivos e metas
3. Dores e necessidades
4. Estilo de comunicação
5. Sugestões de abordagem
6. Modelos de mensagem ou email
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    client_store[uid] = {"resultado": resultado}
    return RedirectResponse(url=f"/cliente/resultado?id={uid}", status_code=303)

@app.get("/cliente/resultado")
def cliente_resultado(request: Request, id: str):
    data = client_store.get(id)
    return templates.TemplateResponse("client/resultado.html", {"request": request, "resultado": data['resultado'] if data else "Nenhum dado."})
