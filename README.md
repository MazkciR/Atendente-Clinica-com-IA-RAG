# Atendente virtual para clínicas odontológicas (RAG + Gemini)

Um chat que responde dúvidas de pacientes **somente com o que está escrito na FAQ da clínica**, mostra de onde tirou a resposta, admite quando não sabe e se recusa a dar orientação clínica.

Projeto final da disciplina *Advanced Generative AI* (MBA em AI Engineering & Multi-Agents). Todos os dados são fictícios (Clínica Exemplo); nenhum dado pessoal real é usado.

## Escolha o seu caminho

| Você é... | Comece por aqui |
|---|---|
| **Professor / avaliador:** quer ver o que foi entregue, os testes e as evidências | **[Parte 1: Entrega para avaliação](docs/professor/README.md)** |
| **Júnior ou pessoa de fora da área:** quer entender e montar o seu próprio | **[Parte 2: Aprenda a montar](docs/aprender/README.md)** |

## Em 30 segundos

Pergunta de um paciente: *"Vocês aceitam o convênio DentalPlus?"* O convênio não existe na FAQ.

- Um chatbot comum (versão v1, sem FAQ) responde **"Sim, aceitamos"**: inventou.
- O atendente deste projeto (v2 em diante) responde que **não tem essa informação** e encaminha à recepção.

O projeto mede essa diferença com 21 casos de teste: a v1 acerta 12 e a v2 acerta os 21.

## O que tem em cada pasta

```
docs/professor/   Parte 1: guia do avaliador (rubrica, resultados, como verificar)
docs/aprender/    Parte 2: conceitos, passo a passo e segurança, em linguagem simples
evidencias/       saídas reais dos testes (C01 a C05 e resumo dos 21 casos)
testes/           casos de teste e resultados completos (JSON)
prompts/          as 4 versões do prompt (v1 a v4)
dados/            a FAQ fictícia da clínica
app.py            o chat (Streamlit)
llm.py            chamada ao Gemini e montagem do prompt
rag.py            busca na FAQ (ChromaDB + embeddings)
avaliar.py        roda os casos de teste com um modelo-juiz
avaliar_busca.py  mede se a busca encontra a seção certa
tabela.py         resume os resultados por categoria
```

Os arquivos de código ficam na raiz de propósito: os scripts procuram `prompts/`, `dados/` e `testes/` ao lado deles.
