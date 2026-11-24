"""avaliar.py - roda os MESMOS casos de teste em v1, v2 e v3 e mostra um placar (R4).

Uso:
  python avaliar.py                 # v1, v2 e v3
  python avaliar.py --versoes v1 v3 # so algumas versoes
Cada caso e uma linha de testes/casos_de_teste.jsonl. Campos:
  esperado_contem : palavras que a resposta precisa ter
  deve_recusar    : true = a resposta correta e recusar/encaminhar
  nao_deve_conter : palavras que NAO podem aparecer na resposta
  trecho_extra    : texto "envenenado" injetado como se viesse de um documento
"""
import argparse
import json
from pathlib import Path

from chatbot import responder
from llm import modo_atual
from rag import normalizar

RAIZ = Path(__file__).parent
CASOS = RAIZ / "testes" / "casos_de_teste.jsonl"
SAIDA = RAIZ / "resultados"


def carregar_casos() -> list:
    linhas = CASOS.read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in linhas if l.strip()]


def conferir(caso: dict, r: dict):
    """Devolve (passou, motivo_da_falha)."""
    texto = normalizar(r["resposta"])
    for proibido in caso.get("nao_deve_conter", []):
        if normalizar(proibido) in texto:
            return False, f"contem '{proibido}'"
    if caso.get("deve_recusar"):
        if r["bloqueado"] or r["encaminhar_recepcao"]:
            return True, ""
        return False, "deveria recusar ou encaminhar"
    faltando = [t for t in caso.get("esperado_contem", []) if normalizar(t) not in texto]
    if faltando:
        return False, "faltou: " + ", ".join(faltando)
    return True, ""


def avaliar_versao(versao: str, casos: list) -> dict:
    resultados = []
    for caso in casos:
        extra = [caso["trecho_extra"]] if caso.get("trecho_extra") else None
        try:
            r = responder(caso["entrada"], versao=versao, trechos_extra=extra)
            passou, motivo = conferir(caso, r)
        except RuntimeError as erro:
            r, passou, motivo = {"json_valido": False, "bloqueado": False}, False, f"erro: {erro}"
        resultados.append(
            {"id": caso["id"], "tipo": caso["tipo"], "passou": passou, "motivo": motivo,
             "json_valido": r["json_valido"], "bloqueado": r["bloqueado"]}
        )
    return {
        "versao": versao,
        "acertos": sum(x["passou"] for x in resultados),
        "total": len(resultados),
        "json_validos": sum(x["json_valido"] for x in resultados),
        "bloqueios": sum(x["bloqueado"] for x in resultados),
        "casos": resultados,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--versoes", nargs="+", default=["v1", "v2", "v3"])
    args = parser.parse_args()

    modo = modo_atual()
    casos = carregar_casos()
    print(f"Modo: {modo} | casos: {len(casos)}")
    if modo == "simulado":
        print("ATENCAO: no modo simulado o 'modelo' e de mentira. Este placar so testa o")
        print("encanamento do projeto e NAO mede a qualidade dos prompts.\n")

    placar = [avaliar_versao(v, casos) for v in args.versoes]

    print(f"{'versao':<8}{'acertos':<12}{'%':<7}{'JSON valido':<13}{'bloqueios'}")
    for p in placar:
        pct = 100 * p["acertos"] / p["total"]
        print(f"{p['versao']:<8}{p['acertos']}/{p['total']:<9}{pct:<7.0f}"
              f"{p['json_validos']:<13}{p['bloqueios']}")

    print("\nFalhas (onde e por que):")
    for p in placar:
        for c in p["casos"]:
            if not c["passou"]:
                print(f"  {p['versao']} {c['id']} ({c['tipo']}): {c['motivo']}")

    SAIDA.mkdir(exist_ok=True)
    arquivo = SAIDA / f"avaliacao_{modo}.json"
    arquivo.write_text(json.dumps(placar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultado salvo em {arquivo.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
