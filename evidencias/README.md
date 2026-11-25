# Evidências

Saídas reais do atendente, identificadas por caso, sem dados pessoais e sem chaves.

| Arquivo | Conteúdo |
|---|---|
| `C01_v1.txt` … `C05_v2.txt` | Os 5 casos do caderno, nas versões v1 e v2: pergunta, esperado (escrito antes de rodar), saída do modelo sem edição e veredito do juiz |
| `resumo_21_casos.md` | Os 21 casos nas versões v1 a v4 (certo/errado pelo juiz) |
| `execucao_avaliar_2026-11-25.txt` | Saída do terminal de `python avaliar.py` (exemplo de execução) |
| `demo_app_v4_vs_v1.md` | As mesmas perguntas no app, na v4 e na v1 |

Correspondência dos casos: C01 = caso 1, C02 = caso 5, C03 = caso 3, C04 = caso 2, C05 = caso 8 (de `testes/casos_de_teste.jsonl`).
As respostas completas das 4 versões estão em `testes/resultados.json`; a rodada anterior ao ajuste do juiz está em `testes/resultados_antigo.json`.
