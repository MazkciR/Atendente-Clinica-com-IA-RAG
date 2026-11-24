# 03. Plano e checklist

Situação em **24/11/2026**. A entrega e as apresentações são em **25/11/2026**, no início do encontro.

## Feito
- [x] Problema, usuário e métrica definidos ([01](01-sobre-o-trabalho.md))
- [x] Arquitetura e tecnologias escolhidas ([02](02-arquitetura.md))
- [x] FAQ fictício (`dados/faq_clinica.md`)
- [x] Busca no FAQ (`rag.py`)
- [x] Proteções de entrada e saída (`guardrails.py`)
- [x] Prompts v1, v2 e v3 (`prompts/`)
- [x] 18 casos de teste, com ataques, viés e LGPD (`testes/casos_de_teste.jsonl`)
- [x] Script de avaliação (`avaliar.py`)
- [x] Interface de chat (`app.py`)
- [x] 13 testes automáticos, todos passando em modo simulado
- [x] README em formato de tutorial

## Falta
Em ordem de prioridade para a entrega:

1. [ ] **Ligar a um modelo real** e fazer a primeira chamada de verdade (o `llm.py` ainda não foi validado com a API)
2. [ ] **Rodar `python avaliar.py` em modo `api`** e anotar o placar de v1, v2 e v3
3. [ ] **Analisar os erros**: em quais casos cada versão falhou e por quê (isso vale mais que a nota final do placar)
4. [ ] Ajustar o prompt v3 se algum ataque passar (injeção indireta `t15`, vazamento, orientação clínica `t12`)
5. [ ] Conferir o viés: as respostas de `t16` e `t17` devem ser equivalentes
6. [ ] **Relatório técnico** (até 8 páginas): problema, arquitetura, modelo, prompts, personalização, avaliação, riscos e limitações. Declarar o uso de assistentes de IA e as fontes
7. [ ] **Pedir para uma pessoa de fora** seguir o README do zero, e corrigir onde ela travar
8. [ ] **Gravar um vídeo curto da demonstração** (plano B se a internet ou a API falharem)
9. [ ] Ensaiar o pitch com cronômetro: 7 minutos + 3 de perguntas

## Roteiro sugerido do pitch (7 minutos)
| Parte | Tempo | Conteúdo |
|---|---|---|
| Problema | ~1 min | Quem usa, qual a dor, por que IA generativa |
| Solução | ~1,5 min | Arquitetura e RAG, com o desenho |
| Demonstração ao vivo | ~2,5 min | Uma pergunta normal, uma pergunta fora do FAQ ("não sei") e um ataque bloqueado |
| Resultados | ~1 min | Placar v1 → v3 e o que aprendemos |
| Riscos e próximos passos | ~1 min | Limitações, segurança e WhatsApp via n8n |

## Registro dos resultados (preencher)
| Versão | Acertos (de 18) | JSON válido | Principais falhas | O que mudou para a versão seguinte |
|---|---|---|---|---|
| v1 | | | | |
| v2 | | | | |
| v3 | | | | |
