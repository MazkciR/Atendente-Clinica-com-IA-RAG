"""llm.py - a unica parte que fala com o modelo de linguagem (LLM).

Dois modos, escolhidos pela variavel LLM_MODO no arquivo .env:

  simulado (padrao)  NAO usa internet nem chave. Devolve uma resposta montada
                     a partir do primeiro trecho do FAQ. Serve para testar o
                     "encanamento" do projeto. NAO mede a qualidade dos prompts.
  api                Chama o modelo de verdade. Exige LLM_API_KEY e LLM_MODEL.

Para trocar de provedor, so esta funcao precisa mudar: chamar_llm().
A chave de API vem SEMPRE de variavel de ambiente, nunca do codigo.
"""
import json
import os
import re
import urllib.error
import urllib.request

try:  # le o arquivo .env, se a biblioteca python-dotenv estiver instalada
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2023-06-01"


def modo_atual() -> str:
    return os.getenv("LLM_MODO", "simulado").strip().lower()


def chamar_llm(system: str, user: str) -> str:
    """Envia as instrucoes (system) e a mensagem (user) e devolve o texto."""
    modo = modo_atual()
    if modo == "simulado":
        return _simulado(system, user)
    if modo == "api":
        return _chamar_api(system, user)
    raise RuntimeError("LLM_MODO invalido: use 'simulado' ou 'api'.")


def _simulado(system: str, user: str) -> str:
    """Resposta de mentira, so para testar o fluxo sem internet."""
    achados = re.findall(r"^\[(\w+)\] (.*?): (.*)$", user, flags=re.M)
    quer_json = "JSON" in system
    if not achados:
        texto = "Não encontrei essa informação. Vou encaminhar para a recepção."
        if quer_json:
            return json.dumps(
                {"resposta": texto, "fonte": None, "encaminhar_recepcao": True},
                ensure_ascii=False,
            )
        return texto
    id_trecho, _titulo, texto = achados[0]
    if quer_json:
        return json.dumps(
            {"resposta": texto, "fonte": id_trecho, "encaminhar_recepcao": False},
            ensure_ascii=False,
        )
    return texto


def _chamar_api(system: str, user: str) -> str:
    chave = os.getenv("LLM_API_KEY", "").strip()
    modelo = os.getenv("LLM_MODEL", "").strip()
    if not chave:
        raise RuntimeError("Defina LLM_API_KEY no arquivo .env (veja o README).")
    if not modelo:
        raise RuntimeError("Defina LLM_MODEL no arquivo .env (veja o README).")

    corpo = {
        "model": modelo,
        "max_tokens": 500,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    # Algumas versoes de modelo nao aceitam "temperature": so envie se pedir.
    temperatura = os.getenv("LLM_TEMPERATURA", "").strip()
    if temperatura:
        corpo["temperature"] = float(temperatura)

    pedido = urllib.request.Request(
        URL_API,
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": chave,
            "anthropic-version": VERSAO_API,
        },
    )
    try:
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        # Nunca imprimimos a chave. Mostramos so o codigo do erro.
        raise RuntimeError(f"A API respondeu com erro HTTP {erro.code}.") from None
    except urllib.error.URLError:
        raise RuntimeError("Nao consegui falar com a API (internet?).") from None
    return dados["content"][0]["text"]
