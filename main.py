
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
