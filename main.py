from fastapi import FastAPI, Request, Form
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
results_store = {}

# ======= LOGIN & MENU =======

@app.get("/")
def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.post("/login")
def login_submit(request: Request, email: str = Form(...)):
    # Você pode adicionar verificação de plano ou autenticação aqui no futuro
    return RedirectResponse(url="/menu", status_code=303)

@app.get("/menu")
def menu_page(request: Request):
    return templates.TemplateResponse("menu/menu.html", {"request": request})


# ======= MENTOR - ANÁLISE DE PERFIL PROFISSIONAL =======

@app.get("/mentor")
def mentor_form(request: Request):
    return templates.TemplateResponse("mentor/formulario.html", {"request": request})

@app.post("/api/analisar")
async def analisar(request: Request, nome: str = Form(...), objetivo: str = Form(...), experiencia: str = Form(...), habilidades: str = Form(...)):
    prompt = f"""
Analise o seguinte perfil profissional com base nas informações fornecidas:
Nome: {nome}
Objetivo profissional: {objetivo}
Experiência: {experiencia}
Habilidades: {habilidades}

Forneça uma análise em 4 seções:
1. Pontos fortes (bullet points)
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
    return RedirectResponse(url=f"/mentor-resultado?id={uid}", status_code=303)

@app.get("/mentor-resultado")
def mentor_resultado(request: Request, id: str):
    data = results_store.get(id)
    if not data:
        return templates.TemplateResponse("mentor/resultado.html", {"request": request, "nome": "Usuário", "resultado": "Nenhum resultado disponível."})
    return templates.TemplateResponse("mentor/resultado.html", {"request": request, "nome": data["nome"], "resultado": data["resultado"]})


# ======= LINKEDIN ASSISTANT =======

@app.get("/linkedin")
def linkedin_form(request: Request):
    return templates.TemplateResponse("linkedin/form.html", {"request": request})

@app.post("/api/otimizar-linkedin")
async def otimizar_linkedin(request: Request, nome: str = Form(...), cargo: str = Form(...), resumo: str = Form(...), experiencia: str = Form(...)):
    prompt = f"""
Otimize o perfil de LinkedIn do usuário com base nos dados fornecidos.

Nome: {nome}
Cargo atual: {cargo}
Resumo atual: {resumo}
Experiência atual: {experiencia}

Retorne uma nova versão da seção "Sobre" e destaque os pontos fortes que podem ser mais atrativos para recrutadores.
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"nome": nome, "resultado": resultado}
    return RedirectResponse(url=f"/linkedin-resultado?id={uid}", status_code=303)

@app.get("/linkedin-resultado")
def linkedin_resultado(request: Request, id: str):
    data = results_store.get(id)
    return templates.TemplateResponse("linkedin/resultado.html", {"request": request, "nome": data["nome"], "resultado": data["resultado"]})


# ======= CLIENTE IDEAL =======

@app.get("/cliente")
def cliente_form(request: Request):
    return templates.TemplateResponse("client/form.html", {"request": request})

@app.post("/api/cliente")
async def gerar_cliente(request: Request,
    segmento: str = Form(...),
    dores: str = Form(...),
    solucoes: str = Form(...),
    perfil: str = Form(...),
    objetivo: str = Form(...),
    fontes: str = Form(""),
    abordagem: str = Form("Email de prospecção")
):
    prompt = f"""
Com base nas informações abaixo, gere um perfil de cliente ideal (persona), incluindo:

1. Nome fictício
2. Idade aproximada
3. Profissão / Cargo
4. Objetivos e metas
5. Dores e necessidades
6. Estilo de comunicação
7. E ao final, gere sugestões específicas de como abordar esse cliente com base no tipo de abordagem: {abordagem}
8. Caso fontes externas estejam presentes, utilize como referência adicional: {fontes}

Informações:
- Segmento: {segmento}
- Dores: {dores}
- Soluções: {solucoes}
- Perfil típico: {perfil}
- Objetivo: {objetivo}
"""

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200
    )

    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    results_store[uid] = {"resultado": resultado}
    return RedirectResponse(url=f"/cliente-resultado?id={uid}", status_code=303)

@app.get("/cliente-resultado")
def cliente_resultado(request: Request, id: str):
    data = results_store.get(id)
    return templates.TemplateResponse("client/result.html", {"request": request, "resultado": data["resultado"]})
