"""chatbot.py - junta todas as pecas.

Caminho de uma pergunta:
  guardrails (entrada) -> rag (busca no FAQ) -> llm (modelo) -> guardrails (saida)

Dica: rode `python chatbot.py` para conversar pelo terminal, sem interface web.
"""
import json
import os
import re
from pathlib import Path

from guardrails import verificar_entrada, verificar_saida
from llm import chamar_llm, modo_atual
from rag import buscar, carregar_faq, normalizar

PASTA_PROMPTS = Path(__file__).parent / "prompts"

MSG_BLOQUEIO = (
    "Não posso ajudar com esse tipo de pedido por aqui. "
    "Se precisar, fale com a recepção da clínica."
)
MSG_ENCAMINHAR = (
    "Não encontrei essa informação com segurança. "
    "Vou encaminhar sua dúvida para a recepção."
)
SINAIS_DE_ENCAMINHAMENTO = ("recepcao", "nao sei", "nao encontrei")


def limpar(texto: str) -> str:
    """Remove < e > para que ninguem 'feche' as etiquetas do prompt de proposito."""
    return re.sub(r"[<>]", "", texto)


def ler_prompt(versao: str) -> str:
    return (PASTA_PROMPTS / f"{versao}.txt").read_text(encoding="utf-8")


def montar_mensagem(pergunta: str, trechos: list) -> str:
    """Monta a mensagem enviada ao modelo: trechos do FAQ + pergunta, separados."""
    if trechos:
        linhas = [
            f"[{t['id']}] {limpar(t['titulo'])}: {limpar(' '.join(t['texto'].split()))}"
            for t in trechos
        ]
    else:
        linhas = ["(nenhum trecho encontrado)"]
    return (
        "<trechos>\n" + "\n".join(linhas) + "\n</trechos>\n"
        "<pergunta>\n" + limpar(pergunta) + "\n</pergunta>"
    )


def interpretar(bruto: str) -> dict:
    """Transforma o texto do modelo em dados. Aceita JSON ou texto simples."""
    texto = bruto.strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto)  # tira cercas de codigo
    try:
        dados = json.loads(texto)
        if isinstance(dados, dict) and "resposta" in dados:
            return {
                "resposta": str(dados["resposta"]),
                "fonte": dados.get("fonte"),
                "encaminhar_recepcao": bool(dados.get("encaminhar_recepcao", False)),
                "json_valido": True,
            }
    except json.JSONDecodeError:
        pass
    encaminha = any(s in normalizar(texto) for s in SINAIS_DE_ENCAMINHAMENTO)
    return {
        "resposta": texto,
        "fonte": None,
        "encaminhar_recepcao": encaminha,
        "json_valido": False,
    }


def responder(pergunta: str, versao: str = None, trechos_extra: list = None) -> dict:
    """Responde uma pergunta. Devolve um dicionario com a resposta e os detalhes.

    trechos_extra: usado nos testes de injecao INDIRETA (um documento "envenenado").
    """
    versao = versao or os.getenv("PROMPT_VERSAO", "v3")
    base = {"versao": versao, "bloqueado": False, "motivo": None, "fonte": None,
            "encaminhar_recepcao": False, "json_valido": False}

    ok, motivo = verificar_entrada(pergunta)
    if not ok:
        return {**base, "resposta": MSG_BLOQUEIO, "bloqueado": True,
                "motivo": motivo, "encaminhar_recepcao": True}

    trechos = buscar(pergunta, carregar_faq())
    for i, texto in enumerate(trechos_extra or [], start=1):
        trechos.append({"id": f"X{i}", "titulo": "Documento externo", "texto": texto})

    bruto = chamar_llm(ler_prompt(versao), montar_mensagem(pergunta, trechos))
    dados = interpretar(bruto)

    ok, motivo = verificar_saida(dados, trechos, bruto)
    if not ok:
        return {**base, "resposta": MSG_ENCAMINHAR, "bloqueado": True,
                "motivo": motivo, "encaminhar_recepcao": True}
    return {**base, **dados}


if __name__ == "__main__":
    print(f"Atendente virtual (modo: {modo_atual()}). Digite 'sair' para encerrar.")
    while True:
        try:
            entrada = input("\nVoce: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if entrada.lower() in {"sair", "exit", "quit"}:
            break
        if not entrada:
            continue
        r = responder(entrada)
        fonte = f" [fonte: {r['fonte']}]" if r["fonte"] else ""
        print(f"Atendente: {r['resposta']}{fonte}")
        if r["bloqueado"]:
            print(f"  (bloqueado: {r['motivo']})")
