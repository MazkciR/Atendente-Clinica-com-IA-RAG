import json
from collections import defaultdict

d = json.load(open("testes/resultados.json", encoding="utf-8"))
cat = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for r in d:
    c = cat[r["categoria"]][r["versao"]]
    c[1] += 1
    c[0] += 1 if r.get("correto") else 0

print("| Categoria | v1 | v2 | v3 |")
print("|---|---|---|---|")
for nome, v in cat.items():
    print(f"| {nome} | " + " | ".join(f"{v[x][0]}/{v[x][1]}" for x in ("v1", "v2", "v3")) + " |")

print()
print("Falhas do v1:")
for r in d:
    if r["versao"] == "v1" and not r.get("correto"):
        print(f"- caso {r['id']} ({r['categoria']}): {r.get('motivo')}")
        