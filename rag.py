import os
import re
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

RAIZ = Path(__file__).parent
CAMINHO_FAQ = RAIZ / "dados" / "faq_clinica.md"
MODELO_EMBEDDING = "gemini-embedding-001"
BACKEND = os.environ.get("RAG_EMBEDDINGS", "gemini")  # "gemini" ou "padrao"

_cliente = chromadb.PersistentClient(path=str(RAIZ / "chroma_db"))
_colecao = _cliente.get_or_create_collection(name=f"faq_clinica_{BACKEND}")
_gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _embeddings(textos: list[str], tipo: str) -> list[list[float]]:
    for tentativa in range(3):
        try:
            resposta = _gemini.models.embed_content(
                model=MODELO_EMBEDDING,
                contents=textos,
                config=types.EmbedContentConfig(task_type=tipo),
            )
            return [e.values for e in resposta.embeddings]
        except Exception:
            if tentativa == 2:
                raise
            time.sleep(5)


def dividir_faq(texto: str) -> list[dict]:
    """Quebra o FAQ em seções: cada '## [CODIGO] Título' vira um trecho."""
    trechos = []
    for bloco in re.split(r"\n(?=## \[)", texto):
        achou = re.match(r"## \[([A-Z0-9-]+)\]", bloco)
        if achou:
            trechos.append({"codigo": achou.group(1), "texto": bloco.strip()})
    return trechos


def indexar() -> int:
    trechos = dividir_faq(CAMINHO_FAQ.read_text(encoding="utf-8"))
    ids = [t["codigo"] for t in trechos]
    documentos = [t["texto"] for t in trechos]
    if BACKEND == "gemini":
        _colecao.upsert(
            ids=ids,
            documents=documentos,
            embeddings=_embeddings(documentos, "RETRIEVAL_DOCUMENT"),
        )
    else:
        _colecao.upsert(ids=ids, documents=documentos)
    return len(trechos)


def buscar(pergunta: str, k: int = 3) -> list[dict]:
    if _colecao.count() == 0:
        indexar()
    if BACKEND == "gemini":
        resultado = _colecao.query(
            query_embeddings=_embeddings([pergunta], "RETRIEVAL_QUERY"),
            n_results=k,
        )
    else:
        resultado = _colecao.query(query_texts=[pergunta], n_results=k)
    return [
        {"codigo": codigo, "texto": texto, "distancia": dist}
        for codigo, texto, dist in zip(
            resultado["ids"][0],
            resultado["documents"][0],
            resultado["distances"][0],
        )
    ]


if __name__ == "__main__":
    print(f"[{BACKEND}] {indexar()} trechos indexados\n")
    for pergunta in [
        "Que horas vocês abrem?",
        "Quanto custa o clareamento?",
        "Meu rosto está inchado depois de um procedimento",
    ]:
        print(pergunta)
        for r in buscar(pergunta):
            print(f"   {r['codigo']:8} distância {r['distancia']:.2f}")