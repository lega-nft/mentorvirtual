from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import os, uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
results_store = {}

# LOGIN
@app.get("/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/login")
def do_login(request: Request, email: str = Form(...)):
    return RedirectResponse(url="/menu", status_code=303)

# DASHBOARD / MENU
@app.get("/menu")
def menu(request: Request):
    return templates.TemplateResponse("menu/dashboard.html", {"request": request})

# MENTOR: ANÁLISE DE PERFIL
@app.get("/mentor")
def mentor_form(request: Request):
    return templates.TemplateResponse("mentor/form.html", {"request": request})

@app.post("/api/analisar")
async def analisar(request: Request, nome: str = Form(...), objetivo: str = Form(...),
                   experiencia: str = Form(...), habilidades: str = Form(...)):
    prompt = f"""
Analise o seguinte perfil profissional:
Nome: {nome}
Objetivo: {objetivo}
Experiência: {experiencia}
Habilidades: {habilidades}
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
    nome = data["nome"] if data else "Usuário"
    resultado = data["resultado"] if data else "Nenhum resultado disponível."
    return templates.TemplateResponse("mentor/result.html", {"request": request, "nome": nome, "resultado": resultado})

# LINKEDIN
@app.get("/linkedin")
def linkedin_form(request: Request):
    return templates.TemplateResponse("linkedin/form.html", {"request": request})

@app.post("/api/linkedin")
async def linkedin_result(request: Request, nome: str = Form(...), cargo: str = Form(...), resumo: str = Form(...)):
    prompt = f"""
Melhore este resumo profissional para o LinkedIn:
Nome: {nome}
Cargo atual: {cargo}
Resumo: {resumo}
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"resultado": resultado}
    return RedirectResponse(url=f"/linkedin/resultado?id={uid}", status_code=303)

@app.get("/linkedin/resultado")
def linkedin_resultado(request: Request, id: str):
    resultado = results_store.get(id, {}).get("resultado", "Nenhum resultado disponível.")
    return templates.TemplateResponse("linkedin/result.html", {"request": request, "resultado": resultado})

# CLIENTE IDEAL
@app.get("/cliente")
def cliente_form(request: Request):
    return templates.TemplateResponse("client/form.html", {"request": request})

@app.post("/api/cliente")
async def cliente_result(request: Request,
                         segmento: str = Form(...),
                         dores: str = Form(...),
                         solucoes: str = Form(...),
                         perfil: str = Form(...),
                         objetivo: str = Form(...),
                         fontes: str = Form(""),
                         abordagem: str = Form(...)):
    prompt = f"""
Com base nos dados abaixo, crie um perfil ideal de cliente e sugestões de abordagem personalizada:
Segmento: {segmento}
Dores: {dores}
Soluções: {solucoes}
Perfil típico: {perfil}
Objetivo: {objetivo}
Fontes externas: {fontes}
Tipo de abordagem: {abordagem}
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
def cliente_resultado(request: Request, id: str):
    resultado = results_store.get(id, {}).get("resultado", "Nenhum resultado disponível.")
    return templates.TemplateResponse("client/result.html", {"request": request, "resultado": resultado})
