# 5. Problemas comuns e como resolver

[← Trilha](README.md) · [← Segurança](04-seguranca.md) · [Passo a passo](03-passo-a-passo.md) · [Próximo: O código por dentro →](06-o-codigo-por-dentro.md)

## Ao instalar e rodar

**`python` ou `git` "não é reconhecido como comando"**
: A ferramenta não está instalada, ou o terminal foi aberto antes da instalação. Instale (Passo 1) e **feche e abra o terminal**. No Windows, marque "Add Python to PATH" ao instalar o Python. No Mac/Linux, tente `python3`.

**No Windows, o `Activate.ps1` dá erro dizendo que "a execução de scripts foi desabilitada"**
: O PowerShell bloqueia scripts por padrão. Rode `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (vale só para aquele terminal) e ative o ambiente de novo.

**`ModuleNotFoundError: No module named 'streamlit'` (ou chromadb, dotenv, google)**
: O ambiente virtual não está ativo, ou as dependências não foram instaladas. Confira se aparece `(.venv)` no terminal. Se não, ative (Passo 3); depois rode `pip install -r requirements.txt`.

**`KeyError: 'GEMINI_API_KEY'` ou `KeyError: 'GEMINI_MODEL'`**
: O código não achou o `.env`. Confirme que o arquivo se chama exatamente `.env` (não `.env.example` nem `.env.txt`), que está **na pasta do projeto** (ao lado de `app.py`) e que tem as duas linhas preenchidas (Passo 5). No Windows, o Bloco de Notas pode salvar como `.env.txt`: use "Salvar como" → "Todos os arquivos".

**`streamlit` não abre no navegador**
: Abra manualmente http://localhost:8501. Se a porta estiver ocupada, o terminal mostra o endereço novo.

## Ao conversar ou avaliar

**Erro 503 / "UNAVAILABLE" / "Desculpe, o serviço está instável"**
: O servidor do Gemini estava sobrecarregado naquele instante. Não é erro seu. O código já tenta de novo; se persistir, espere alguns minutos e tente outra vez.

**Erro 429 / "quota" / "RESOURCE_EXHAUSTED"**
: Você passou da cota gratuita de chamadas. Espere o limite renovar ou rode menos casos (por exemplo, `python avaliar.py v2` em vez de todas as versões).

**A busca do RAG devolve seções que não fazem sentido**
: Sempre vêm 3 trechos, relevantes ou não. Olhe as distâncias no expansor "Trechos da FAQ usados": distância grande significa pouca relação. Se você mudou a FAQ, apague a pasta `chroma_db/` para reindexar.

**Meus resultados na avaliação são diferentes dos do projeto**
: É esperado. Os modelos variam entre execuções, e o próprio juiz é um modelo. Diferenças de 1 ou 2 casos são normais. O que importa é a **diferença grande** entre v1 e v2.

**O `testes/resultados.json` mudou depois que rodei a avaliação**
: Rodar `avaliar.py` sobrescreve os resultados das versões avaliadas. Para recuperar o original: `git restore testes/resultados.json`.

## Ao usar Git e GitHub

**"Cloned into" dentro de outra pasta de projeto**
: Você rodou `git clone` estando dentro de uma pasta de projeto e criou uma pasta dentro da outra. Saia com `cd ..` e clone no lugar certo. Se o objetivo era **publicar a sua pasta**, o comando é outro: `git init`, `git remote add origin URL` e `git push`, e não `clone`.

**`GH007: Your push would publish a private email address`**
: O GitHub bloqueia commits com o seu e-mail pessoal quando a opção de privacidade está ligada. Configure o e-mail "noreply" que aparece em *GitHub → Settings → Emails* (formato `NUMERO+usuario@users.noreply.github.com`):
```
git config user.email "NUMERO+usuario@users.noreply.github.com"
git commit --amend --reset-author --no-edit
```
Depois envie de novo com `git push`.

**`git push` rejeitado ("non-fast-forward" / "fetch first")**
: O GitHub tem commits que você não tem. Rode `git pull` antes e depois `git push`.

**Publiquei uma chave por engano**
: Revogue a chave imediatamente e crie outra (veja [Segurança](04-seguranca.md)). Apagar o arquivo depois não limpa o histórico do Git.
