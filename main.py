from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure sua chave da OpenAI (você pode usar variáveis de ambiente no Railway)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/api/analisar", response_class=HTMLResponse)
async def analisar_perfil(
    nome: str = Form(...),
    cargo: str = Form(...),
    experiencia: str = Form(...),
    habilidades: str = Form(...),
    soft_skills: str = Form(...),
    objetivo: str = Form(...),
    desafios: str = Form(...),
    linkedin: str = Form(...),
    preferencias: str = Form(...),
    curriculo: UploadFile = File(...)
):
    conteudo_cv = await curriculo.read()
    texto_cv = conteudo_cv.decode("utf-8", errors="ignore")

    prompt = f"""
    Aja como um consultor de carreira.
    Analise o seguinte currículo:
    {texto_cv}

    Perfil do LinkedIn: {linkedin}

    Informações adicionais:
    Nome: {nome}
    Cargo atual: {cargo}
    Experiência: {experiencia}
    Habilidades técnicas: {habilidades}
    Soft skills: {soft_skills}
    Objetivo de carreira: {objetivo}
    Desafios enfrentados: {desafios}
    Preferências de atuação: {preferencias}

    Gere uma análise completa com:
    - Pontos fortes
    - Áreas a melhorar
    - Sugestões de melhorias no currículo e LinkedIn
    - Recomendação de próximo passo
    - Oportunidades compatíveis com o objetivo
    """

    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    analise = resposta["choices"][0]["message"]["content"]

    return f"""
    <html>
      <head>
        <title>Análise de Perfil</title>
        <style>
          body {{ font-family: Arial, sans-serif; padding: 2rem; }}
          h1 {{ color: #2d2dff; }}
          pre {{ background: #f4f4f4; padding: 1rem; border-radius: 8px; white-space: pre-wrap; }}
          a {{ display: inline-block; margin-top: 2rem; text-decoration: none; color: white; background: #2d2dff; padding: 0.6rem 1.2rem; border-radius: 8px; }}
        </style>
      </head>
      <body>
        <h1>Olá {nome} 👋</h1>
        <p>Aqui está sua análise completa:</p>
        <pre>{analise}</pre>
        <a href='https://mentorvirtual.vercel.app'>⬅ Voltar ao formulário</a>
      </body>
    </html>
    """
