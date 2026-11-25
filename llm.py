import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

RAIZ = Path(__file__).parent

_client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=30000),
)
MODELO = os.environ["GEMINI_MODEL"]


def carregar_prompt(versao: str, pergunta: str | None = None) -> str:
    texto = (RAIZ / "prompts" / f"{versao}.md").read_text(encoding="utf-8")
    if "{TRECHOS}" in texto:
        # v4 (RAG): busca só os trechos da FAQ relevantes para esta pergunta
        from rag import buscar

        trechos = buscar(pergunta or "", k=3)
        texto = texto.replace("{TRECHOS}", "\n\n".join(t["texto"] for t in trechos))
    if "{FAQ}" in texto:
        faq = (RAIZ / "dados" / "faq_clinica.md").read_text(encoding="utf-8")
        texto = texto.replace("{FAQ}", faq)
    return texto


def montar_pergunta(versao: str, pergunta: str) -> str:
    if versao in ("v3", "v4"):
        return f"<pergunta_do_paciente>\n{pergunta}\n</pergunta_do_paciente>"
    return pergunta


def chamar_llm(prompt_sistema: str, pergunta: str, json_saida: bool = False, temperatura=None) -> str:
    config = types.GenerateContentConfig(
        system_instruction=prompt_sistema,
        response_mime_type="application/json" if json_saida else None,
        temperature=temperatura,
    )
    resposta = _client.models.generate_content(
        model=MODELO,
        contents=pergunta,
        config=config,
    )
    return resposta.text or ""