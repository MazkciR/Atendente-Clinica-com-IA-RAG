import json
import sys
from pathlib import Path

from rag import buscar

RAIZ = Path(__file__).parent


def carregar_casos():
    caminho = RAIZ / "testes" / "casos_de_teste.jsonl"
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas if linha.strip()]


def main(k: int = 3):
    casos = [c for c in carregar_casos() if c["fonte"]]
    acertos = 0
    for caso in casos:
        codigos = [r["codigo"] for r in buscar(caso["pergunta"], k)]
        achou = caso["fonte"] in codigos
        acertos += achou
        marca = "OK  " if achou else "MISS"
        print(f"{marca} caso {caso['id']:>2} esperado {caso['fonte']:8} -> {codigos}")
    print(f"\nAcerto da busca (top-{k}): {acertos}/{len(casos)} ({100 * acertos / len(casos):.0f}%)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)