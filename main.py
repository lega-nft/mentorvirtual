from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    preferencias: str = Form(...)
):
    prompt = f"""
Você é um consultor de carreira com experiência em coaching e mercado de trabalho moderno. Sua missão é analisar o perfil abaixo de maneira personalizada, suave e didática, como se estivesse guiando a pessoa em uma mentoria individual.

Dado esse perfil:

Nome: {nome}
Cargo Atual: {cargo}
Experiência Profissional: {experiencia}
Habilidades Técnicas: {habilidades}
Soft Skills: {soft_skills}
Objetivo Profissional: {objetivo}
Desafios Enfrentados: {desafios}
Perfil no LinkedIn: {linkedin}
Preferências Pessoais ou Profissionais: {preferencias}

Faça uma análise com os seguintes elementos:

1. Visão Geral do Perfil
2. Oportunidades de Melhoria
3. Sugestões de Ações
4. Próximos Passos
5. Mensagem Final de Incentivo

Use uma linguagem amigável, profissional e empática. Evite parecer genérico ou mecânico.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    analise = response.choices[0].message.content

    html_resultado = f"""
    <html>
      <head>
        <title>Perfil Analisado</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            padding: 2rem;
            line-height: 1.6;
          }}
          h1 {{
            color: #2d2dff;
          }}
          a {{
            display: inline-block;
            margin-top: 2rem;
            text-decoration: none;
            color: white;
            background: #2d2dff;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
          }}
          pre {{
            white-space: pre-wrap;
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 8px;
          }}
        </style>
      </head>
      <body>
        <h1>Olá {nome.upper()} 👋</h1>
        <p>Segue abaixo a sua análise de perfil profissional com sugestões e insights personalizados:</p>
        <pre>{analise}</pre>
        <a href='https://mentorvirtual.vercel.app'>⬅ Voltar ao formulário</a>
      </body>
    </html>
    """

    return html_resultado
