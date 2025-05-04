from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

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
    return f"""
    <html>
      <head>
        <title>Perfil Analisado</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            padding: 2rem;
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
        </style>
      </head>
      <body>
        <h1>Olá {nome} 👋</h1>
        <p>Seu perfil foi analisado com sucesso!</p>
        <p><strong>Cargo:</strong> {cargo}</p>
        <p><strong>Objetivo:</strong> {objetivo}</p>
        <p><strong>Próximo passo:</strong> Em breve enviaremos sugestões personalizadas.</p>
        <a href='https://mentorvirtual.vercel.app'>⬅ Voltar ao formulário</a>
      </body>
    </html>
    """

