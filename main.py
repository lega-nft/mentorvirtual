from fastapi import FastAPI, Form, Request
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
      <head><title>Perfil Analisado</title></head>
      <body style="font-family:sans-serif; padding:2rem;">
        <h1>Olá {nome} 👋</h1>
        <p>Seu perfil foi analisado com sucesso!</p>
        <p><strong>Cargo:</strong> {cargo}</p>
        <p><strong>Objetivo:</strong> {objetivo}</p>
        <p><strong>Próximo passo:</strong> Em breve você receberá sugestões personalizadas no seu e-mail ou LinkedIn.</p>
        <a href="https://mentorvirtual.vercel.app" style="margin-top:2rem; display:inline-block;">⬅ Voltar ao formulário</a>
      </body>
    </html>
    """
