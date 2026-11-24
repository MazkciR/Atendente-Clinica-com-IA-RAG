"""guardrails.py - "grades de protecao" antes e depois do modelo (requisito R5).

Importante: isto e uma PRIMEIRA barreira simples (regras), nao uma garantia.
Por isso o projeto tambem testa ataques em testes/casos_de_teste.jsonl.
"""
import re

from rag import normalizar

# Marcador secreto que fica no inicio dos prompts. Se aparecer na RESPOSTA,
# significa que o modelo "vazou" o prompt interno.
MARCADOR_PROMPT = "[[PROMPT_INTERNO]]"

LIMITE_CARACTERES = 800

# Frases tipicas de tentativa de enganar o modelo (ja sem acento, minusculas).
PADROES_INJECAO = [
    r"ignore (as|todas as|suas) (regras|instrucoes)",
    r"ignore (the|all|previous) (rules|instructions)",
    r"esqueca (as|suas|todas as) (regras|instrucoes)",
    r"(mostre|revele|exiba|imprima|repita) (o |seu |sua )?(seu |sua )?(prompt|instrucoes)",
    r"system prompt",
    r"modo (desenvolvedor|deus|admin)",
    r"nova regra",
    r"chave (de )?api",
    r"(senha|token) (do|da|de) (sistema|servidor|admin)",
]

# Dados pessoais que o usuario NAO deve enviar (LGPD: coletar so o necessario).
PADRAO_CPF = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
PADRAO_EMAIL = r"[\w.+-]+@[\w-]+\.[\w.-]+"

PADRAO_CHAVE_API = r"sk-[a-z0-9_-]{10,}"


def verificar_entrada(texto: str):
    """Confere a pergunta ANTES de chamar o modelo.

    Devolve (True, None) se estiver ok, ou (False, "motivo") se deve bloquear.
    """
    if len(texto) > LIMITE_CARACTERES:
        return False, "entrada_muito_longa"
    limpo = normalizar(texto)
    for padrao in PADROES_INJECAO:
        if re.search(padrao, limpo):
            return False, "possivel_prompt_injection"
    if re.search(PADRAO_CPF, texto) or re.search(PADRAO_EMAIL, texto):
        return False, "dados_pessoais"
    return True, None


def verificar_saida(dados: dict, trechos: list, bruto: str):
    """Confere a resposta DEPOIS do modelo.

    - nao pode conter o marcador do prompt interno nem algo parecido com chave de API;
    - se respondeu com uma fonte, a fonte precisa ser um dos trechos recuperados
      (isso ajuda a barrar fonte inventada = alucinacao).
    """
    if MARCADOR_PROMPT in bruto:
        return False, "vazamento_de_prompt"
    if re.search(PADRAO_CHAVE_API, bruto.lower()):
        return False, "vazamento_de_chave"
    if dados.get("json_valido") and not dados.get("encaminhar_recepcao"):
        ids_validos = {t["id"] for t in trechos}
        if dados.get("fonte") not in ids_validos:
            return False, "fonte_invalida"
    return True, None
