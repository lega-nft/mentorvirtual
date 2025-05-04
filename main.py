from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html lang=\"pt-BR\">
    <head>
      <meta charset=\"UTF-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>
      <title>Mentor Virtual</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          padding: 2rem;
          max-width: 700px;
          margin: auto;
        }
        h1 {
          color: #2d2dff;
          margin-bottom: 1rem;
        }
        label {
          font-weight: bold;
          display: block;
          margin-top: 1rem;
        }
        input, textarea {
          width: 100%;
          padding: 0.6rem;
          margin-top: 0.3rem;
          border-radius: 6px;
          border: 1px solid #ccc;
        }
        button {
          margin-top: 2rem;
          padding: 0.7rem 1.5rem;
          background-color: #2d2dff;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 1rem;
        }
        button:hover {
          background-color: #1a1aff;
        }
      </style>
    </head>
    <body>
      <h1>Mentor Virtual – Análise de Perfil Profissional</h1>
      <form action=\"/api/analisar\" method=\"post\">
        <label for=\"nome\">Nome completo</label>
        <input type=\"text\" name=\"nome\" required />

        <label for=\"cargo\">Cargo atual</label>
        <input type=\"text\" name=\"cargo\" required />

        <label for=\"experiencia\">Experiência profissional</label>
        <textarea name=\"experiencia\" rows=\"4\" required></textarea>

        <label for=\"habilidades\">Habilidades técnicas</label>
        <textarea name=\"habilidades\" rows=\"3\" required></textarea>

        <label for=\"soft_skills\">Soft Skills (comportamentais)</label>
        <textarea name=\"soft_skills\" rows=\"3\" required></textarea>

        <label for=\"objetivo\">Objetivo profissional</label>
        <input type=\"text\" name=\"objetivo\" required />

        <label for=\"desafios\">Desafios enfrentados</label>
        <textarea name=\"desafios\" rows=\"3\"></textarea>

        <label for=\"linkedin\">Link do seu LinkedIn</label>
        <input type=\"url\" name=\"linkedin\" placeholder=\"https://linkedin.com/in/seuperfil\" />

        <label for=\"preferencias\">Preferências de carreira, empresa, cultura etc.</label>
        <textarea name=\"preferencias\" rows=\"3\"></textarea>

        <button type=\"submit\">🔍 Analisar Perfil</button>
      </form>
    </body>
    </html>
    """

@app.post("/api/analisar", response_class=HTMLResponse)
async def analisar_perfil(
    nome: str = Form(...),
    cargo: str = Form(...),
    experiencia: str = Form(...),
    habilidades: str = Form(...),
    soft_skills: str = Form(...),
    objetivo: str = Form(...),
    desafios: str = Form(""),
    linkedin: str = Form(""),
    preferencias: str = Form("")
):
    prompt = f"""
Você é um mentor de carreira virtual, com foco em desenvolvimento profissional e orientação prática. Analise o seguinte perfil e forneça um diagnóstico completo em 4 seções:
1. Pontos fortes identificados;
2. Áreas de melhoria;
3. Sugestões de desenvolvimento de carreira (como cursos, práticas, cargos e empresas);
4. Feedback final de incentivo como um coach empático.

### Dados do profissional:
- Nome: {nome}
- Cargo atual: {cargo}
- Experiência: {experiencia}
- Habilidades técnicas: {habilidades}
- Soft skills: {soft_skills}
- Objetivo profissional: {objetivo}
- Desafios enfrentados: {desafios}
- LinkedIn: {linkedin}
- Preferências: {preferencias}
"""

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "Você é um mentor de carreira profissional."},
                {"role": "user", "content": prompt}
            ]
        )
        analise = resposta.choices[0].message.content.strip()
    except Exception as e:
        analise = f"Erro ao processar a análise com a IA: {e}"

    return f"""
    <html>
      <head>
        <meta charset=\"utf-8\"/>
        <title>Análise de Perfil</title>
        <style>
          body {{ font-family: Arial, sans-serif; padding: 2rem; max-width: 800px; margin: auto; }}
          h1 {{ color: #2d2dff; }}
          pre {{ background: #f4f4f4; padding: 1rem; border-radius: 8px; white-space: pre-wrap; }}
          a {{ display: inline-block; margin-top: 2rem; text-decoration: none; color: white; background: #2d2dff; padding: 0.6rem 1.2rem; border-radius: 8px; }}
        </style>
      </head>
      <body>
        <h1>Olá, {nome} 👋</h1>
        <p>Veja abaixo sua análise personalizada:</p>
        <pre>{analise}</pre>
        <a href=\"/\">⬅ Voltar ao formulário</a>
      </body>
    </html>
    """
