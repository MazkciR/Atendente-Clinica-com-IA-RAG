# 04. Glossário

Termos de IA usados neste projeto, em linguagem simples.

## Como o modelo funciona
| Termo | Significado |
|---|---|
| **LLM** | *Large Language Model*: grande modelo de linguagem, como GPT, Claude e Gemini |
| **Token** | A unidade que o modelo lê e escreve. Pode ser uma palavra, um pedaço de palavra ou um sinal. **Token não é palavra** |
| **Contexto (janela de contexto)** | Tudo o que vai na chamada: instruções, histórico, pergunta, fontes e o espaço da resposta. Tem limite e conta no custo |
| **Embedding** | Lista de números que representa um texto. Textos de assunto parecido ficam com números parecidos |
| **Atenção** | Mecanismo em que cada palavra "olha" para as outras e dá mais peso às relevantes |
| **Transformer** | Arquitetura de rede neural baseada em atenção, usada pelos LLMs atuais |
| **Encoder / Decoder** | O encoder lê a entrada inteira (serve para classificar e buscar). O decoder gera texto um token por vez (é o que os assistentes fazem) |

## Os três "pesos" que confundem
| Termo | Significado | Quando muda |
|---|---|---|
| **Pesos do modelo** | Números aprendidos no treino. É o "conhecimento" do modelo | Só no treino |
| **Contexto** | O que você envia em cada chamada | A cada chamada |
| **Pesos de atenção** | Quanto cada palavra influencia a próxima, calculado na hora | A cada resposta |

Colar um texto no chat muda o contexto, **não** os pesos do modelo. Por isso o RAG funciona sem retreinar.

## Treino e uso
| Termo | Significado |
|---|---|
| **Pré-treino** | O modelo lê muito texto e aprende a prever o próximo token |
| **SFT** | Ajuste com exemplos de pedido e resposta desejada, para o modelo agir como assistente |
| **Inferência** | Usar o modelo já treinado para gerar uma resposta |
| **Temperatura** | Controla a variedade da escolha do próximo token. Baixa é mais previsível, alta é mais variada. Temperatura zero **não** garante que o fato seja verdadeiro |
| **Alucinação** | Resposta fluente e confiante, mas sem sustentação (data, número ou citação inventados) |

## Neste projeto
| Termo | Significado |
|---|---|
| **Prompt** | As instruções enviadas ao modelo. Aqui há três versões: v1, v2 e v3 |
| **RAG** | *Retrieval-Augmented Generation*. O sistema busca trechos de uma base de documentos e os entrega ao modelo junto com a pergunta |
| **Few-shot** | Dar exemplos de entrada e saída no prompt para o modelo imitar o formato |
| **Saída estruturada (JSON)** | Pedir a resposta em um formato fixo, para o programa conseguir conferir |
| **Guardrail** | "Grade de proteção": regra que barra pedidos ou respostas perigosas |
| **Injeção de prompt** | Tentativa de fazer o modelo desobedecer às instruções (direta: na pergunta. Indireta: escondida em um documento recuperado) |
| **LLM-as-judge** | Usar outro modelo para dar nota às respostas com base em uma rubrica |
| **Fine-tuning / LoRA** | Ajustar o próprio modelo. O LoRA treina só um adaptador pequeno e mantém o resto congelado |
| **LGPD** | Lei Geral de Proteção de Dados Pessoais (lei brasileira): coletar só o necessário e proteger dados pessoais |
| **JSONL** | Arquivo com um objeto JSON por linha. Usado nos casos de teste |

## Três confusões comuns
1. **Pesos do modelo × pesos de atenção**: os primeiros são fixos após o treino, os segundos são recalculados a cada entrada.
2. **Contexto × pesos**: colocar o manual no prompt não faz o modelo "aprender" o manual.
3. **Parecido × verdadeiro**: embedding próximo, peso de atenção alto e texto fluente **não** provam que a informação está correta. Sempre confira a fonte.
