# 06. Como publicar este projeto no GitHub com segurança

Passo a passo para quem **ainda não subiu** o projeto. Faça na pasta do projeto.

## Antes de tudo
O arquivo `.env` existir na sua máquina **não é problema**: o `.gitignore` impede o envio. O que **não pode** acontecer é uma chave aparecer em um arquivo que vai para o GitHub. A checagem para isso está no Passo 2.

## Passo 1: criar o repositório vazio no GitHub
1. Entre em github.com e clique em **New repository**.
2. Nome sugerido: `Atendente-Clinica-com-IA-RAG`.
3. **Não** marque "Add a README", ".gitignore" nem "license" (o projeto já tem os seus).
4. Escolha **Private** enquanto estiver revisando. Depois você pode tornar público.
5. Clique em **Create repository**.

## Passo 2: preparar o Git na sua pasta
```bash
git init
git add .
git status
```
Confira a lista do `git status`: **não pode** aparecer `.env`, `.venv/` nem arquivos em `resultados/*.json`. Se aparecer, **pare** e revise o `.gitignore`.

Agora procure por chaves esquecidas **dentro dos arquivos que vão subir**:
```bash
git grep --cached -n -i "api_key"
git grep --cached -n -i "sk-"
```
No primeiro comando devem aparecer **só nomes de variável** (como `LLM_API_KEY=` vazio no `.env.example`, e o código do `llm.py` e o README que citam esse nome). No segundo, nada de valor parecido com uma chave. **Se enxergar uma chave de verdade, pare** e remova antes de continuar.

```bash
git diff --cached --stat
git commit -m "Primeira versão: chatbot de clínica com RAG, guardrails e avaliação"
git branch -M main
```

## Passo 3: ligar ao GitHub e enviar
Se você estiver publicando uma cópia sua do projeto, troque `MazkciR` pelo seu usuário e o nome do repositório pelo seu:
```bash
git remote add origin https://github.com/MazkciR/Atendente-Clinica-com-IA-RAG.git
git push -u origin main
```
O Git vai pedir login. Use o **navegador/gerenciador de credenciais** (ou `gh auth login`, se tiver o GitHub CLI).

**Nunca cole um token dentro da URL do `remote`** nem em arquivo do projeto.

## Passo 4: conferir no site
Abra o repositório no GitHub e confirme que **não há** `.env` na lista de arquivos e que o README aparece formatado, com o desenho.

## Licença
Antes de tornar público, escolha uma licença (por exemplo, MIT) em **Add file → Create new file → `LICENSE`**. Sem licença, ninguém tem permissão formal de reutilizar o código.

## Se você enviou um segredo sem querer
1. **Revogue a chave agora**, no site do provedor, e crie outra.
2. Só depois pense em limpar o histórico. Mesmo apagando o commit, a chave antiga deve ser considerada comprometida.
