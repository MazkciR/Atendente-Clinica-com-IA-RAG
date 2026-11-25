import json
import sys
from pathlib import Path

versao = sys.argv[1] if len(sys.argv) > 1 else "v2"
caminho = Path(__file__).parent / "testes" / "resultados.json"
dados = json.loads(caminho.read_text(encoding="utf-8"))

for r in dados:
    if r["versao"] == versao and not r.get("correto"):
        print(f"--- caso {r['id']} ({r['categoria']}): {r['pergunta']}")
        print("RESPOSTA:", r["resposta"])
        print("JUIZ:", r.get("motivo"))
        print()