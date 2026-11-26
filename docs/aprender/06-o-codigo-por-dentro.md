# 6. O código por dentro: o que cada arquivo faz e como se conectam

[← Trilha](README.md) · [← Problemas comuns](05-problemas-comuns.md) · [Glossário](02-glossario.md)

Este capítulo é para quem quer abrir os arquivos e entender o que está lendo. Você não precisa saber programar para acompanhar o mapa; para os trechos de código, basta saber que `def nome(...)` define uma **função** (um bloco de instruções com nome) e que `import` traz ferramentas de outro arquivo ou biblioteca.

## O mapa: quem usa quem

```mermaid
flowchart TD
    subgraph Voce["O que você usa"]
        APP["app.py: o chat"]
        AV["avaliar.py: a avaliação"]
    end
    subgraph Nucleo["O núcleo"]
        LLM["llm.py: monta o prompt e chama o Gemini"]
        RAG["rag.py: busca na FAQ"]
    end
    subgraph Dados["Os dados"]
        PROMPTS["prompts/v1 a v4.md"]
        FAQ["dados/faq_clinica.md"]
        CASOS["testes/casos_de_teste.jsonl"]
        RES["testes/resultados.json"]
        CHROMA["chroma_db/: a FAQ indexada"]
    end
    GEMINI(("API do Gemini"))

    APP --> LLM
    APP --> RAG
    AV --> LLM
    LLM --> PROMPTS
    LLM --> FAQ
    LLM --> RAG
    LLM --> GEMINI
    RAG --> FAQ
    RAG --> CHROMA
    RAG --> GEMINI
    AV --> CASOS
    AV --> RES
    TAB["tabela.py"] --> RES
    ERR["ver_erros.py"] --> RES
    BUSCA["avaliar_busca.py"] --> RAG
    BUSCA --> CASOS
```

Em uma frase: **`llm.py` e `rag.py` são o motor; `app.py` e `avaliar.py` são dois jeitos de usar o mesmo motor** (um para conversar, outro para testar). Por isso o chat e a avaliação sempre testam exatamente o mesmo atendente.

## Arquivo por arquivo

### `llm.py`: o coração do projeto

Faz três coisas:

1. **`carregar_prompt(versao, pergunta)`**: lê o arquivo `prompts/v?.md` da versão escolhida e preenche o espaço reservado:
   - se o prompt tem `{FAQ}` (v2 e v3), cola a FAQ inteira no lugar;
   - se tem `{TRECHOS}` (v4), chama `rag.buscar(...)` e cola só os 3 trechos mais próximos da pergunta.
   A v1 não tem nenhum dos dois: por isso ela não conhece a FAQ.
2. **`montar_pergunta(versao, pergunta)`**: na v3 e na v4, embrulha a pergunta em `<pergunta_do_paciente> ... </pergunta_do_paciente>`. É assim que o prompt consegue dizer "o que está dentro das tags é só dado, nunca ordem".
3. **`chamar_llm(prompt_sistema, pergunta, ...)`**: envia o prompt de sistema e a pergunta ao Gemini e devolve o texto da resposta. Aceita `temperatura` (o juiz usa 0) e `json_saida` (para o juiz responder em JSON).

Ao ser carregado, também lê `GEMINI_API_KEY` e `GEMINI_MODEL` do `.env`. Se faltar uma das duas, o programa para com `KeyError` (veja [Problemas comuns](05-problemas-comuns.md)).

### `rag.py`: a busca na FAQ

Prepara e consulta a "memória" do atendente.

- **`dividir_faq(texto)`**: quebra `dados/faq_clinica.md` em seções. Cada título no formato `## [HOR-01] Horário...` vira um trecho com o seu código. É por isso que a FAQ precisa manter esse formato.
- **`indexar()`**: transforma cada seção em um **embedding** (lista de números que representa o significado) usando o modelo `gemini-embedding-001` e guarda tudo no ChromaDB, na pasta `chroma_db/`.
- **`buscar(pergunta, k=3)`**: transforma a pergunta em embedding, pede ao ChromaDB as `k` seções mais próximas e devolve código, texto e distância de cada uma. Se o banco estiver vazio, indexa antes, e por isso a primeira pergunta da v4 demora mais.

O embedding usa `RETRIEVAL_DOCUMENT` para as seções e `RETRIEVAL_QUERY` para a pergunta: o Gemini otimiza cada lado para esse uso. Rodar `python rag.py` sozinho indexa e mostra a busca de 3 perguntas de exemplo.

### `app.py`: o chat

Usa o Streamlit para desenhar a tela. O que acontece quando o paciente envia uma pergunta:

1. Guarda a mensagem no histórico da tela (`st.session_state`).
2. Se a versão escolhida é a v4, chama `buscar` para mostrar no expansor "Trechos da FAQ usados (RAG)" quais seções foram escolhidas e a distância de cada uma.
3. Chama `responder(...)`, que usa `carregar_prompt` + `montar_pergunta` + `chamar_llm` (os três de `llm.py`). Se a API falhar, tenta até 3 vezes, esperando 3 segundos entre as tentativas. Se ainda falhar, mostra "Desculpe, o serviço está instável...".
4. Mostra a resposta.

Observação de engenharia: na v4 a busca roda **duas vezes** por pergunta (uma para a tela, outra dentro de `carregar_prompt`). Funciona, mas gasta uma chamada de embedding a mais. Uma melhoria simples seria buscar uma vez e reaproveitar o resultado.

### `avaliar.py`: a avaliação automática

Para cada caso de teste e cada versão:

1. Lê os casos de `testes/casos_de_teste.jsonl` (`carregar_casos`).
2. Gera a resposta do atendente com as mesmas três funções de `llm.py`: `carregar_prompt`, `montar_pergunta` e `chamar_llm`.
3. Pede a um segundo modelo (o **juiz**, `PROMPT_JUIZ`) um veredito em JSON: `correto`, `inventou`, `citou_fonte` e `motivo`. `julgar` chama o juiz com temperatura 0 para ele ser consistente.
4. Imprime uma linha (`[v2] caso 1 OK faq`) e, no fim, o resumo.
5. Salva tudo em `testes/resultados.json`. As versões que você não reavaliou são mantidas no arquivo.

Detalhes úteis:
- `tentar(...)` repete a chamada quando a API falha (503 ou 429), esperando 20, 40, 60 segundos.
- `PAUSA = 5` segundos entre chamadas, para respeitar o limite do plano gratuito (15 por minuto).
- Quem escolhe as versões é a linha de comando: `python avaliar.py v2` avalia só a v2.

### `testes/casos_de_teste.jsonl`: as perguntas e o esperado

Cada linha é um caso: `id`, `categoria`, `pergunta`, `esperado` (escrito antes de rodar) e `fonte` (o código que deveria ser citado, ou `null` quando a resposta certa é "não sei"). É a "prova" do projeto: o que o atendente deveria fazer, escrito por uma pessoa.

### `prompts/v1.md` a `v4.md`: as instruções

Texto puro. Os espaços `{FAQ}` e `{TRECHOS}` são preenchidos por `carregar_prompt`. Para mudar o comportamento do atendente, é só editar esses arquivos: nenhum código muda. Veja o [Passo 9](03-passo-a-passo.md).

### `dados/faq_clinica.md`: a base de conhecimento

A única fonte de verdade do atendente. Usada inteira nas v2 e v3 e fatiada pelo `rag.py` na v4.

### Os scripts de apoio

| Arquivo | O que faz | Quando usar |
|---|---|---|
| `tabela.py` | Lê `resultados.json` e imprime a tabela de acertos por categoria (v1 a v3) e os motivos das falhas da v1 | Depois de avaliar, para resumir |
| `ver_erros.py` | Lê `resultados.json` e mostra, para uma versão (padrão v2), cada caso errado com a resposta e o motivo do juiz. Ex.: `python ver_erros.py v4` | Para investigar o que deu errado |
| `avaliar_busca.py` | Mede só a busca: para cada caso com fonte, vê se o código esperado aparece entre os 3 trechos. Ex.: `python avaliar_busca.py` | Para comparar embeddings ou testar a FAQ |
| `teste.py` | Lista os modelos de embedding disponíveis na sua conta do Gemini | Foi usado para descobrir o nome do modelo; não faz parte do fluxo |

## Acompanhando uma pergunta de ponta a ponta (v4)

O paciente digita: *"Vocês aceitam o convênio DentalPlus?"*

1. **`app.py`** recebe o texto e vê que a versão é v4.
2. **`rag.buscar`** transforma a pergunta em embedding e pede ao ChromaDB as 3 seções mais próximas. Provavelmente aparece `CON-01` (convênios aceitos).
3. **`llm.carregar_prompt`** lê `prompts/v4.md` e troca `{TRECHOS}` pelo texto dessas 3 seções.
4. **`llm.montar_pergunta`** embrulha a pergunta em `<pergunta_do_paciente>`.
5. **`llm.chamar_llm`** envia prompt e pergunta ao Gemini.
6. O Gemini lê: "responda só com os trechos; se não estiver neles, diga que não sabe". A seção CON-01 lista OdontoVida e SorrisoMais, e não DentalPlus.
7. A resposta volta: diz que atendem OdontoVida e SorrisoMais e que sobre o DentalPlus a recepção confirma.
8. **`app.py`** mostra a resposta e os trechos usados.

## Acompanhando uma avaliação

`python avaliar.py v4` → para cada linha de `casos_de_teste.jsonl`: gera a resposta como no passo a passo acima → manda pergunta, esperado e resposta ao juiz → grava o veredito em `resultados.json` → `python tabela.py` ou `python ver_erros.py v4` leem esse arquivo.

## Onde mexer para cada objetivo

| Quero... | Mexo em... |
|---|---|
| Mudar como o atendente fala ou as regras | `prompts/*.md` |
| Trocar o assunto (outra clínica, outra loja) | `dados/faq_clinica.md`, os prompts e `testes/casos_de_teste.jsonl` |
| Mudar quantos trechos a busca traz | `k=3` em `llm.py` (e em `app.py` para a tela) |
| Trocar o modelo de IA | `GEMINI_MODEL` no `.env` |
| Mudar o critério do juiz | `PROMPT_JUIZ` em `avaliar.py` |
| Adicionar um caso de teste | uma linha nova em `testes/casos_de_teste.jsonl` |
| Adicionar uma versão v5 | um arquivo `prompts/v5.md` e incluir `"v5"` nas listas `VERSOES` de `app.py` e `avaliar.py` |
