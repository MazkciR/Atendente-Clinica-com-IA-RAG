# 01. Sobre o trabalho: problema, usuário e requisitos

Resumo, em palavras próprias, do que a disciplina pede e de como este projeto responde a cada ponto.

## O desafio
Em grupo, construir um **protótipo funcional** de IA generativa que resolva um problema real de um usuário concreto. Não é preciso um produto pronto: é preciso mostrar que **funciona de ponta a ponta** e trazer **evidências** (versões de prompt, testes, tratamento de riscos).

## O problema que escolhemos (R1)
| Pergunta | Resposta |
|---|---|
| **Quem usa?** | Pacientes de clínicas odontológicas pequenas e a recepção que os atende |
| **Qual é a dor?** | A recepção perde tempo repetindo as mesmas respostas (horário, convênio, valores, remarcação) e deixa pessoas sem resposta fora do expediente |
| **Por que IA generativa e não regras fixas?** | As pessoas perguntam do jeito que querem ("que horas vocês abrem?", "funciona no sábado?"). Um modelo entende a intenção e escreve uma resposta natural; regras fixas exigiriam prever cada frase |
| **Como saber se funcionou?** | Percentual de respostas corretas nos casos de teste, mais: nenhuma resposta inventada (alucinação), nenhum vazamento e nenhuma orientação clínica |

## Requisitos mínimos e onde estão neste repositório
| Requisito | O que se espera | Onde está |
|---|---|---|
| **R1** Problema e valor | Usuário, dor, por que IA generativa, métrica | Este documento |
| **R2** Prompt engineering | Pelo menos 3 técnicas, com versões v1 → v2 → v3 comparadas | `prompts/` (veja abaixo) |
| **R3** Personalização | Pelo menos uma entre RAG, fine-tuning ou multimodal, com justificativa | RAG (`rag.py`, `dados/`); justificativa em [02-arquitetura](02-arquitetura.md) |
| **R4** Avaliação | 15 ou mais casos de teste, métrica ou LLM-as-judge, evolução entre versões | `testes/casos_de_teste.jsonl` (18 casos) e `avaliar.py` |
| **R5** Segurança e ética | Injeção de prompt, vazamento, alucinação, viés, LGPD: mitigação e testes | `guardrails.py` e [05-seguranca](05-seguranca.md) |

## As três versões de prompt (R2)
| Versão | Técnicas usadas | Ideia |
|---|---|---|
| **v1** | Instrução simples | Ponto de partida: só pede para responder com os trechos |
| **v2** | Persona + regras + **exemplos (few-shot)** + **saída estruturada em JSON** | Faz o modelo citar a fonte e admitir quando não sabe |
| **v3** | v2 + **separação entre instruções e dados** (a pergunta e os trechos são "dados não confiáveis") + recusa de orientação clínica + regras contra vazamento e viés | Defesa contra injeção de prompt e respostas perigosas |

Para cada versão registre no relatório: **o que mudou, por quê e o resultado nos mesmos casos de teste**.

## Entregáveis da disciplina
1. Protótipo funcional com README de execução (este repositório)
2. Relatório técnico de até 8 páginas
3. Biblioteca de prompts versionada (`prompts/`)
4. Apresentação de 7 minutos com demonstração ao vivo e 3 minutos de perguntas

## Regras importantes
- Assistentes de IA podem ser usados, **desde que declarados no relatório**
- Dados fictícios ou públicos, **nunca dados pessoais reais**
- Nunca versionar chaves de API
- Ter um vídeo da demonstração gravado como plano B
