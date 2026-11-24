"""app.py - a tela do chat (Streamlit).

Para abrir:  streamlit run app.py
"""
import streamlit as st

from chatbot import responder
from llm import modo_atual

st.set_page_config(page_title="Atendente virtual - Clínica Exemplo")
st.title("Atendente virtual")
st.caption(
    "Projeto acadêmico com dados fictícios. "
    "Não envie dados pessoais (CPF, e-mail, telefone)."
)

modo = modo_atual()
if modo == "simulado":
    st.warning(
        "Modo SIMULADO: as respostas são de teste e não vêm de um modelo de IA. "
        "Veja o README para ligar a API."
    )

versao = st.sidebar.selectbox("Versão do prompt", ["v1", "v2", "v3"], index=2)
st.sidebar.write(f"Modo: {modo}")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.write(msg["texto"])

pergunta = st.chat_input("Digite sua pergunta")
if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    try:
        r = responder(pergunta, versao=versao)
        texto = r["resposta"]
        if r["fonte"]:
            texto += f"\n\n_Fonte: {r['fonte']}_"
        if r["bloqueado"]:
            texto += f"\n\n_(bloqueado pela proteção: {r['motivo']})_"
    except RuntimeError as erro:
        texto = f"Erro de configuração: {erro}"

    st.session_state.mensagens.append({"papel": "assistant", "texto": texto})
    with st.chat_message("assistant"):
        st.write(texto)
