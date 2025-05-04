from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/api/analisar")
def analisar_perfil(
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
    return {
        "mensagem": f"Olá {nome}, seu perfil foi analisado com sucesso!",
        "proximo_passo": "Vamos recomendar conteúdos e conexões em breve."
    }
