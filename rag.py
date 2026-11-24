"""rag.py - a parte "R" do RAG: RECUPERAR trechos do FAQ parecidos com a pergunta.

Versao didatica, sem bibliotecas externas: compara PALAVRAS (busca lexical).
Mais para frente, esta funcao pode ser trocada por uma busca com embeddings
(por exemplo, ChromaDB) sem mexer no resto do projeto.
"""
import re
import unicodedata
from pathlib import Path

CAMINHO_FAQ = Path(__file__).parent / "dados" / "faq_clinica.md"

# Palavras comuns que nao ajudam a achar o assunto (ja sem acento).
PALAVRAS_VAZIAS = {
    "que", "para", "por", "com", "uma", "uns", "das", "dos", "nas", "nos", "aos",
    "voce", "voces", "qual", "quais", "como", "onde", "quando", "quanto", "quantos",
    "tem", "tenho", "estou", "sou", "posso", "pode", "podem", "preciso", "queria",
    "quero", "fazer", "minha", "meu", "seu", "sua", "nao", "sim", "mais", "muito",
    "muita", "aqui", "ola", "bom", "boa", "dia", "tarde", "noite", "favor", "mas",
    "ser", "ter", "esta", "esse", "essa", "isso", "tambem", "clinica", "sobre",
}


def normalizar(texto: str) -> str:
    """Deixa o texto em minusculas e sem acentos, para comparar sem erro."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acento.lower()


def palavras_chave(texto: str) -> set:
    """Conjunto de palavras uteis do texto (3+ letras, sem as 'vazias')."""
    achadas = re.findall(r"[a-z0-9]+", normalizar(texto))
    return {p for p in achadas if len(p) >= 3 and p not in PALAVRAS_VAZIAS}


def carregar_faq(caminho=CAMINHO_FAQ) -> list:
    """Le o arquivo do FAQ e devolve uma lista de trechos.

    Cada trecho comeca com uma linha assim:  ## [F01] Titulo do assunto
    """
    conteudo = Path(caminho).read_text(encoding="utf-8")
    padrao = r"^## \[(F\d+)\]\s*(.+?)\n(.*?)(?=^## \[|\Z)"
    trechos = []
    for m in re.finditer(padrao, conteudo, flags=re.S | re.M):
        corpo = m.group(3).strip()
        # Linha opcional "Palavras-chave: a, b, c": ajuda a busca a achar sinonimos
        # ("horas", "abre"...) e NAO e enviada ao modelo.
        achou = re.search(r"^Palavras-chave:\s*(.+)$", corpo, flags=re.M)
        chaves = achou.group(1) if achou else ""
        if achou:
            corpo = corpo.replace(achou.group(0), "").strip()
        trechos.append(
            {"id": m.group(1), "titulo": m.group(2).strip(), "texto": corpo,
             "palavras_chave": chaves}
        )
    return trechos


def buscar(pergunta: str, trechos: list, k: int = 2) -> list:
    """Devolve ate k trechos com mais palavras em comum com a pergunta.

    Palavras do TITULO e da linha "Palavras-chave" valem o dobro.
    Se nenhum trecho tiver palavra em comum, devolve lista vazia
    (e o chatbot deve responder "nao sei" em vez de inventar).
    """
    alvo = palavras_chave(pergunta)
    pontuados = []
    for trecho in trechos:
        pontos = 2 * len(alvo & palavras_chave(trecho["titulo"]))
        pontos += 2 * len(alvo & palavras_chave(trecho.get("palavras_chave", "")))
        pontos += len(alvo & palavras_chave(trecho["texto"]))
        if pontos > 0:
            pontuados.append((pontos, trecho))
    pontuados.sort(key=lambda par: -par[0])
    return [trecho for _, trecho in pontuados[:k]]
