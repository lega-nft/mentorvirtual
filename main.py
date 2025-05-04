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

# Armazenar os resultados em memória temporariamente
results_store = {}
linkedin_store = {}
cliente_store = {}

@app.get("/")
def homepage(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})

@app.post("/api/analisar")
async def analisar(request: Request, nome: str = Form(...), objetivo: str = Form(...), experiencia: str = Form(...), habilidades: str = Form(...)):
    prompt = f"""
Analise o seguinte perfil profissional com base nas informações fornecidas:
Nome: {nome}
Objetivo profissional: {objetivo}
Experiência: {experiencia}
Habilidades: {habilidades}

Forneça uma análise em 4 seções:
1. Pontos fortes (marcados com bullet points)
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
    return RedirectResponse(url=f"/resultado?id={uid}", status_code=303)

@app.get("/resultado")
async def resultado(request: Request, id: str):
    data = results_store.get(id)
    if not data:
        return templates.TemplateResponse("resultado.html", {"request": request, "nome": "Usuário", "resultado": "Nenhum resultado disponível."})
    return templates.TemplateResponse("resultado.html", {"request": request, "nome": data['nome'], "resultado": data['resultado']})

# NOVAS ROTAS: ASSISTENTE LINKEDIN
@app.get("/linkedin")
async def linkedin_form(request: Request):
    return templates.TemplateResponse("linkedin.html", {"request": request})

@app.post("/api/otimizar-linkedin")
async def otimizar_linkedin(
    request: Request,
    nome: str = Form(...),
    cargo: str = Form(...),
    resumo: str = Form(...),
    experiencia: str = Form(...)
):
    prompt = f"""
Aja como um consultor de LinkedIn. Otimize o seguinte perfil profissional com um tom persuasivo, estratégico e profissional. Não invente dados, apenas melhore o que for fornecido. Use linguagem atrativa.

Nome: {nome}
Cargo atual: {cargo}
Resumo original: {resumo}
Experiência profissional: {experiencia}

Responda com:
1. Uma nova versão otimizada da seção "Sobre" do LinkedIn.
2. Sugestões de melhoria para a seção de "Experiência Profissional", considerando estrutura, resultados mensuráveis, palavras-chave e impacto.
"""

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    linkedin_store[uid] = {"nome": nome, "resultado": resultado}
    return RedirectResponse(url=f"/linkedin-resultado?id={uid}", status_code=303)

@app.get("/linkedin-resultado")
async def linkedin_resultado(request: Request, id: str):
    data = linkedin_store.get(id)
    if not data:
        return templates.TemplateResponse("resultado.html", {"request": request, "nome": "Usuário", "resultado": "Nenhum resultado disponível."})
    return templates.TemplateResponse("resultado.html", {"request": request, "nome": data['nome'], "resultado": data['resultado']})

# NOVAS ROTAS: MAPEAMENTO DE CLIENTE
@app.get("/cliente")
async def cliente_form(request: Request):
    return templates.TemplateResponse("cliente_perfil.html", {"request": request})

@app.post("/api/mapear-cliente")
async def mapear_cliente(
    request: Request,
    segmento: str = Form(...),
    problemas: str = Form(...),
    solucao: str = Form(...),
    perfil: str = Form(...),
    objetivo: str = Form(...),
    fontes: str = Form(""),
    abordagem: str = Form("Email de prospecção")
):
    prompt = f"""
Você é um especialista em estratégia de negócios e marketing. Com base nas informações abaixo, gere um perfil detalhado do cliente ideal, incluindo:

1. Persona (nome fictício, idade, profissão)
2. Objetivos e metas
3. Dores e necessidades
4. Estilo de comunicação
5. Canais preferidos
6. Comportamentos de compra

Além disso:
7. Analise as fontes fornecidas como site ou perfil social (descreva o tom, posicionamento e estilo percebido): {fontes}
8. Sugira 2 ou 3 formas estratégicas de abordar esse cliente.
9. Gere um modelo de abordagem no formato selecionado: {abordagem}

---
Segmento: {segmento}
Dores principais: {problemas}
Soluções oferecidas: {solucao}
Perfil típico: {perfil}
Objetivo com o mapeamento: {objetivo}
"""

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200
    )

    resultado = response.choices[0].message.content
    uid = str(uuid.uuid4())
    cliente_store[uid] = {"resultado": resultado}
    return RedirectResponse(url=f"/cliente-resultado?id={uid}", status_code=303)

@app.get("/cliente-resultado")
async def cliente_resultado(request: Request, id: str):
    data = cliente_store.get(id)
    if not data:
        return templates.TemplateResponse("resultado.html", {"request": request, "nome": "Perfil do Cliente", "resultado": "Nenhum resultado disponível."})
    return templates.TemplateResponse("resultado.html", {"request": request, "nome": "Perfil do Cliente", "resultado": data['resultado']})
